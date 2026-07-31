#!/bin/bash

# ==========================================================
# Lixeira Segura Pro
# Gerador DEB profissional usando PyInstaller
#
# Autor: Jackson Q.
# ==========================================================

set -e

APP_NAME="lixeira-segura"
APP_TITLE="Lixeira Segura Pro"
VERSION="1.0.0"

MAIN_SCRIPT="lixeira_segura.py"
ICON="icon/icone.png"

SPEC_FILE="${APP_NAME}.spec"

BUILD_DIR="build"
DIST_DIR="dist"
DEB_DIR="deb_build"

OUTPUT="${APP_NAME}_${VERSION}_amd64.deb"


############################################
# Funções
############################################

erro()
{
    echo "ERRO: $1"
    exit 1
}

ok()
{
    echo "[OK] $1"
}


############################################
# Verificações
############################################

echo "======================================"
echo " Lixeira Segura Pro - Gerador DEB"
echo "======================================"


command -v python3 >/dev/null || \
erro "Python3 não encontrado"


command -v dpkg-deb >/dev/null || \
erro "dpkg-deb não encontrado"


[ -f "$MAIN_SCRIPT" ] || \
erro "$MAIN_SCRIPT não encontrado"


[ -f "$ICON" ] || \
erro "$ICON não encontrado"


############################################
# Verificar PyInstaller
############################################

echo "Verificando PyInstaller..."

if ! python3 -m PyInstaller --version >/dev/null 2>&1
then

    echo "PyInstaller não encontrado."

    python3 -m pip install --user pyinstaller

fi


PYI_VERSION=$(python3 -m PyInstaller --version)

echo "PyInstaller: $PYI_VERSION"


############################################
# Limpeza
############################################

echo "Limpando arquivos antigos..."

rm -rf "$BUILD_DIR"
rm -rf "$DIST_DIR"
rm -rf "$DEB_DIR"
rm -f "$SPEC_FILE"
rm -f "$OUTPUT"


############################################
# Localizar CustomTkinter
############################################

echo "Verificando CustomTkinter..."

python3 - <<EOF
import customtkinter
print("CustomTkinter OK:", customtkinter.__version__)
EOF


ok "Ambiente preparado"


echo "Próxima etapa: criando SPEC..."
############################################
# Criar arquivo SPEC
############################################

echo "Criando arquivo SPEC..."

CTK_PATH=$(python3 - <<EOF
import customtkinter
import os
print(os.path.dirname(customtkinter.__file__))
EOF
)


cat > "$SPEC_FILE" <<EOF
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files


datas = []

datas += collect_data_files("customtkinter")

datas += [
    ("icon/icone.png", "icon")
]


hiddenimports = [
    "customtkinter",
    "PIL",
    "PIL.Image",
    "darkdetect",
    "packaging"
]


a = Analysis(
    ["$MAIN_SCRIPT"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(a.pure)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="$APP_NAME",
    debug=False,
    strip=False,
    upx=True,
    console=False
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="$APP_NAME"
)

EOF


ok "Arquivo SPEC criado."


############################################
# Compilar com PyInstaller
############################################

echo "Compilando executável..."


python3 -m PyInstaller \
    --clean \
    "$SPEC_FILE"


ok "Executável criado."
############################################
# Criar estrutura DEB
############################################

echo "Criando estrutura do pacote DEB..."


mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/$APP_NAME"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"


############################################
# Copiar executável
############################################

cp -r "dist/$APP_NAME/"* \
"$DEB_DIR/opt/$APP_NAME/"


chmod +x \
"$DEB_DIR/opt/$APP_NAME/$APP_NAME"


############################################
# Copiar ícone
############################################

cp "$ICON" \
"$DEB_DIR/usr/share/pixmaps/$APP_NAME.png"


############################################
# Arquivo CONTROL
############################################

cat > "$DEB_DIR/DEBIAN/control" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Jackson Q.
Depends: libxcb-cursor0, xdg-utils, libxcb-cursor0
Description: Lixeira Segura Pro
 Aplicativo para destruição segura de arquivos.
 Desenvolvido por Jackson Q.
EOF


############################################
# Criar comando do sistema
############################################

cat > "$DEB_DIR/usr/bin/$APP_NAME" <<EOF
#!/bin/bash

cd /opt/$APP_NAME

exec ./lixeira-segura "\$@"

EOF


chmod 755 "$DEB_DIR/usr/bin/$APP_NAME"

############################################
# Criar atalho do menu
############################################

cat > "$DEB_DIR/usr/share/applications/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_TITLE
Comment=Destruição segura de arquivos
Exec=$APP_NAME
Icon=$APP_NAME
Terminal=false
Categories=Utility;
StartupNotify=true
EOF


chmod 644 "$DEB_DIR/usr/share/applications/$APP_NAME.desktop"


ok "Estrutura DEB criada."
############################################
# Gerar pacote DEB
############################################

echo "Gerando arquivo .deb..."

dpkg-deb --build \
"$DEB_DIR" \
"$OUTPUT"


if [ -f "$OUTPUT" ]; then

    echo
    echo "======================================"
    echo "  SUCESSO!"
    echo "======================================"
    echo
    echo "Pacote criado:"
    echo "$OUTPUT"
    echo
    echo "Instalar:"
    echo "sudo apt install ./$OUTPUT"
    echo

else

    echo "Erro: pacote não foi criado."
    exit 1

fi