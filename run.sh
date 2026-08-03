#!/bin/bash

# ==========================================
# Lixeira Segura Pro
#
# Desenvolvido por Jackson Q.
# ==========================================

DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$DIR"

source venv/bin/activate

exec python3 lixeira_segura.py "$@"
