#!/bin/bash

PYTHON_CMD="python3"
PIP_CMD="pip3"
REQUIREMENTS_FILE="requirements.txt"
PROJECT_ROOT=$(pwd)

info() {
    echo "[INFO] $1"
}
error() {
    echo "[ERRO] $1" >&2; exit 1;
}
warning() {
    echo "[AVISO] $1"
}

install_jdk_macos() {
    if command -v brew &> /dev/null; then
        info "Tentando instalar OpenJDK via Homebrew..."
        if brew install openjdk; then # Instala a versão mais recente gerenciada pelo brew
            info "OpenJDK possivelmente instalado via Homebrew."
            # Adicionar instruções para configurar JAVA_HOME se necessário,
            # pois o brew pode instalar em um local não padrão para o PATH.
            # Exemplo para zsh (pode variar):
            # echo 'export PATH="/usr/local/opt/openjdk/bin:$PATH"' >> ~/.zshrc
            # echo 'export CPPFLAGS="-I/usr/local/opt/openjdk/include"' >> ~/.zshrc
            # warning "Pode ser necessário adicionar o OpenJDK do Brew ao seu PATH e reiniciar o terminal."
            # warning "Consulte: brew info openjdk"
            # Tentativa de encontrar o java recém-instalado
            if command -v java &> /dev/null; then return 0; else return 1; fi
        else
            warning "Falha ao tentar instalar OpenJDK via Homebrew."
            return 1
        fi
    else
        warning "Homebrew (brew) não encontrado. Não é possível instalar JDK automaticamente no macOS."
        return 1
    fi
}

install_jdk_linux() {
    local pkg_manager_found=false
    if command -v apt-get &> /dev/null; then
        pkg_manager_found=true
        info "Tentando instalar OpenJDK (versão padrão do repositório) via apt..."
        if sudo apt-get update && sudo apt-get install -y default-jdk; then
            info "OpenJDK (default-jdk) possivelmente instalado via apt."
            return 0
        else
            warning "Falha ao tentar instalar default-jdk via apt."
        fi
    fi
    
    if command -v dnf &> /dev/null; then
        pkg_manager_found=true
        info "Tentando instalar OpenJDK (java-latest-openjdk-devel) via dnf..."
        if sudo dnf install -y java-latest-openjdk-devel; then # Ou um pacote específico como java-17-openjdk-devel
            info "OpenJDK possivelmente instalado via dnf."
            return 0
        else
            warning "Falha ao tentar instalar OpenJDK via dnf."
        fi
    fi

    if command -v yum &> /dev/null; then # Menos comum para JDKs recentes
         pkg_manager_found=true
        info "Tentando instalar OpenJDK (java-latest-openjdk-devel) via yum..."
        if sudo yum install -y java-latest-openjdk-devel; then
            info "OpenJDK possivelmente instalado via yum."
            return 0
        else
            warning "Falha ao tentar instalar OpenJDK via yum."
        fi
    fi

    if ! $pkg_manager_found; then
        warning "Nenhum gerenciador de pacotes comum (apt, dnf, yum) encontrado para instalar JDK no Linux."
    fi
    return 1
}


attempt_python_install_macos() {
    if command -v brew &> /dev/null; then
        info "Tentando instalar Python 3 e pip via Homebrew..."
        if brew install python python3-pip; then
            info "Python 3 e pip possivelmente instalados via Homebrew."
            if command -v python3 &> /dev/null; then PYTHON_CMD="python3"; else PYTHON_CMD="python"; fi
            if command -v pip3 &> /dev/null; then PIP_CMD="pip3"; fi
            return 0
        else
            warning "Falha ao tentar instalar Python 3 e pip via Homebrew."
            return 1
        fi
    else
        warning "Homebrew (brew) não encontrado. Não é possível instalar Python automaticamente no macOS."
        return 1
    fi
}

attempt_python_install_linux() {
    if command -v apt-get &> /dev/null; then
        info "Tentando instalar Python 3 e pip via apt..."
        if sudo apt-get update && sudo apt-get install -y python3 python3-pip; then
            info "Python 3 e pip possivelmente instalados via apt."
            return 0
        else
            warning "Falha ao tentar instalar Python 3 e pip via apt."
            return 1
        fi
    elif command -v dnf &> /dev/null; then
        info "Tentando instalar Python 3 e pip via dnf..."
        if sudo dnf install -y python3 python3-pip; then
            info "Python 3 e pip possivelmente instalados via dnf."
            return 0
        else
            warning "Falha ao tentar instalar Python 3 e pip via dnf."
            return 1
        fi
    elif command -v yum &> /dev/null; then
        info "Tentando instalar Python 3 e pip via yum..."
        if sudo yum install -y python3 python3-pip; then
            info "Python 3 e pip possivelmente instalados via yum."
            return 0
        else
            warning "Falha ao tentar instalar Python 3 e pip via yum."
            return 1
        fi
    else
        warning "Nenhum gerenciador de pacotes comum (apt, dnf, yum) encontrado para instalar Python no Linux."
        return 1
    fi
}

