#!/bin/bash

# ==========================================================
# Script de Configuração Inicial - Lixeira Segura Pro
# Desenvolvido por: Jackson Q.
# ==========================================================

echo "🛠️ Iniciando configuração do ambiente profissional..."

# 1. Instalar dependências do sistema necessárias para o Python e Tkinter
echo "📥 Instalando dependências do sistema (pode pedir senha)..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-tk libxcb-cursor0

# 2. Criar ambiente virtual (venv)
echo "📦 Criando ambiente virtual isolado (venv)..."
rm -rf venv
python3 -m venv venv

# 3. Instalar dependências no ambiente isolado
echo "📥 Instalando bibliotecas no ambiente virtual..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "🎉 AMBIENTE CONFIGURADO COM SUCESSO!"
    echo "✅ Pasta 'venv' pronta com CustomTkinter e PyInstaller."
    echo "🚀 Agora você pode rodar o 'gerar_deb.sh'."
    echo "=========================================="
else
    echo "❌ Ocorreu um erro na configuração do ambiente."
    exit 1
fi
