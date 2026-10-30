<#
.SYNOPSIS
  Start one builder session in its own worktree, at the tier planning set.

.DESCRIPTION
  The fixed steps of a dispatch, so no manager session types them by hand:

    1. read <main checkout>\.claude\dispatch.json (no file, no run)
    2. take the tier's model, effort and turn cap (no tier, no dispatch)
    3. read the prompt file (a double quote in it is refused)
    4. read the deny list from the builders' settings file
    5. make the worktree .claude\worktrees\<Name> on branch worktree-<Name>
    6. run the project's setup commands in it
    7. start the session in the background
    8. check it has a pid and runs in that worktree; stop it if not

  Dry run by default: steps 1 to 4 are done, every command of steps 5 to 8
  is printed, and nothing is changed. Pass -Apply to act.

  The permission mode is dontAsk. No parameter and no config key changes
  it, so a builder is never started in a mode that skips permission checks.

  dispatch.json is the project owner's file, like a settings file: its
  setup commands are run as written. See the README for its keys.

  -Apply acts only in a main checkout the owner has listed in
  <user profile>\.claude\dispatch-projects.json. A config file alone is not
  enough: a session could write one in a folder of its own.

.EXAMPLE
  .\dispatch.ps1 -Name fix-42 -Tier low -PromptFile C:\briefs\fix-42.txt
  .\dispatch.ps1 -Name fix-42 -Tier low -PromptFile C:\briefs\fix-42.txt -Apply
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Tier,
    [Parameter(Mandatory = $true)][string]$PromptFile,
    [int]$TurnCap,
    [string]$Project = (Get-Location).Path,
    [switch]$NoSetup,
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

# Tier defaults; a project's dispatch.json may override a tier under "tiers".
$tiers = @{
    low    = @{ model = 'claude-sonnet-5-5'; effort = 'medium'; turnCap = 30 }
    medium = @{ model = 'claude-sonnet-5-5'; effort = 'high'; turnCap = 80 }
    high   = @{ model = 'claude-opus-5-5'; effort = 'medium'; turnCap = 200 }
}
$mode = 'dontAsk'

function Refuse([string]$Why) {
    [Console]::Error.WriteLine("dispatch refused: $Why")
    exit 2
}

function Show([string[]]$Command) {
    # One printed line per command, each argument on show as it is passed.
    ($Command | ForEach-Object { if ($_ -match '[\s"]') { "'$_'" } else { $_ } }) -join ' '
}

if ($Name -notmatch '^[a-z0-9][a-z0-9-]{0,62}$') {
    Refuse "the name must be lower-case letters, digits and hyphens: $Name"
}

