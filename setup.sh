#!/bin/bash

# Este script automatiza a instalação do comando 'prose' no sistema.
echo "Configurando o ambiente para a Prose Lang..."

# Pega o caminho absoluto do diretório atual.
INSTALL_DIR="$(pwd)"
PROSE_CMD_PATH="$INSTALL_DIR/prose"

# Garante que o script 'prose' tenha permissão de execução.
chmod +x "$PROSE_CMD_PATH"

# Define o local padrão para binários do usuário.
BIN_DIR="/usr/local/bin"
SYMLINK_PATH="$BIN_DIR/prose"
echo "Será necessário usar a senha de administrador para criar o comando 'prose' em $BIN_DIR"

# Remove um link antigo se ele existir, para evitar erros.
if [ -L "$SYMLINK_PATH" ]; then
    sudo rm "$SYMLINK_PATH"
fi

# Cria um link simbólico (atalho) do nosso script para a pasta de binários do sistema.
# O 'sudo' é necessário porque /usr/local/bin é um diretório protegido.
sudo ln -s "$PROSE_CMD_PATH" "$SYMLINK_PATH"
echo ""
echo "Feito! O comando 'prose' foi instalado com sucesso."
echo "Por favor, abra uma NOVA janela do terminal e teste com: prose seu_arquivo.prose"