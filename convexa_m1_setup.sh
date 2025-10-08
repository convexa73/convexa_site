#!/usr/bin/env bash
set -e

echo "=== Convexa M1 one-shot setup ==="

# 1) Xcode Command Line Tools
if xcode-select -p >/dev/null 2>&1; then
  echo "✓ Xcode Command Line Tools found."
else
  echo "✗ Xcode CLT not found. A janela de instalação será aberta agora (interativa)."
  xcode-select --install || true
  echo "Após instalar as CLT, reexecute este script."
  exit 1
fi

# 2) Homebrew
if command -v brew >/dev/null 2>&1; then
  echo "✓ Homebrew encontrado: $(brew -v | head -n1)"
else
  echo "✗ Homebrew não encontrado. Instale manualmente (Apple Silicon):"
  echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo "Depois rode novamente este script."
  exit 1
fi

# 3) Pacotes necessários
pkgs=(openssl@3 libpq jpeg libtiff freetype webp pkg-config)
for p in "${pkgs[@]}"; do
  if brew list --versions "$p" >/dev/null 2>&1; then
    echo "✓ $p já instalado: $(brew list --versions "$p")"
  else
    echo "→ Instalando $p ..."
    brew install "$p"
  fi
done

# 4) PATH para libpq (pg_config)
LIBPQ_PREFIX="$(brew --prefix libpq)"
if ! command -v pg_config >/dev/null 2>&1; then
  echo "→ Adicionando libpq ao PATH via ~/.zprofile"
  echo "export PATH=\"$LIBPQ_PREFIX/bin:$PATH\"" >> "$HOME/.zprofile"
  # shellcheck disable=SC1090
  source "$HOME/.zprofile" || true
else
  echo "✓ pg_config disponível: $(pg_config --version)"
fi

# 5) Criar/atualizar venv (arm64) e instalar requirements se existir
if [ -f "requirements.txt" ]; then
  if [ ! -d ".venv" ]; then
    echo "→ Criando venv arm64 em .venv"
    /usr/bin/arch -arm64 python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install -U pip setuptools wheel
  echo "→ Instalando requirements.txt"
  pip install -r requirements.txt || {
    echo "Falha no pip install. Tentando ajuste com psycopg2-binary..."
    pip uninstall -y psycopg2 || true
    pip install psycopg2-binary
    pip install -r requirements.txt
  }
else
  echo "Aviso: requirements.txt não encontrado na pasta atual."
fi

echo "=== Setup concluído. ==="
echo "Dicas:"
echo "  - Se 'Pillow' falhar, garanta que jpeg/libtiff/freetype/webp foram instalados (já cuidamos acima)."
echo "  - Se 'psycopg2' falhar, use 'psycopg2-binary' em dev."
