import platform
import subprocess
import os
import stat

# Script para detectar o SO e executar o script de setup de ambiente de desenvolvimento apropriado.

def run_script(script_path, shell_command=None):
    """Tenta executar um script."""
    if not os.path.exists(script_path):
        print(f"[ERRO] Script de setup não encontrado em: {script_path}")
        print("Certifique-se de que você está executando este inicializador da raiz do projeto.")
        return False

    try:
        print(f"[INFO] Executando script: {script_path}...")
        if shell_command:
            # Para scripts .sh, pode ser necessário dar permissão de execução
            if script_path.endswith(".sh"):
                current_permissions = os.stat(script_path).st_mode
                if not (current_permissions & stat.S_IXUSR):
                    print(f"[INFO] Adicionando permissão de execução para {script_path}")
                    os.chmod(script_path, current_permissions | stat.S_IXUSR)
            
            # Usar uma lista de argumentos para subprocess.run
            command_list = [shell_command, script_path]
            if shell_command.lower() == "powershell.exe" or shell_command.lower() == "powershell":
                 # Para PowerShell, é comum precisar ajustar a política ou usar -File
                 command_list = [shell_command, "-ExecutionPolicy", "Bypass", "-File", script_path]

            process = subprocess.run(command_list, check=False) # check=False para inspecionar returncode
            if process.returncode != 0:
                print(f"[ERRO] O script de setup ({script_path}) encontrou um erro (código de saída: {process.returncode}).")
                return False
        else:
            # Este bloco 'else' raramente será usado para .sh ou .ps1, pois shell_command é fornecido.
            # Mantido para generalidade, mas com aviso.
            print(f"[AVISO] Executando {script_path} sem um shell_command explícito. Certifique-se de que é executável e tem shebang correto.")
            process = subprocess.run([script_path], shell=True, check=False) # shell=True pode ser um risco de segurança se script_path for de fonte não confiável
            if process.returncode != 0:
                print(f"[ERRO] O script de setup ({script_path}) encontrou um erro (código de saída: {process.returncode}).")
                return False

        print(f"[INFO] Script de setup ({script_path}) concluído.")
        return True
    except FileNotFoundError:
        print(f"[ERRO] O interpretador '{shell_command}' não foi encontrado. Verifique se está instalado e no PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Erro ao executar o script de setup ({script_path}): {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Um erro inesperado ocorreu: {e}")
        return False

def main():
    print("-------------------------------------------------------------")
    print("Inicializador do Setup do Ambiente de Desenvolvimento Prose Lang")
    print("-------------------------------------------------------------")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    os_system = platform.system().lower()
    success = False

    if os_system == "windows":
        print("[INFO] Sistema Operacional detectado: Windows")
        script_to_run = os.path.join(script_dir, "setup.ps1") # Nome alterado
        success = run_script(script_to_run, shell_command="powershell.exe")
    elif os_system == "linux":
        print("[INFO] Sistema Operacional detectado: Linux")
        script_to_run = os.path.join(script_dir, "setup.sh") # Nome alterado
        success = run_script(script_to_run, shell_command="bash")
    elif os_system == "darwin": # macOS
        print("[INFO] Sistema Operacional detectado: macOS")
        script_to_run = os.path.join(script_dir, "setup.sh") # Nome alterado
        success = run_script(script_to_run, shell_command="bash")
    else:
        print(f"[ERRO] Sistema Operacional não suportado: {os_system}")
        print("Este script de setup suporta apenas Windows, Linux e macOS.")
        exit(1)

    if success:
        print("\n[INFO] Processo de setup do ambiente de desenvolvimento finalizado.")
        print("Se o Python ou o JDK foram instalados ou atualizados, pode ser necessário")
        print("reiniciar seu terminal ou IDE para que as alterações no PATH tenham efeito.")
    else:
        print("\n[AVISO] O processo de setup do ambiente de desenvolvimento encontrou problemas.")
        print("Por favor, revise as mensagens de erro acima.")

if __name__ == "__main__":
    main()
