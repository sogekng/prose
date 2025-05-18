<#
.SYNOPSIS
    Script para configurar o ambiente de desenvolvimento da Prose Lang no Windows.
    Tenta instalar Python 3, pip e JDK sistemicamente.
    Instala dependências Python do requirements.txt.
    Executa as instalações sem perguntas, pedindo elevação apenas quando necessário.
#>

# --- Configurações ---
$PythonExecutable = "python"
$PipExecutable = "pip"
$RequirementsFile = "requirements.txt"
$ProjectRoot = Get-Location

# --- Funções Auxiliares ---
function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Error { param([string]$Message) Write-Host "[ERRO] $Message" -ForegroundColor Red; exit 1 }
function Write-Warning { param([string]$Message) Write-Host "[AVISO] $Message" -ForegroundColor Yellow }
function Test-CommandExists { param([string]$Command) return (Get-Command $Command -ErrorAction SilentlyContinue) }

function Install-Jdk-Windows {
    Write-Warning "JDK (java/javac) não encontrado. Tentando instalar..."
    $jdkInstalled = $false

    if (Test-CommandExists "choco") {
        Write-Info "Tentando instalar OpenJDK via Chocolatey (requer elevação)..."
        try {
            # 'openjdk' em choco geralmente instala a última LTS. Para a mais recente, pode ser 'openjdk --version=latest' ou um pacote específico.
            # Vamos usar 'openjdk' que é mais comum.
            Start-Process choco -ArgumentList "install openjdk -y --no-progress" -Verb RunAs -Wait
            Write-Info "OpenJDK possivelmente instalado via Chocolatey. Um novo terminal pode ser necessário para atualizar o PATH."
            # É difícil verificar o sucesso imediatamente aqui sem reabrir o terminal.
            # O usuário precisará verificar.
            $jdkInstalled = $true # Assume tentativa de sucesso
        } catch { Write-Warning "Falha ao tentar instalar OpenJDK via Chocolatey: $($_.Exception.Message)" }
    } else { Write-Info "Chocolatey (choco) não encontrado." }

    if (-not $jdkInstalled -and (Test-CommandExists "winget")) {
        Write-Info "Tentando instalar Microsoft OpenJDK (versão mais recente) via Winget..."
        try {
            # O ID pode variar, ex: Microsoft.OpenJDK.17 ou Microsoft.OpenJDK.LTS
            # Vamos tentar um ID comum para a versão mais recente do OpenJDK da Microsoft.
            winget install --id Microsoft.OpenJDK.Latest --exact --accept-source-agreements --accept-package-agreements --silent
            Write-Info "OpenJDK (Microsoft) possivelmente instalado via Winget. Um novo terminal pode ser necessário."
            $jdkInstalled = $true # Assume tentativa de sucesso
        } catch { Write-Warning "Falha ao tentar instalar OpenJDK via Winget: $($_.Exception.Message)" }
    } elseif (-not $jdkInstalled) { Write-Info "Winget não encontrado." }
    
    if ($jdkInstalled) {
        Write-Warning "A instalação do JDK pode ter alterado o PATH. É altamente recomendável fechar este terminal e executar o script novamente em um novo terminal (ou verificar 'java -version') para que as alterações no PATH tenham efeito."
    }
    return $jdkInstalled
}