info "Verificando dependências do script de setup..."
if ! command -v curl &> /dev/null; then error "curl não encontrado."; fi # Curl não é mais usado para JDK, mas pode ser para outras coisas no futuro
if ! command -v tar &> /dev/null; then error "tar não encontrado."; fi   # Tar não é mais usado para JDK

info "Verificando ambiente Python..."
PYTHON_INSTALLED_SUCCESSFULLY=false
if ! command -v $PYTHON_CMD &> /dev/null; then
    warning "$PYTHON_CMD não encontrado. Tentando instalar..."
    OS_FOR_PYTHON_INSTALL=$(uname -s)
    if [[ "$OS_FOR_PYTHON_INSTALL" == "Darwin" ]]; then
        if attempt_python_install_macos; then PYTHON_INSTALLED_SUCCESSFULLY=true; fi
    elif [[ "$OS_FOR_PYTHON_INSTALL" == "Linux" ]]; then
        if attempt_python_install_linux; then PYTHON_INSTALLED_SUCCESSFULLY=true; fi
    else
        warning "Instalação automática de Python não suportada para $OS_FOR_PYTHON_INSTALL."
    fi

    if ! $PYTHON_INSTALLED_SUCCESSFULLY || ! command -v $PYTHON_CMD &> /dev/null; then
        error "$PYTHON_CMD ainda não encontrado. Instalação manual necessária."
    fi
fi
info "$($PYTHON_CMD --version) encontrado."

if ! command -v $PIP_CMD &> /dev/null; then
    if [[ "$PYTHON_CMD" == "python3" ]] && command -v pip3 &> /dev/null; then PIP_CMD="pip3";
    elif [[ "$PYTHON_CMD" == "python" ]] && command -v pip &> /dev/null; then PIP_CMD="pip";
    else error "$PIP_CMD não encontrado. Instalação manual do pip necessária."; fi
fi
info "$($PIP_CMD --version) encontrado."

if [ -f "${PROJECT_ROOT}/${REQUIREMENTS_FILE}" ]; then
    info "Instalando dependências de '${REQUIREMENTS_FILE}' usando $PIP_CMD..."
    if $PIP_CMD install -r "${PROJECT_ROOT}/${REQUIREMENTS_FILE}"; then
        info "Dependências Python instaladas."
    else
        error "Falha ao instalar dependências Python."
    fi
else
    info "Arquivo '${REQUIREMENTS_FILE}' não encontrado."
fi

info "Verificando instalação do JDK no sistema..."
JDK_INSTALL_SUCCESSFUL=false
if command -v java &> /dev/null && command -v javac &> /dev/null; then
    info "JDK já parece estar instalado e no PATH."
    java -version
    javac -version
    JDK_INSTALL_SUCCESSFUL=true
else
    warning "JDK (java/javac) não encontrado no PATH. Tentando instalar..."
    OS_FOR_JDK_INSTALL=$(uname -s)
    if [[ "$OS_FOR_JDK_INSTALL" == "Darwin" ]]; then
        if install_jdk_macos; then JDK_INSTALL_SUCCESSFUL=true; fi
    elif [[ "$OS_FOR_JDK_INSTALL" == "Linux" ]]; then
        if install_jdk_linux; then JDK_INSTALL_SUCCESSFUL=true; fi
    else
        warning "Instalação automática de JDK não suportada para $OS_FOR_JDK_INSTALL."
    fi

    if ! $JDK_INSTALL_SUCCESSFUL || ! (command -v java &> /dev/null && command -v javac &> /dev/null); then
        error "JDK (java/javac) ainda não encontrado no PATH após tentativa de instalação. Instalação manual ou configuração do PATH necessária."
    else
        info "JDK instalado/encontrado com sucesso."
        java -version
        javac -version
    fi
fi

info "Setup do ambiente de desenvolvimento concluído."
exit 0
