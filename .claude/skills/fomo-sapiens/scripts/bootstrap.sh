#!/usr/bin/env bash
# Fomo Sapiens bootstrap — macOS / Linux.
#   bash scripts/bootstrap.sh              # full: Python (if missing) + deps + Playwright/Chromium
#   bash scripts/bootstrap.sh --no-browser # skip Playwright + Chromium (manual token paste only)
#
# Guarantees afterwards: ~/.config/fomo-sapiens/venv exists with every dependency, and
# `python3 scripts/fomo.py ...` works (scripts/_deps.py re-execs into that venv on its own).
# Idempotent — safe to re-run.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${HOME}/.config/fomo-sapiens"
VENV="${CONF}/venv"
MIN_MINOR=9
WANT_BROWSER=1
[[ "${1:-}" == "--no-browser" ]] && WANT_BROWSER=0

log()  { printf '\033[1;34m[fomo-bootstrap]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[fomo-bootstrap] %s\033[0m\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

# ---------- 1. find a usable Python (>= 3.9, with venv + pip) ----------
py_ok() {  # $1 = interpreter path; prints it on success
  local p="$1"
  [[ -x "$p" ]] || have "$p" || return 1
  "$p" - <<'PY' >/dev/null 2>&1 || return 1
import sys, importlib.util
sys.exit(0 if sys.version_info >= (3, 9) and importlib.util.find_spec("venv") else 1)
PY
  echo "$p"
}

find_python() {
  local c
  for c in python3.13 python3.12 python3.11 python3.10 python3.9 python3 python \
           "${CONF}/uv-python" "$HOME/.local/bin/python3"; do
    if py_ok "$c" 2>/dev/null; then return 0; fi
  done
  # uv-managed interpreters (from a previous run's uv fallback)
  if have uv || [[ -x "$HOME/.local/bin/uv" ]]; then
    local uv_bin; uv_bin="$(command -v uv || echo "$HOME/.local/bin/uv")"
    local p; p="$("$uv_bin" python find 3.12 2>/dev/null || true)"
    [[ -n "$p" ]] && py_ok "$p" && return 0
  fi
  return 1
}

# On macOS a bare `python3` may be Xcode's stub that pops a CLT install dialog; py_ok handles
# that (the stub fails the version probe), so we never treat the stub as usable.

sudo_ok() { have sudo && sudo -n true >/dev/null 2>&1; }

install_python() {
  local os; os="$(uname -s)"
  log "No Python >= 3.${MIN_MINOR} found — installing one."
  case "$os" in
    Darwin)
      if have brew; then
        log "Using Homebrew: brew install python@3.12"
        brew install python@3.12 >&2 || true
        # brew's python is keg-only sometimes; add its bin to PATH for this run
        export PATH="$(brew --prefix python@3.12 2>/dev/null)/bin:$(brew --prefix 2>/dev/null)/bin:$PATH"
        find_python && return 0
      fi
      ;;
    Linux)
      if have apt-get && sudo_ok; then
        log "Using apt: python3 python3-venv python3-pip"
        sudo apt-get update -qq >&2 && sudo apt-get install -y -qq python3 python3-venv python3-pip >&2 || true
        find_python && return 0
      elif have dnf && sudo_ok; then
        log "Using dnf: python3 python3-pip"
        sudo dnf install -y -q python3 python3-pip >&2 || true
        find_python && return 0
      elif have apk && sudo_ok; then
        sudo apk add --no-cache python3 py3-pip >&2 || true
        find_python && return 0
      elif have pacman && sudo_ok; then
        sudo pacman -Sy --noconfirm python >&2 || true
        find_python && return 0
      fi
      ;;
  esac
  # Universal, no-sudo fallback: uv downloads a self-contained CPython into ~/.local.
  log "Falling back to uv (standalone Python, no admin rights needed)."
  if ! have uv && [[ ! -x "$HOME/.local/bin/uv" ]]; then
    have curl || have wget || die "Need curl or wget to download uv. Install Python 3.9+ manually and re-run."
    if have curl; then curl -LsSf https://astral.sh/uv/install.sh | sh >&2
    else wget -qO- https://astral.sh/uv/install.sh | sh >&2; fi
  fi
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  have uv || die "uv install failed. Install Python 3.9+ manually and re-run."
  uv python install 3.12 >&2
  find_python && return 0
  die "Installed uv but could not locate its Python. Try: uv python find 3.12"
}

PY="$(find_python || true)"
if [[ -z "$PY" ]]; then
  PY="$(install_python)"
fi
log "Using Python: $PY ($("$PY" -c 'import sys;print(".".join(map(str,sys.version_info[:3])))'))"

# ---------- 2. private venv (avoids PEP 668 'externally-managed' pip errors) ----------
mkdir -p "$CONF"; chmod 700 "$CONF"
if [[ ! -x "$VENV/bin/python" ]] || ! "$VENV/bin/python" -c 'import sys;sys.exit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null; then
  log "Creating venv at $VENV"
  rm -rf "$VENV"
  "$PY" -m venv "$VENV" >&2 || {
    # Some distros ship python without ensurepip; let uv build the venv instead.
    have uv || die "python -m venv failed (missing python3-venv?). Install it or uv, then re-run."
    uv venv --python "$PY" "$VENV" >&2
  }
fi
VPY="$VENV/bin/python"
"$VPY" -m ensurepip --upgrade >/dev/null 2>&1 || true
"$VPY" -m pip install -q --upgrade pip >&2 2>/dev/null || true

# ---------- 3. deps ----------
log "Installing requirements"
"$VPY" -m pip install -q -r "$HERE/requirements.txt" >&2

if [[ "$WANT_BROWSER" == 1 ]]; then
  log "Installing Playwright + Chromium (automated login / key export; ~150 MB, once)"
  "$VPY" -m pip install -q playwright >&2
  "$VPY" -m playwright install chromium >&2 || log "WARNING: Chromium download failed — login.py will fall back to manual token paste."
fi

# ---------- 4. verify ----------
"$VPY" - <<'PY' >&2
import curl_cffi, solders, eth_account, eth_abi, rlp
print("[fomo-bootstrap] deps OK:", "curl_cffi", curl_cffi.__version__)
PY

log "Done. Use the scripts as documented — e.g.  python3 scripts/fomo.py whoami"
log "(any python3 works: scripts re-exec into $VENV automatically; or call $VPY directly)"
echo "$VPY"
