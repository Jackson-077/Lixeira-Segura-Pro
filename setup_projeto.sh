#!/bin/bash

# ==========================================================
# Script de Configuração Inicial - Lixeira Segura Pro
#
# Desenvolvido por: Jackson Q.
# ==========================================================

set -e

echo "=========================================="
echo " Lixeira Segura Pro"
echo " Configuração Inicial"
echo "=========================================="
echo

# ----------------------------------------------------------
# Verificar Python
# ----------------------------------------------------------

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 não encontrado."
    echo "Instale o Python3 antes de continuar."
    exit 1
fi

# ----------------------------------------------------------
# Verificar módulo venv
# ----------------------------------------------------------

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "❌ O módulo python3-venv não está instalado."
    echo
    echo "Instale com:"
    echo
    echo "sudo apt install python3-venv"
    exit 1
fi

# ----------------------------------------------------------
# Remover venv antiga
# ----------------------------------------------------------

if [ -d "venv" ]; then
    echo "🗑️ Removendo ambiente virtual antigo..."
    rm -rf venv
fi

# ----------------------------------------------------------
# Criar ambiente virtual
# ----------------------------------------------------------

echo "📦 Criando ambiente virtual..."

python3 -m venv venv

# ----------------------------------------------------------
# Atualizar pip
# ----------------------------------------------------------

echo "⬆️ Atualizando pip..."

./venv/bin/python -m pip install --upgrade pip

# ----------------------------------------------------------
# Instalar dependências
# ----------------------------------------------------------

echo "📥 Instalando dependências..."

./venv/bin/pip install -r requirements.txt

# ----------------------------------------------------------
# Gerar run.sh
# ----------------------------------------------------------

echo "🚀 Criando run.sh..."

cat > run.sh << 'EOF'
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
EOF

chmod +x run.sh

# ----------------------------------------------------------
# Finalizado
# ----------------------------------------------------------

echo
echo "=========================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo
echo "Arquivos criados:"
echo "  ✔ Ambiente virtual (venv)"
echo "  ✔ Dependências instaladas"
echo "  ✔ Script run.sh"
echo
echo "Para executar o programa:"
echo
echo "    ./run.sh"
echo
echo "=========================================="