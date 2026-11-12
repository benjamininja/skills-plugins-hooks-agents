<#
.SYNOPSIS
  Resume a stopped builder session with a follow-up message, with no other
  flags.

.DESCRIPTION
  The follow-up step of a dispatch, as one fixed command, so no manager
  session types it by hand:

    1. refuse a worktree that does not exist
    2. read the message file (UTF-8, trimmed); refuse a message that holds
       a double quote
    3. run  claude --resume <SessionId> --bg <message>  with the worktree
       as the working directory, and no other flag
    4. wait up to 60 s for the claude process to exit, then print
       "exit: <code>"

  No other flag is ever passed: a resume with a flag starts a copy of the
  builder without the builder settings. Use it only for a builder that
  has stopped, never one that is still running.

  -Claude is optional. Without it the script finds claude on PATH.

.PARAMETER Worktree
  The builder's worktree folder. It becomes the working directory.

.PARAMETER SessionId
  The builder's full session id, from the "started:" line of dispatch.ps1.

.PARAMETER MessageFile
  A text file holding the message. It must hold no double quote.

.PARAMETER Claude
  Optional. The claude executable, as a name on PATH or a full path.

.EXAMPLE
  .\resume_plain.ps1 -Worktree C:\repo\.claude\worktrees\fix-42 -SessionId <id> -MessageFile C:\notes\msg.txt
  .\resume_plain.ps1 -Worktree C:\repo\.claude\worktrees\fix-42 -SessionId <id> -MessageFile C:\notes\msg.txt -Claude C:\tools\claude.exe
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Worktree,
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$MessageFile,
    [string]$Claude
)

if (-not $Claude) {
    $cmd = Get-Command claude -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $cmd) { throw 'claude not found on PATH; pass -Claude' }
    $Claude = $cmd.Source
}
if (-not (Test-Path -LiteralPath $Worktree)) { throw "no worktree $Worktree" }
$msg = (Get-Content -LiteralPath $MessageFile -Raw -Encoding UTF8).Trim()
if ($msg.Contains('"')) { throw 'message holds a double quote' }

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $Claude
$psi.Arguments = '"--resume" "' + $SessionId + '" "--bg" "' + $msg + '"'
$psi.WorkingDirectory = $Worktree
$psi.UseShellExecute = $false
$p = [System.Diagnostics.Process]::Start($psi)
$p.WaitForExit(60000) | Out-Null
Write-Output "exit: $($p.ExitCode)"
