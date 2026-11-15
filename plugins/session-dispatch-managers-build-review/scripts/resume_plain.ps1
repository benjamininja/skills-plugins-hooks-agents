<#
.SYNOPSIS
  Resume a stopped builder session with a follow-up message, with no other
  flags.

.DESCRIPTION
  The follow-up step of a dispatch, as one fixed command, so no manager
  session types it by hand:

    1. refuse a worktree that does not exist
    2. refuse a session id that is not a session id (hex digits in the
       8-4-4-4-12 shape of the "started:" line) or that starts with a hyphen
    3. read the message file (UTF-8, trimmed); refuse a message that holds
       a double quote or whose text starts with a hyphen
    4. find the CLI as dispatch.ps1 does: the "claude" key of the main
       checkout's .claude\dispatch.json, else claude on PATH. The main
       checkout is found from the worktree.
    5. run  claude --resume <SessionId> --bg <message>  with the worktree
       as the working directory, and no other flag
    6. wait up to 60 s for the claude process to exit, then print
       "exit: <code>" and exit with that code; if it is still running,
       print its pid and exit 3 (the process is left running)

  No other flag is ever passed: a resume with a flag starts a copy of the
  builder without the builder settings. Use it only for a builder that
  has stopped, never one that is still running.

.PARAMETER Worktree
  The builder's worktree folder. It becomes the working directory.

.PARAMETER SessionId
  The builder's full session id, from the "started:" line of dispatch.ps1.

.PARAMETER MessageFile
  A text file holding the message. It must hold no double quote and must
  not start with a hyphen.

.EXAMPLE
  .\resume_plain.ps1 -Worktree C:\repo\.claude\worktrees\fix-42 -SessionId <id> -MessageFile C:\notes\msg.txt
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Worktree,
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$MessageFile
)

$ErrorActionPreference = 'Stop'

function Refuse([string]$Why) {
    [Console]::Error.WriteLine("resume refused: $Why")
    exit 2
}

if (-not (Test-Path -LiteralPath $Worktree)) { Refuse "no worktree $Worktree" }
if ($SessionId.Contains('"')) { Refuse 'the session id holds a double quote' }
if ($SessionId.TrimStart().StartsWith('-')) { Refuse 'the session id starts with a hyphen' }
if ($SessionId -cnotmatch '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$') {
    Refuse "the session id is not a session id (hex digits, 8-4-4-4-12): $SessionId"
}
if (-not (Test-Path -LiteralPath $MessageFile -PathType Leaf)) { Refuse "no message file: $MessageFile" }
$msg = (Get-Content -LiteralPath $MessageFile -Raw -Encoding UTF8)
$msg = if ($msg) { $msg.Trim() } else { '' }
if (-not $msg) { Refuse "the message file is empty: $MessageFile" }
if ($msg.Contains('"')) { Refuse 'the message holds a double quote' }
if ($msg.StartsWith('-')) { Refuse 'the message starts with a hyphen' }

$Claude = 'claude'
$common = (& git -C $Worktree rev-parse --path-format=absolute --git-common-dir 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $common) { Refuse "not a git checkout: $Worktree" }
$main = (Split-Path -Parent ($common -replace '/', '\')).TrimEnd('\')
$configPath = Join-Path $main '.claude\dispatch.json'
if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    try {
        $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Refuse "the config file is not valid JSON: $configPath"
    }
    $found = $config.PSObject.Properties['claude']
    if ($found -and $null -ne $found.Value -and "$($found.Value)" -ne '') { $Claude = "$($found.Value)" }
}
if ($Claude.TrimStart().StartsWith('-')) { Refuse 'the claude path of the config file starts with a hyphen' }
$cmd = Get-Command $Claude -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $cmd) { Refuse "claude not found: $Claude (the config's claude key, else PATH)" }

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $cmd.Source
$psi.Arguments = '"--resume" "' + $SessionId + '" "--bg" "' + $msg + '"'
$psi.WorkingDirectory = $Worktree
$psi.UseShellExecute = $false
$p = [System.Diagnostics.Process]::Start($psi)
if (-not $p.WaitForExit(60000)) {
    Write-Output "still running after 60 s: pid $($p.Id)"
    exit 3
}
Write-Output "exit: $($p.ExitCode)"
exit $p.ExitCode
