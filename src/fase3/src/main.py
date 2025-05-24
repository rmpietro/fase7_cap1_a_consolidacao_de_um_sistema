import oracledb
import json
import requests
import pandas as pd
from pathlib import Path
from db_crud import read_table, create_tipo_cultura, create_area_cultivo, create_sensor, create_leitura


# Conexão ao Oracle com entrada de credenciais
def connect_to_db():
    try:
        with open("config/config.json") as config_file:
            config = json.load(config_file)
            print("------Programa de Monitoramento de Culturas------\n")
        return oracledb.connect(
            user=config['user'],
            password=config['password'],
            dsn=config['dsn']
        )
    except FileNotFoundError:

        print("------Programa de Monitoramento de Culturas------\n")

        username = input("Digite o usuário do banco de dados: ")
        password = input("Digite a senha do banco de dados: ")
        dsn = "oracle.fiap.com.br:1521/ORCL"
        config_path = Path(__file__).parent / "config" / "config.json"
        criar_config_json(username, password, dsn, config_path)
        return oracledb.connect(user=username, password=password, dsn=dsn)

def criar_config_json(user, password, dsn, filename):
    config_data = {
        "user": user,
        "password": password,
        "dsn": dsn
    }

    with open(filename, "w") as config_file:
        json.dump(config_data, config_file, indent=2)

    print(f"Arquivo '{filename}' criado com sucesso no diretório src/config.")

# Função para ler o DDL e criar as tabelas no Banco de Dados
def create_tables(connection):
    try:
        # Verifica se as tabelas já existem
        with connection.cursor() as cursor:
            cursor.execute("""SELECT COUNT(*) FROM user_Tables WHERE table_name IN ('AREA_CULTIVO', 'LEITURAS', 'SENSOR', 'TIPO_CULTURA')""")
            if cursor.fetchone()[0] != 0:
                print("Estrutura de Banco de Dados encontrada.")
                return

        # Se as tabelas não existem, cria-as usando o script DDL
        ddl_file_path = Path(__file__).parent / "config" / "script_ddl.sql"
        with open(ddl_file_path, 'r') as ddl_file:
            ddl_commands = ddl_file.read()

        ddl_blocks = ddl_commands.split(';\n')

        with connection.cursor() as cursor:
            for block in ddl_blocks:
                block = block.strip()
                if block:
                    if block.upper().startswith("BEGIN"):
                        block += ";\n/"
                    cursor.execute(block)
                    print(f"Comando executado com sucesso:\n{block}\n")

        connection.commit()
        print("Todas as tabelas foram criadas com sucesso.")
    except oracledb.Error as e:
        print(f"Ocorreu um erro ao executar o DDL: {e}")

# Função para inserir dados a partir do JSON
def insert_data_from_json(connection, json_file_path):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT COUNT(*) FROM LEITURAS
        """)
        if cursor.fetchone()[0] != 0:
            print("Tabelas aparentemente já estão populadas com pelo menos uma linha. Dados não serão importados.")
            return

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Inserindo dados na tabela tipo_cultura
    for cultura in data["tipo_cultura"]:
        create_tipo_cultura(connection, cultura["id_cultura"], cultura["nome"], cultura["data_plantio"])

    # Inserindo dados na tabela area_cultivo
    for area in data["area_cultivo"]:
        create_area_cultivo(connection, area["id_area"], area["id_cultura"], area["area_extensao"], area["end_localizacao"])

    # Inserindo dados na tabela sensor
    for sensor in data["sensor"]:
        create_sensor(connection, sensor["id_sensor"], sensor["id_area"], sensor["descricao"], sensor["tipo"], sensor["modelo"])

    # Inserindo dados na tabela leituras
    for leitura_list in data["leituras"]:
        for leitura in leitura_list:
            create_leitura(
                connection,
                leitura["timestamp"],
                leitura["temp"],
                leitura["humid"],
                leitura["P"],
                leitura["K"],
                leitura["pH"],
                leitura["irrigacao"]["estado"],
                leitura["irrigacao"]["motivo"],
                1  # Assumindo id_sensor 1 para todas as leituras, ajuste conforme necessário
            )

    print("Dados inseridos com sucesso a partir do JSON.")

def get_chuva_previsao():
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': -22.1256,
        'lon': -51.3889,
        'appid': "48380355e6896ab9c1318bc85deca9c3",
        'units': 'metric',
        'cnt': 5  # Limitar a previsão para 5 dias
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Extrair dados de chuva e data
    previsao_chuva = []
    for item in data['list']:
        data_hora = item['dt_txt']
        chuva = item.get('rain', {}).get('3h', 0)  # Usa 0 mm se não houver previsão de chuva
        previsao_chuva.append({"Data e Hora": data_hora, "Previsão de Chuva (mm)": chuva})

    # Exibir tabela formatada
    df_chuva = pd.DataFrame(previsao_chuva)
    print("\n\n-------Previsão de Chuva para Presidente Prudente na data de amanhã a cada 3h-------")
    print(df_chuva)
    print("-----------------------------------------------------------------------------\n\n")

# Função principal para uso do script
def main_menu():
    connection = connect_to_db()

    while True:
        print("\nEscolha uma opção:")
        print("1. Criar tabelas no banco de dados")
        print("2. Inserir dados do JSON no banco de dados")
        print("3. Iniciar o dashboard")
        print("4. Obter previsão de chuva para a cidade de Presidente Prudente (3/3h)")
        print("5. Sair")
        
        choice = input("Digite o número da opção desejada: ")

        if choice == "1":
            create_tables(connection)
        elif choice == "2":
            json_file_path = Path(__file__).parent / "dados" / "dados_app.json"
            insert_data_from_json(connection, json_file_path)
        elif choice == "3":
            from dashboard.dashboard import app as dashboard_app
            dashboard_app.run_server(debug=False)
            print("Dashboard não implementado.")
        elif choice == "4":
            get_chuva_previsao()
        elif choice == "5":
            print("Encerrando o programa...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

    # Fecha a conexão
    connection.close()

if __name__ == "__main__":
    main_menu()


