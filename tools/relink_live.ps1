<#
.SYNOPSIS
  Point every ~/.claude skill, agent and hook link at one checkout of this repo.

.DESCRIPTION
  Links (directory junctions, see docs/adr/0003):
    ~/.claude/skills/<name>  ->  <Source>\skills\<name>     (one per skill)
    ~/.claude/agents         ->  <Source>\.claude\agents    (one junction)
    ~/.claude/hooks/<name>   ->  <Source>\hooks\<name>      (one per hook)

  <Source> should be the live clone: a checkout that only ever holds merged
  main and is never edited by hand (docs/adr/0011, Revision 2), so nothing
  unfinished goes live.

  Dry run by default: prints what it would do and changes nothing. Pass -Apply
  to act. Existing junctions are re-pointed. A real directory in the way is
  never deleted: it is reported and skipped unless -BackupDir is given, in
  which case it is moved there first. Junctions under ~/.claude that point
  into another checkout of this repo but have no counterpart in <Source>
  (a skill or hook removed from main) are reported, and removed with -Prune.

.EXAMPLE
  .\tools\relink_live.ps1 -Source C:\Users\benha\claude-live\skills-plugins-hooks-agents
  .\tools\relink_live.ps1 -Source C:\Users\benha\claude-live\skills-plugins-hooks-agents -Apply -Prune
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [string]$ClaudeHome = (Join-Path $env:USERPROFILE '.claude'),
    [string]$BackupDir,
    [switch]$Apply,
    [switch]$Prune
)

$ErrorActionPreference = 'Stop'
$Source = (Resolve-Path -LiteralPath $Source).Path.TrimEnd('\')

foreach ($required in 'skills', 'hooks', '.claude\agents') {
    if (-not (Test-Path -LiteralPath (Join-Path $Source $required) -PathType Container)) {
        throw "Not a checkout of this repo (missing $required): $Source"
    }
}

# name -> target, grouped by the ~/.claude folder the link lives in
$wanted = [ordered]@{}
Get-ChildItem -LiteralPath (Join-Path $Source 'skills') -Directory | ForEach-Object {
    $wanted[(Join-Path $ClaudeHome "skills\$($_.Name)")] = $_.FullName
}
Get-ChildItem -LiteralPath (Join-Path $Source 'hooks') -Directory | ForEach-Object {
    $wanted[(Join-Path $ClaudeHome "hooks\$($_.Name)")] = $_.FullName
}
$wanted[(Join-Path $ClaudeHome 'agents')] = (Join-Path $Source '.claude\agents')

function Get-LinkTarget([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    if ($item.LinkType) { return [string]($item.Target | Select-Object -First 1) }
    return '<real directory>'
}

function Remove-Link([string]$Path) {
    # Deletes the link itself. Never -Recurse: that would follow the junction
    # and delete the target's contents.
    [System.IO.Directory]::Delete($Path, $false)
}

$counts = @{ ok = 0; create = 0; repoint = 0; skipped = 0; pruned = 0 }
$mode = if ($Apply) { 'APPLY' } else { 'DRY RUN (pass -Apply to act)' }
Write-Output "relink_live: $mode"
Write-Output "  source: $Source"
Write-Output "  target: $ClaudeHome"

foreach ($link in $wanted.Keys) {
    $target = $wanted[$link]
    $current = Get-LinkTarget $link

    if ($current -eq $target) { $counts.ok++; continue }

    if ($null -eq $current) {
        Write-Output "  create   $link -> $target"
        $counts.create++
    }
    elseif ($current -eq '<real directory>') {
        if (-not $BackupDir) {
            Write-Output "  SKIP     $link is a real directory, not a link (pass -BackupDir to move it aside)"
            $counts.skipped++
            continue
        }
        Write-Output "  backup   $link -> $BackupDir, then link -> $target"
        $counts.repoint++
        if ($Apply) {
            New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
            Move-Item -LiteralPath $link -Destination (Join-Path $BackupDir (Split-Path $link -Leaf))
        }
    }
    else {
        Write-Output "  repoint  $link : $current -> $target"
        $counts.repoint++
        if ($Apply) { Remove-Link $link }
    }

    if ($Apply) {
        New-Item -ItemType Directory -Force -Path (Split-Path $link -Parent) | Out-Null
        New-Item -ItemType Junction -Path $link -Target $target | Out-Null
    }
}

# Links left behind by something removed from <Source>: junctions whose target
# is inside some checkout of this repo's skills\ or hooks\ but is not wanted.
foreach ($folder in 'skills', 'hooks') {
    $dir = Join-Path $ClaudeHome $folder
    if (-not (Test-Path -LiteralPath $dir)) { continue }
    Get-ChildItem -LiteralPath $dir -Force -Directory | Where-Object { $_.LinkType } | ForEach-Object {
        if ($wanted.Contains($_.FullName)) { return }
        $target = [string]($_.Target | Select-Object -First 1)
        if ($target -notmatch "\\skills-plugins-hooks-agents[^\\]*\\$folder\\") { return }
        if ($Prune) {
            Write-Output "  prune    $($_.FullName) (was -> $target)"
            $counts.pruned++
            if ($Apply) { Remove-Link $_.FullName }
        }
        else {
            Write-Output "  STALE    $($_.FullName) -> $target (not in source; pass -Prune to remove)"
            $counts.skipped++
        }
    }
}

Write-Output ("  summary: {0} already correct, {1} to create, {2} to repoint, {3} pruned, {4} skipped" -f `
        $counts.ok, $counts.create, $counts.repoint, $counts.pruned, $counts.skipped)
if (-not $Apply) { Write-Output '  nothing changed (dry run).' }
