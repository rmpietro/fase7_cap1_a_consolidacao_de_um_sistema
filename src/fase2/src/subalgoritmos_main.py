import os
import platform

def exibir_menu() -> None:
    print(
        """
        MENU PRINCIPAL
        ----------------------------------
        1 - Inserir novo Silo
        2 - Ler Registro de Silo
        3 - Listar Todos os Silos
        4 - Alterar Silo Existente
        5 - Excluir Silo Existente
        6 - Gerar Relatório de Silos
        7 - Exportar Dados do Banco (Backup JSON)
        8 - Importar Dados para o Banco (Backup JSON)
        9 - Sair
        ----------------------------------
        """
    )

def limpar_console() -> None:
    sistema = platform.system()
    if sistema == "Windows":
        os.system("cls")
    elif sistema == "Linux" or sistema == "Darwin":
        os.system("clear")

def exibir_tipo() -> None:
    print("""
    Lista de produtos disponíveis:
1 - Milho
2 - Soja
3 - Arroz
4 - Trigo
5 - Feijão
""")