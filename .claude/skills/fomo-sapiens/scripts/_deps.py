"""Dependency/interpreter fallback for the Fomo Sapiens scripts.

Every script does `import _deps` before importing curl_cffi & co. If the deps
are missing from the current interpreter, we transparently re-exec into the
private venv that scripts/bootstrap.sh (or .ps1) creates. If that venv doesn't
exist either, we exit with the one command that fixes it, instead of a traceback.

This keeps `python3 scripts/fomo.py ...` working no matter which python3 the
caller has, or even when only the bootstrap-managed Python exists.
"""
import os
import sys

VENV_DIR = os.path.join(os.path.expanduser("~/.config/fomo-sapiens"), "venv")
VENV_PY = (
    os.path.join(VENV_DIR, "Scripts", "python.exe")
    if os.name == "nt"
    else os.path.join(VENV_DIR, "bin", "python")
)
REQUIRED = ("curl_cffi", "solders", "eth_account", "eth_abi", "rlp")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_BOOTSTRAP = (
    f'powershell -ExecutionPolicy Bypass -File "{os.path.join(SCRIPTS_DIR, "bootstrap.ps1")}"'
    if os.name == "nt"
    else f'bash "{os.path.join(SCRIPTS_DIR, "bootstrap.sh")}"'
)


def _missing():
    import importlib.util
    return [m for m in REQUIRED if importlib.util.find_spec(m) is None]


def ensure():
    if sys.version_info < (3, 9):
        _fail(f"Python {sys.version.split()[0]} is too old (need 3.9+).")
    missing = _missing()
    if not missing:
        return
    in_venv = os.path.abspath(sys.executable) == os.path.abspath(VENV_PY)
    is_script = bool(sys.argv) and os.path.isfile(sys.argv[0])  # not `python -c` / REPL
    if is_script and not in_venv and os.path.exists(VENV_PY) and os.environ.get("FOMO_NO_REEXEC") != "1":
        # Re-run this exact command under the bootstrap venv's interpreter.
        env = dict(os.environ, FOMO_NO_REEXEC="1")
        argv = [VENV_PY] + sys.argv
        if os.name == "nt":
            # execv on Windows doesn't replace the process cleanly; spawn + exit instead.
            import subprocess
            sys.exit(subprocess.call(argv, env=env))
        os.execve(VENV_PY, argv, env)
    _fail(f"Missing Python packages: {', '.join(missing)}.")


def _fail(reason):
    sys.stderr.write(
        f"Fomo Sapiens: {reason}\n"
        f"Run the bootstrap once (installs Python if needed, then all deps into a private venv):\n"
        f"  {_BOOTSTRAP}\n"
        f"Then re-run this command unchanged.\n"
    )
    sys.exit(2)


ensure()
