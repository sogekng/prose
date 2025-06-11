@echo off
REM Este script funciona como o comando 'prose' no Windows.
REM %~dp0 expande para o diretório onde este script .bat está localizado.
REM %* passa todos os argumentos recebidos para o script Python.
python "%~dp0\src\main.py" %*