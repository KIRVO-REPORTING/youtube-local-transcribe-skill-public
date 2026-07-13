$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoDir

$MinimumVersion = [Version]"3.10"

function Get-PythonCommand {
    if ($env:PYTHON_BIN) {
        $cmd = Get-Command $env:PYTHON_BIN -ErrorAction SilentlyContinue
        if ($cmd) {
            return @{ File = $cmd.Source; Args = @() }
        }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{ File = $py.Source; Args = @("-3") }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{ File = $python.Source; Args = @() }
    }

    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) {
        return @{ File = $python3.Source; Args = @() }
    }

    return $null
}

function Invoke-BasePython {
    param([string[]]$Arguments)
    & $script:PythonCommand.File @($script:PythonCommand.Args) @Arguments
}

function Show-PythonHelp {
    Write-Host @"
Python 3.10+ was not found.

Install Python first, then re-run:
  powershell -ExecutionPolicy Bypass -File .\install.ps1

Common options:
- Install Python 3.10+ from https://www.python.org/downloads/windows/
- Or use winget: winget install Python.Python.3.12
- During installation, enable "Add python.exe to PATH" if offered.
"@
}

$script:PythonCommand = Get-PythonCommand
if (-not $script:PythonCommand) {
    Show-PythonHelp
    exit 1
}

$VersionText = Invoke-BasePython @("-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))")
$Version = [Version]$VersionText.Trim()
if ($Version -lt $MinimumVersion) {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if ($uv) {
        Write-Host "Found Python $Version; provisioning Python 3.12 with uv..."
        & $uv.Source python install 3.12
        $UvPython = (& $uv.Source python find 3.12).Trim()
        $script:PythonCommand = @{ File = $UvPython; Args = @() }
        $VersionText = Invoke-BasePython @("-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))")
        $Version = [Version]$VersionText.Trim()
    }
    if ($Version -lt $MinimumVersion) {
        Write-Host "Found Python $Version, but Python $MinimumVersion+ is required."
        Show-PythonHelp
        exit 1
    }
}

try {
    Invoke-BasePython @("-m", "pip", "--version") | Out-Null
} catch {
    Write-Host "pip was not available. Trying ensurepip..."
    try {
        Invoke-BasePython @("-m", "ensurepip", "--upgrade") | Out-Null
    } catch {
        Write-Host "pip is not available for this Python installation. Reinstall Python with pip enabled, then re-run install.ps1."
        exit 1
    }
}

if (Test-Path ".venv") {
    $ExistingVenvPython = Join-Path $RepoDir ".venv\Scripts\python.exe"
    $RecreateVenv = -not (Test-Path $ExistingVenvPython)
    if (-not $RecreateVenv) {
        $ExistingVersionText = (& $ExistingVenvPython -c "import sys; print('.'.join(map(str, sys.version_info[:3])))").Trim()
        $RecreateVenv = ([Version]$ExistingVersionText -lt $MinimumVersion)
    }
    if ($RecreateVenv) {
        Write-Host "Recreating .venv with Python $MinimumVersion+..."
        Remove-Item ".venv" -Recurse -Force
    }
}

if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv..."
    try {
        Invoke-BasePython @("-m", "venv", ".venv")
    } catch {
        Write-Host "Could not create a virtual environment. Reinstall Python with venv support, then re-run install.ps1."
        exit 1
    }
}

$VenvPython = Join-Path $RepoDir ".venv\Scripts\python.exe"
$VenvCommand = Join-Path $RepoDir ".venv\Scripts\video-to-notes.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment Python was not found at $VenvPython"
    exit 1
}

Write-Host "Installing video-to-notes into .venv..."
& $VenvPython -m pip install --upgrade pip setuptools wheel
& $VenvPython -m pip install -e .

$CodexHomeDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
if ($env:VIDEO_TO_NOTES_INSTALL_CODEX_SKILL -ne "0" -and ($env:CODEX_HOME -or (Test-Path $CodexHomeDir))) {
    $SkillTarget = Join-Path $CodexHomeDir "skills\video-to-notes"
    if (Test-Path $SkillTarget) {
        Remove-Item $SkillTarget -Recurse -Force
    }
    New-Item -ItemType Directory -Force (Split-Path -Parent $SkillTarget) | Out-Null
    Copy-Item (Join-Path $RepoDir "codex-skill") $SkillTarget -Recurse -Force
    Write-Host "Installed Codex skill: $SkillTarget"
}

Write-Host "Validating Python, yt-dlp EJS, JavaScript runtime, and ffmpeg..."
& $VenvPython -m ytlt doctor --base-only
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host @"

Installed.

Use this environment in the current PowerShell:
  .\.venv\Scripts\Activate.ps1

Then configure language, Whisper fallback model, and output target:
  video-to-notes configure

Or run it directly:
  .\.venv\Scripts\video-to-notes.exe configure

YouTube requires Deno 2.3+ or Node.js 22+. The installer validates this before reporting success.
"@

if ($env:VIDEO_TO_NOTES_SKIP_CONFIGURE -ne "1" -and $env:YTLT_SKIP_CONFIGURE -ne "1" -and [Environment]::UserInteractive) {
    $answer = Read-Host "Run video-to-notes configure now? [Y/n]"
    if ($answer -notin @("n", "N", "no", "NO", "No")) {
        & $VenvCommand configure
    }
}