function Install-Python-Windows {
    Write-Warning "$PythonExecutable não encontrado. Tentando instalar..."
    $pythonInstalled = $false

    if (Test-CommandExists "choco") {
        Write-Info "Tentando instalar Python 3 e pip via Chocolatey (requer elevação)..."
        try {
            Start-Process choco -ArgumentList "install python pip -y --no-progress" -Verb RunAs -Wait
            Write-Info "Python 3 e pip possivelmente instalados via Chocolatey. Um novo terminal pode ser necessário."
            $pythonInstalled = $true
        } catch { Write-Warning "Falha ao tentar instalar Python via Chocolatey: $($_.Exception.Message)" }
    } else { Write-Info "Chocolatey (choco) não encontrado." }

    if (-not $pythonInstalled -and (Test-CommandExists "winget")) {
        Write-Info "Tentando instalar Python 3 via Winget..."
        try {
            winget install --id Python.Python.3 --exact --accept-source-agreements --accept-package-agreements --silent
            Write-Info "Python 3 possivelmente instalado via Winget. Um novo terminal pode ser necessário."
            $pythonInstalled = $true
        } catch { Write-Warning "Falha ao tentar instalar Python via Winget: $($_.Exception.Message)" }
    } elseif (-not $pythonInstalled) { Write-Info "Winget não encontrado." }
    
    if ($pythonInstalled) {
        Write-Warning "A instalação do Python pode ter alterado o PATH. É altamente recomendável fechar este terminal e executar o script novamente em um novo terminal para que as alterações no PATH tenham efeito."
    }
    return $pythonInstalled
}

Write-Info "Verificando ambiente Python..."
if (-not (Test-CommandExists $PythonExecutable)) {
    if (-not (Install-Python-Windows)) {
        Write-Error "$PythonExecutable não encontrado e falha na tentativa de instalação. Instalação manual necessária."
    }
    if (-not (Test-CommandExists $PythonExecutable)) {
         Write-Error "$PythonExecutable ainda não encontrado após tentativa de instalação. Feche e abra um novo terminal/PowerShell e tente novamente, ou instale manualmente."
    }
}
Write-Info "$($PythonExecutable --version 2>&1) encontrado."

if (-not (Test-CommandExists $PipExecutable)) {
    Write-Info "Tentando garantir/atualizar o pip usando '$PythonExecutable -m ensurepip --upgrade'..."
    Invoke-Expression "$PythonExecutable -m ensurepip --upgrade"
    if (-not (Test-CommandExists $PipExecutable)) {
        if ($PythonExecutable -eq "python3" -and (Test-CommandExists "pip3")) { $PipExecutable = "pip3" }
        else { Write-Error "$PipExecutable ainda não encontrado. Verifique a instalação do Python/pip." }
    }
}
Write-Info "$($PipExecutable --version 2>&1) encontrado."

if (Test-Path -Path (Join-Path -Path $ProjectRoot -ChildPath $RequirementsFile)) {
    Write-Info "Instalando dependências de '$RequirementsFile' usando $PipExecutable..."
    $pipCommand = "$PipExecutable install -r `"$((Join-Path -Path $ProjectRoot -ChildPath $RequirementsFile))`""
    try {
        Invoke-Expression $pipCommand
        Write-Info "Dependências Python instaladas."
    } catch { Write-Error "Falha ao instalar dependências Python. Erro: $($_.Exception.Message)" }
} else { Write-Info "Arquivo '$RequirementsFile' não encontrado." }


Write-Info "Verificando instalação do JDK no sistema..."
$jdkIsAvailable = $false
if ((Test-CommandExists "java") -and (Test-CommandExists "javac")) {
    Write-Info "JDK (java/javac) já parece estar instalado e no PATH."
    java -version # Oculta a saída de erro se houver
    javac -version # Oculta a saída de erro se houver
    $jdkIsAvailable = $true
} else {
    if (-not (Install-Jdk-Windows)) {
        Write-Error "JDK (java/javac) não encontrado e falha na tentativa de instalação. Instalação manual ou configuração do PATH necessária."
    }
     # Após a tentativa de instalação, verifica novamente. O usuário pode precisar reiniciar o terminal.
    if ((Test-CommandExists "java") -and (Test-CommandExists "javac")) {
        Write-Info "JDK (java/javac) encontrado após tentativa de instalação."
        java -version
        javac -version
        $jdkIsAvailable = $true
    } else {
        Write-Error "JDK (java/javac) ainda não encontrado no PATH após tentativa de instalação. Instalação manual ou configuração do PATH necessária. Pode ser preciso reiniciar o terminal."
    }
}

Write-Info "Setup do ambiente de desenvolvimento concluído."
exit 0
