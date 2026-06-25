# Remove "Co-authored-by: Cursor" from the latest commit message.
# Run in Windows Terminal or PowerShell OUTSIDE Cursor so attribution is not re-injected.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$git = "C:\Program Files\Git\cmd\git.exe"
if (-not (Test-Path $git)) {
  $git = "git"
}

$msg = @"
Add org questionnaire flow and reliable Windows dev startup.

Introduces applicability checks, policy generation, session storage, and dashboard UX improvements. Adds dev:all scripts with port cleanup, webpack dev mode, and a Next.js /api proxy so the frontend stays connected when backend ports change.
"@

$msgFile = Join-Path $env:TEMP "clickcomply-amend-msg.txt"
[System.IO.File]::WriteAllText($msgFile, $msg)

$env:GIT_AUTHOR_NAME = "AadityaJain"
$env:GIT_AUTHOR_EMAIL = "122963080+Git-AadityaJain@users.noreply.github.com"
$env:GIT_COMMITTER_NAME = $env:GIT_AUTHOR_NAME
$env:GIT_COMMITTER_EMAIL = $env:GIT_AUTHOR_EMAIL

& $git commit --amend -F $msgFile
Remove-Item $msgFile -Force

Write-Host ""
& $git log -1 --format=full
Write-Host ""
Write-Host "If this commit was already pushed, update remote with:"
Write-Host "  git push --force-with-lease origin main"
