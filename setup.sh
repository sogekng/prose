#!/bin/bash
echo "Configurando o ambiente para a Prose Lang..."

INSTALL_DIR="$(pwd)"
PROSE_CMD_PATH="$INSTALL_DIR/prose"

chmod +x "$PROSE_CMD_PATH"

BIN_DIR="/usr/local/bin"
SYMLINK_PATH="$BIN_DIR/prose"
echo "Será necessário usar a senha de administrador para criar o comando 'prose' em $BIN_DIR"

if [ -L "$SYMLINK_PATH" ]; then
    sudo rm "$SYMLINK_PATH"
fi

sudo ln -s "$PROSE_CMD_PATH" "$SYMLINK_PATH"
echo ""
echo "Feito! O comando 'prose' foi instalado com sucesso."
echo "Por favor, abra uma NOVA janela do terminal e teste com: prose seu_arquivo.prose"