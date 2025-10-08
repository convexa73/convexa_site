#!/usr/bin/env bash
set -e

echo "=== System Info ==="
echo "Date: $(date)"
echo "sw_vers:"
sw_vers || true
echo "Kernel:"
uname -a || true
echo "Architecture (uname -m): $(uname -m)"
echo

echo "=== Rosetta 2 (optional) ==="
if /usr/bin/pgrep oahd >/dev/null 2>&1; then
  echo "Rosetta: running"
else
  echo "Rosetta: not running (ok if you don't need x86_64 tools)"
fi
echo

echo "=== Xcode Command Line Tools ==="
if xcode-select -p >/dev/null 2>&1; then
  echo "CLT Path: $(xcode-select -p)"
else
  echo "CLT not installed. Install with: xcode-select --install"
fi
clang --version || true
echo

echo "=== Homebrew ==="
if command -v brew >/dev/null 2>&1; then
  echo "brew: $(brew -v | head -n1)"
  echo "brew prefix: $(brew --prefix)"
  echo "brew doctor (summary):"
  brew doctor || true
else
  echo "Homebrew not found. Install from https://brew.sh (Apple Silicon)."
fi
echo

echo "=== OpenSSL / libpq / imaging libs (via Homebrew) ==="
for pkg in openssl@3 libpq jpeg libtiff freetype webp pkg-config; do
  if brew list --versions "$pkg" >/dev/null 2>&1; then
    echo "✓ $pkg installed: $(brew list --versions "$pkg")"
  else
    echo "✗ $pkg not found via brew"
  fi
done
echo "Note: If libpq is installed, you may need: echo 'export PATH="$(brew --prefix libpq)/bin:$PATH"' >> ~/.zprofile"
echo

echo "=== Python (system) ==="
if command -v python3 >/dev/null 2>&1; then
  echo "python3: $(python3 -V)"
  echo "python3 path: $(which python3)"
  python3 -c "import platform, sys; print('platform.machine:', platform.machine()); print('arch:', platform.architecture()); print('venv site:', getattr(sys, 'real_prefix', None) or 'not in venv')" || true
else
  echo "python3 not found."
fi
echo

echo "=== Pip (system) ==="
if command -v pip3 >/dev/null 2>&1; then
  echo "pip3: $(pip3 -V)"
else
  echo "pip3 not found."
fi
echo

echo "=== Virtualenv sanity (run inside your project folder) ==="
if [ -d ".venv" ]; then
  echo ".venv exists."
  if [ -f ".venv/bin/python" ]; then
    VENV_PY=".venv/bin/python"
  elif [ -f ".venv/Scripts/python.exe" ]; then
    VENV_PY=".venv/Scripts/python.exe"
  else
    VENV_PY=""
  fi

  if [ -n "$VENV_PY" ]; then
    echo "Venv Python: $VENV_PY"
    file "$VENV_PY" || true
    "$VENV_PY" -c "import sys, platform; print('VENV python:', sys.version); print('machine:', platform.machine()); print('prefix:', sys.prefix)"
    echo "pip in venv:"
    "$VENV_PY" -m pip -V
    echo "pip list (top 50):"
    "$VENV_PY" -m pip list | head -n 50
  else
    echo "Could not locate venv python inside .venv"
  fi
else
  echo "No .venv folder found here."
fi
echo

echo "=== PostgreSQL toolchain check ==="
if command -v pg_config >/dev/null 2>&1; then
  echo "pg_config: $(pg_config --version) at $(which pg_config)"
else
  echo "pg_config not on PATH. If you installed libpq via brew, add it to PATH:"
  echo "  echo 'export PATH="$(brew --prefix libpq)/bin:$PATH"' >> ~/.zprofile"
fi
echo

echo "=== OpenSSL check (runtime) ==="
if command -v openssl >/dev/null 2>&1; then
  echo "openssl: $(openssl version)"
else
  echo "openssl not found on PATH."
fi
echo

echo "=== Compiler / headers quick probe ==="
if command -v pkg-config >/dev/null 2>&1; then
  echo "pkg-config found: $(pkg-config --version)"
  for lib in libpq libssl libjpeg; do
    if pkg-config --exists "$lib"; then
      echo "pkg-config: $lib OK"
    else
      echo "pkg-config: $lib MISSING (may be fine if using wheels)"
    fi
  done
else
  echo "pkg-config not found."
fi
echo

echo "=== DONE ==="
