import subprocess

def main_menu():
    print("Iniciando o dashboard Streamlit...")
    try:
        subprocess.run(["streamlit", "run", "dashboard/Dashboard_Inicial.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar o Streamlit: {e}")
    except FileNotFoundError:
        print("Erro: Streamlit não encontrado. Certifique-se de que o Streamlit está instalado.")

if __name__ == "__main__":
    main_menu()


