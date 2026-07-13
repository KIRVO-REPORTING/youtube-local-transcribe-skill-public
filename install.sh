#!/usr/bin/env sh
set -eu

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$REPO_DIR"

MIN_VERSION="3.10"

python_is_supported() {
  "$1" - "$MIN_VERSION" <<'PY' >/dev/null 2>&1
import sys
minimum = tuple(map(int, sys.argv[1].split(".")))
raise SystemExit(0 if sys.version_info[:2] >= minimum else 1)
PY
}

find_python() {
  for candidate in "${PYTHON_BIN:-}" python3.14 python3.13 python3.12 python3.11 python3.10 python3 python; do
    if [ -n "$candidate" ] && command -v "$candidate" >/dev/null 2>&1 && python_is_supported "$candidate"; then
      command -v "$candidate"
      return 0
    fi
  done
  if command -v uv >/dev/null 2>&1; then
    echo "No supported system Python found; provisioning Python 3.12 with uv..." >&2
    uv python install 3.12 >&2
    candidate=$(uv python find 3.12)
    if [ -n "$candidate" ] && python_is_supported "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  fi
  return 1
}

print_python_help() {
  cat <<'EOF'
Python 3.10+ was not found.

Install Python first, then re-run ./install.sh.

Common options:
- macOS with Homebrew: brew install python
- Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-pip
- Fedora: sudo dnf install python3 python3-pip
- Arch: sudo pacman -S python python-pip
- Otherwise install Python 3.12 from https://www.python.org/downloads/
EOF
}

PYTHON=$(find_python || true)
if [ -z "$PYTHON" ]; then
  print_python_help
  exit 1
fi

if ! "$PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "pip was not available. Trying ensurepip..."
  if ! "$PYTHON" -m ensurepip --upgrade >/dev/null 2>&1; then
    cat <<'EOF'
pip is not available for this Python installation.

Install pip/venv support, then re-run ./install.sh.
On Ubuntu/Debian this is usually:
  sudo apt update && sudo apt install python3-venv python3-pip
EOF
    exit 1
  fi
fi

if [ -d ".venv" ] && { [ ! -x ".venv/bin/python" ] || ! python_is_supported ".venv/bin/python"; }; then
  echo "Recreating .venv with Python $MIN_VERSION+..."
  rm -rf .venv
fi

if [ ! -d ".venv" ]; then
  echo "Creating .venv..."
  if ! "$PYTHON" -m venv .venv; then
    cat <<'EOF'
Could not create a Python virtual environment.

Install venv support, then re-run ./install.sh.
On Ubuntu/Debian this is usually:
  sudo apt update && sudo apt install python3-venv
EOF
    exit 1
  fi
fi

VENV_PYTHON=".venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
  echo "Virtual environment Python was not found at $VENV_PYTHON"
  exit 1
fi

echo "Installing video-to-notes into .venv..."
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel
"$VENV_PYTHON" -m pip install -e .

CODEX_HOME_DIR=${CODEX_HOME:-"$HOME/.codex"}
if [ "${VIDEO_TO_NOTES_INSTALL_CODEX_SKILL:-auto}" != "0" ] && { [ -n "${CODEX_HOME:-}" ] || [ -d "$CODEX_HOME_DIR" ]; }; then
  SKILL_TARGET="$CODEX_HOME_DIR/skills/video-to-notes"
  "$VENV_PYTHON" - "$REPO_DIR/codex-skill" "$SKILL_TARGET" <<'PY'
from pathlib import Path
import shutil
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
if target.exists():
    shutil.rmtree(target)
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, target)
print(f"Installed Codex skill: {target}")
PY
fi

echo "Validating Python, yt-dlp EJS, JavaScript runtime, and ffmpeg..."
"$VENV_PYTHON" -m ytlt doctor --base-only

cat <<EOF

Installed.

Use this environment in the current shell:
  . .venv/bin/activate

Then configure language, Whisper fallback model, and output target:
  video-to-notes configure

Or run it directly:
  .venv/bin/video-to-notes configure

YouTube requires Deno 2.3+ or Node.js 22+. The installer validates this before reporting success.
EOF

if [ "${VIDEO_TO_NOTES_SKIP_CONFIGURE:-${YTLT_SKIP_CONFIGURE:-0}}" != "1" ]; then
  if [ -t 0 ] && [ -t 1 ]; then
    printf '\nRun video-to-notes configure now? [Y/n] '
    IFS= read -r answer
    case "$answer" in
      n|N|no|NO|No) exit 0 ;;
      *) .venv/bin/video-to-notes configure ;;
    esac
  fi
fi
