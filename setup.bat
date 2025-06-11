@echo off
rem Este script automatiza a instalação do comando 'prose' no Windows.
echo Configurando o ambiente para a Prose Lang...

rem Adiciona o diretório atual ao PATH do usuário de forma permanente.
rem Isso permite que o comando 'prose.bat' seja encontrado de qualquer lugar.
setx PATH "%PATH%;%cd%"

echo.
echo Feito! O comando 'prose' foi adicionado ao seu PATH.
echo Por favor, abra uma NOVA janela do terminal (CMD ou PowerShell) e teste com: prose seu_arquivo.prose