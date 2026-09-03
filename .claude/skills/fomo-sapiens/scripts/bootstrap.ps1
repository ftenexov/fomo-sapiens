# Fomo Sapiens bootstrap — Windows (PowerShell 5.1+ / 7).
#   powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1              # full
#   powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1 -NoBrowser   # skip Playwright/Chromium
# Installs Python (winget, else uv standalone) if missing, builds a private venv at
# ~\.config\fomo-sapiens\venv, installs deps. Afterwards `python scripts\fomo.py ...` works
# (scripts\_deps.py re-execs into the venv automatically). Idempotent.
param([switch]$NoBrowser)
$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Conf = Join-Path $HOME ".config\fomo-sapiens"
$Venv = Join-Path $Conf "venv"
$VPy  = Join-Path $Venv "Scripts\python.exe"

function Log($m) { Write-Host "[fomo-bootstrap] $m" -ForegroundColor Cyan }
function Die($m) { Write-Host "[fomo-bootstrap] $m" -ForegroundColor Red; exit 1 }

function Test-Py($exe) {
  try {
    $out = & $exe -c "import sys,importlib.util;print(int(sys.version_info>=(3,9) and importlib.util.find_spec('venv') is not None))" 2>$null
    return ($out -eq "1")
  } catch { return $false }
}

function Find-Python {
  # Skip the Microsoft Store 'python.exe' alias stub (0-byte AppExecutionAlias) — Test-Py rejects it.
  foreach ($c in @("py -3.12","py -3.11","py -3.10","py -3.9","py -3","python3","python")) {
    $parts = $c.Split(" "); $exe = $parts[0]; $arg = $parts[1..($parts.Length-1)]
    if (Get-Command $exe -ErrorAction SilentlyContinue) {
      try {
        $ver = & $exe @arg -c "import sys,importlib.util;print(int(sys.version_info>=(3,9) and importlib.util.find_spec('venv') is not None))" 2>$null
        if ($ver -eq "1") { return (& $exe @arg -c "import sys;print(sys.executable)") }
      } catch {}
    }
  }
  $uv = Get-Command uv -ErrorAction SilentlyContinue
  if (-not $uv -and (Test-Path "$HOME\.local\bin\uv.exe")) { $uv = "$HOME\.local\bin\uv.exe" }
  if ($uv) { try { $p = & $uv python find 3.12 2>$null; if ($p -and (Test-Py $p)) { return $p } } catch {} }
  return $null
}

function Install-Python {
  Log "No Python >= 3.9 found - installing one."
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Log "Using winget: Python.Python.3.12"
    try { winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent | Out-Host } catch {}
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    $p = Find-Python; if ($p) { return $p }
  }
  Log "Falling back to uv (standalone Python, no admin rights)."
  if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = "$HOME\.local\bin;$env:Path"
  }
  if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { Die "uv install failed. Install Python 3.9+ from python.org and re-run." }
  uv python install 3.12 | Out-Host
  $p = Find-Python; if ($p) { return $p }
  Die "Installed uv but could not locate its Python. Try: uv python find 3.12"
}

$Py = Find-Python
if (-not $Py) { $Py = Install-Python }
Log "Using Python: $Py"

New-Item -ItemType Directory -Force -Path $Conf | Out-Null
if (-not (Test-Path $VPy) -or -not (Test-Py $VPy)) {
  Log "Creating venv at $Venv"
  if (Test-Path $Venv) { Remove-Item -Recurse -Force $Venv }
  & $Py -m venv $Venv
}
& $VPy -m pip install -q --upgrade pip 2>$null

Log "Installing requirements"
& $VPy -m pip install -q -r (Join-Path $Here "requirements.txt")

if (-not $NoBrowser) {
  Log "Installing Playwright + Chromium (automated login / key export; ~150 MB, once)"
  & $VPy -m pip install -q playwright
  try { & $VPy -m playwright install chromium } catch { Log "WARNING: Chromium download failed - login.py will fall back to manual token paste." }
}

& $VPy -c "import curl_cffi, solders, eth_account, eth_abi, rlp; print('[fomo-bootstrap] deps OK: curl_cffi', curl_cffi.__version__)"
Log "Done. Use the scripts as documented - e.g.  python scripts\fomo.py whoami"
Write-Output $VPy
