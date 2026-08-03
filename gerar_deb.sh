#!/bin/bash

# ==========================================================
# Lixeira Segura Pro - Gerador DEB Profissional
# Versão: 1.1 (Correção PEP 668 - VENV Edition)
# Autor: Jackson Q.
# ==========================================================

set -e

APP_NAME="lixeira-segura"
APP_TITLE="Lixeira Segura Pro"
VERSION="1.1.0"
MAIN_SCRIPT="lixeira_segura.py"
ICON="icon/icone.png"
VENV_BIN="./venv/bin"

echo "======================================"
echo " Lixeira Segura Pro - Gerador DEB"
echo "======================================"

# 1. Verificações Iniciais
[ -d "venv" ] || { echo "❌ Erro: venv não encontrada. Rode ./setup_projeto.sh primeiro."; exit 1; }
[ -f "$MAIN_SCRIPT" ] || { echo "❌ Erro: $MAIN_SCRIPT não encontrado."; exit 1; }
[ -f "$ICON" ] || { echo "❌ Erro: $ICON não encontrado na pasta icon/."; exit 1; }

# 2. Limpeza
echo "🧹 Limpando builds antigos..."
rm -rf build dist deb_build *.spec *.deb

# 3. Compilação com PyInstaller via VENV
echo "🚀 Compilando executável profissional (via VENV)..."
$VENV_BIN/python -m PyInstaller \
    --noconfirm \
    --onedir \
    --windowed \
    --name "$APP_NAME" \
    --add-data "icon/icone.png:icon" \
    --collect-all "customtkinter" \
    --hidden-import "PIL.Image" \
    --hidden-import "darkdetect" \
    --hidden-import "packaging" \
    "$MAIN_SCRIPT"

# 4. Criar estrutura do pacote DEB
echo "📦 Criando estrutura do pacote DEB..."
DEB_DIR="deb_build"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/$APP_NAME"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"

# 5. Copiar arquivos compilados
cp -r "dist/$APP_NAME/"* "$DEB_DIR/opt/$APP_NAME/"
cp "$ICON" "$DEB_DIR/usr/share/pixmaps/$APP_NAME.png"

# 6. Criar arquivo CONTROL
cat << EOF > "$DEB_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Jackson Q.
Depends: libxcb-cursor0, xdg-utils
Description: Lixeira Segura Pro
 Aplicativo para destruicao segura de arquivos.
 Desenvolvido por Jackson Q. com interface moderna.
EOF

# 7. Criar comando de atalho no sistema
cat << EOF > "$DEB_DIR/usr/bin/$APP_NAME"
#!/bin/bash
exec /opt/$APP_NAME/$APP_NAME "\$@"
EOF
chmod 755 "$DEB_DIR/usr/bin/$APP_NAME"

# 8. Criar atalho no Menu de Aplicativos
cat << EOF > "$DEB_DIR/usr/share/applications/$APP_NAME.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_TITLE
Comment=Destruicao segura de arquivos
Exec=$APP_NAME
Icon=$APP_NAME
Terminal=false
Categories=Utility;System;
StartupNotify=true
EOF
chmod 644 "$DEB_DIR/usr/share/applications/$APP_NAME.desktop"

# 9. Gerar o arquivo .deb final
echo "🏗️  Gerando instalador final..."
dpkg-deb --build "$DEB_DIR" "${APP_NAME}_${VERSION}_amd64.deb"

echo "======================================"
echo "  🎉 SUCESSO!"
echo "======================================"
echo "Pacote criado: ${APP_NAME}_${VERSION}_amd64.deb"
echo "Para instalar: sudo apt install ./${APP_NAME}_${VERSION}_amd64.deb"
echo "======================================"