# 1. The main checkout and its config.
$common = (& git -C $Project rev-parse --path-format=absolute --git-common-dir 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $common) { Refuse "not a git checkout: $Project" }
$main = (Split-Path -Parent ($common -replace '/', '\')).TrimEnd('\')

$configPath = Join-Path $main '.claude\dispatch.json'
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    Refuse "no config file. The project owner creates $configPath from the plugin's templates\dispatch.json"
}
try {
    $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Refuse "the config file is not valid JSON: $configPath"
}

function Setting([string]$Key, $Default) {
    $found = $config.PSObject.Properties[$Key]
    if ($null -eq $found -or $null -eq $found.Value -or "$($found.Value)" -eq '') { return $Default }
    return $found.Value
}

$agent = Setting 'agent' $null
$settingsRel = Setting 'buildersSettings' $null
$claude = Setting 'claude' 'claude'
$readLine = [string](Setting 'readLine' '')
$setup = @(Setting 'setup' @())
if (-not $agent) { Refuse 'the config file names no agent' }
if (-not $settingsRel) { Refuse 'the config file names no buildersSettings file' }
if ($readLine.Contains('"')) { Refuse 'the readLine of the config file holds a double quote' }

# 2. The tier.
if (-not $Tier) { Refuse 'no tier, no dispatch. Planning sets the tier; pass it with -Tier' }
$Tier = $Tier.ToLowerInvariant()
if (-not $tiers.ContainsKey($Tier)) { Refuse "the tier must be low, medium or high: $Tier" }
$chosen = $tiers[$Tier].Clone()
$over = Setting 'tiers' $null
if ($over -and $over.PSObject.Properties[$Tier]) {
    foreach ($key in 'model', 'effort', 'turnCap') {
        $value = $over.$Tier.PSObject.Properties[$key]
        if ($value -and $value.Value) { $chosen[$key] = $value.Value }
    }
}
if ($TurnCap -gt 0) { $chosen.turnCap = $TurnCap }

# 3. The prompt.
if (-not (Test-Path -LiteralPath $PromptFile -PathType Leaf)) { Refuse "no prompt file: $PromptFile" }
$brief = (Get-Content -LiteralPath $PromptFile -Raw -Encoding UTF8).Trim()
if (-not $brief) { Refuse "the prompt file is empty: $PromptFile" }
if ($brief.Contains('"')) {
    Refuse 'the prompt file holds a double quote. PowerShell cuts the prompt off at the first one; reword it'
}
$prompt = (@($readLine, $brief, "Or stop after $($chosen.turnCap) turns.") | Where-Object { $_ }) -join "`n`n"

# 4. The deny list, from the one place it is kept.
$settingsPath = Join-Path $main $settingsRel
if (-not (Test-Path -LiteralPath $settingsPath -PathType Leaf)) {
    Refuse "no builders' settings file: $settingsPath"
}
try {
    $deny = @((Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json).permissions.deny)
} catch {
    Refuse "the builders' settings file is not valid JSON: $settingsPath"
}
$deny = @($deny | Where-Object { $_ })
if ($deny.Count -eq 0) { Refuse "the builders' settings file has no deny rule: $settingsPath" }

# No value may pass for a flag of the CLI: a leading hyphen is refused.
$values = @{ agent = $agent; model = $chosen.model; effort = $chosen.effort; prompt = $prompt }
foreach ($key in $values.Keys) {
    if ("$($values[$key])".TrimStart().StartsWith('-')) { Refuse "the $key starts with a hyphen" }
}
foreach ($rule in $deny) {
    if ("$rule".TrimStart().StartsWith('-')) { Refuse "a deny rule starts with a hyphen: $rule" }
}

$worktree = Join-Path $main ".claude\worktrees\$Name"
$branch = "worktree-$Name"
$hasWorktree = Test-Path -LiteralPath $worktree -PathType Container

$addWorktree = @('git', '-C', $main, 'worktree', 'add', ".claude/worktrees/$Name", '-b', $branch)
$start = @(
    $claude, '--bg', '-w', $Name, '--name', $Name,
    '--model', $chosen.model, '--effort', $chosen.effort,
    '--permission-mode', $mode, '--settings', $settingsPath,
    '--plugin-dir', (Split-Path -Parent $PSScriptRoot),
    '--agent', $agent, $prompt, '--disallowedTools'
) + $deny
$check = @($claude, 'agents', '--json')

Write-Output "name:      $Name"
Write-Output "tier:      $Tier ($($chosen.model), effort $($chosen.effort), turn cap $($chosen.turnCap))"
Write-Output "main:      $main"
Write-Output "worktree:  $worktree$(if ($hasWorktree) { ' (already there)' })"
Write-Output "settings:  $settingsPath ($($deny.Count) deny rules)"
Write-Output "mode:      $mode"

# The owner's list of main checkouts where -Apply may act. The profile
# folder comes from the system, not from an environment variable a
# session could set.
$listPath = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.claude\dispatch-projects.json'
$listed = @()
if (Test-Path -LiteralPath $listPath -PathType Leaf) {
    try {
        $listed = @((Get-Content -LiteralPath $listPath -Raw -Encoding UTF8 | ConvertFrom-Json).projects)
    } catch {
        Refuse "the owner's list of projects is not valid JSON: $listPath"
    }
}
$isListed = @($listed | Where-Object { $_ -and ("$_" -replace '/', '\').TrimEnd('\') -ieq $main }).Count -gt 0
Write-Output "apply:     $(if ($isListed) { 'this project is on the list' } else { 'would be refused, this project is not on the list' }) ($listPath)"

if (-not $Apply) {
    Write-Output ''
    Write-Output 'DRY RUN. Nothing was changed. These would run, in this order:'
    if (-not $hasWorktree) { Write-Output "  $(Show $addWorktree)" }
    if ($NoSetup) {
        Write-Output '  (no setup: -NoSetup)'
    } else {
        foreach ($command in $setup) { Write-Output "  [in the worktree] $command" }
    }
    Write-Output "  [in $main] $(Show $start)"
    Write-Output "  $(Show $check)"
    Write-Output ''
    Write-Output 'Pass -Apply to act.'
    exit 0
}

if (-not $isListed) {
    Refuse "this project is not on the owner's list. The owner adds $main to $listPath"
}

# 5. The worktree.
if (-not $hasWorktree) {
    & git -C $main worktree add ".claude/worktrees/$Name" -b $branch
    if ($LASTEXITCODE -ne 0) { Refuse "git could not make the worktree $worktree" }
}

# 6. Setup.
if (-not $NoSetup) {
    Push-Location -LiteralPath $worktree
    try {
        foreach ($command in $setup) {
            Write-Output "setup: $command"
            & powershell.exe -NoProfile -NonInteractive -Command $command
            if ($LASTEXITCODE -ne 0) { Refuse "a setup command failed (exit $LASTEXITCODE): $command" }
        }
    } finally {
        Pop-Location
    }
}

# 7. Start, from the main checkout.
Push-Location -LiteralPath $main
try {
    $rest = $start[1..($start.Count - 1)]
    & $claude @rest
    if ($LASTEXITCODE -ne 0) { Refuse "the session did not start (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
}

# 8. Check the pid and the folder.
Start-Sleep -Seconds 3
$listed = (& $claude agents --json) -join "`n" | ConvertFrom-Json
$session = @($listed | Where-Object { $_.name -eq $Name }) | Select-Object -Last 1
$isHome = $session -and $session.pid -and
    ([string]$session.cwd).TrimEnd('\') -ieq $worktree.TrimEnd('\')
if (-not $isHome) {
    if ($session -and $session.sessionId) { & $claude stop $session.sessionId }
    $where = if ($session) { [string]$session.cwd } else { 'not listed' }
    Refuse "the session is not running in its worktree (it is: $where). It was stopped; look before a second try"
}

Write-Output ''
Write-Output "started:   $Name, pid $($session.pid), session $($session.sessionId)"
Write-Output "watch:     $(Show $check)"
