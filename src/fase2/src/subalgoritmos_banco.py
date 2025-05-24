import oracledb
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

oracledb.defaults.fetch_lobs = False

# Definição de produtos (milho, soja, arroz, trigo, feijão)
milho  = (1, "Milho", 1440.97, 13.0, 14.1, 15.0, 25.1, 6.0, 7.6)
soja   = (2, "Soja", 1784.67, 11.0, 13.1, 15.0, 25.1, 6.0, 7.6)
arroz  = (3, "Arroz", 1255.00, 12.0, 14.1, 10.0, 25.1, 6.0, 7.1)
trigo  = (4, "Trigo", 1432.76, 12.0, 14.1, 10.0, 25.1, 5.5, 6.6)
feijao = (5, "Feijão", 3103.00, 11.0, 13.1, 15.0, 25.1, 5.8, 6.9)

conectado = False
conn = None

def set_connection(usuario: str, senha: str) -> bool:
    global conn, conectado
    try:
        conn = oracledb.connect(user=usuario, password=senha, dsn='oracle.fiap.com.br:1521/ORCL')
    except oracledb.DatabaseError as Error:
        print(f"Erro ao estabelecer conexão: {Error}")
        conectado = False
        return False
    else:
        conectado = True
        return True

def check_table_exists():
    try:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT COUNT(*) FROM user_Tables WHERE table_name = 'SILOS'""")
            if cursor.fetchone()[0] == 0:
                print("Estrutura de Banco de Dados não encontrada.")
                print("Criando tabela \"SILOS\" no Banco de Dados conectado...")
                diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
                caminho = os.path.join(diretorio_raiz, 'arquivos', 'silos.sql')
                with open(caminho, "r") as arq:
                    sql_ddl = arq.read()
                    cursor.execute(sql_ddl)
                    conn.commit()
                    print("Tabela SILOS criada com sucesso!")
    except oracledb.DatabaseError as Error:
        print(f"Erro ao buscar tabela SILOS: {Error}")
        return False

def close_connection():
    if conn:
        try:
            conn.close()
        except oracledb.DatabaseError as e:
            print(f"Erro ao fechar a conexão: {e}")

# Função para inserir registro no banco de dados
def insert(tipo: int, quantidade: float, silo_nome: str, endereco: str, capacidade: float,
           umidade: float, temperatura: float, ph: float, obs: str) -> bool:
    print("----- CADASTRAR SILO -----\n")
    try:
        with conn.cursor() as cursor:
            if tipo == 1:
                nome_produto = milho[1]
            elif tipo == 2:
                nome_produto = soja[1]
            elif tipo == 3:
                nome_produto = arroz[1]
            elif tipo == 4:
                nome_produto = trigo[1]
            elif tipo == 5:
                nome_produto = feijao[1]
            else:
                nome_produto = ''

            cadastro = """ 
                INSERT INTO SILOS(nome_produto, tipo_produto, quantidade, silo_nome, endereco, capacidade, 
                                  data_hora_registro, umidade, temperatura, ph, observacoes) 
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11) 
            """
            cursor.execute(cadastro, (nome_produto, tipo, quantidade, silo_nome, endereco, capacidade,
                                      datetime.now(), umidade, temperatura, ph, obs))
            conn.commit()
    except oracledb.DatabaseError as Error:
        print(f"Erro ao gravar registro: {Error}")
        return False
    else:
        print("Registro gravado com sucesso!")
        return True

#Função para alterar um registro no banco de dados
def update(dados_silo: list) -> bool:
    print("----- ALTERAR -----\n")
    try:
        with conn.cursor() as cursor:
            alteracao = f"""UPDATE SILOS SET nome_produto = :1, tipo_produto = :2, quantidade = :3, 
                silo_nome = :4, endereco = :5, capacidade = :6, umidade = :7, temperatura = :8, 
                ph = :9, observacoes = :10 WHERE id = :11"""

            match dados_silo[1]:
                case 1:
                    nome_produto = milho[1]
                case 2:
                    nome_produto = soja[1]
                case 3:
                    nome_produto = arroz[1]
                case 4:
                    nome_produto = trigo[1]
                case 5:
                    nome_produto = feijao[1]
                case _:
                    nome_produto = ''

            cursor.execute(alteracao, (nome_produto,  dados_silo[1], dados_silo[2],
                                       dados_silo[3], dados_silo[4], dados_silo[5],
                                       dados_silo[6], dados_silo[7], dados_silo[8],
                                       dados_silo[9], dados_silo[0]))
            conn.commit()

    except oracledb.DatabaseError as Error:
        print(f"Erro ao alterar registro: {Error}")
        return False
    except Exception as Error:
        print(f"Erro inesperado: {Error}")
        return False
    else:
        print("Registro alterado com sucesso!")
        return True

# Função para listar todos os registros
def get_all() -> None:
    print("----- LISTAR SILOS -----\n")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM SILOS")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['id', 'nome_produto', 'tipo_produto', 'quantidade', 'silo_nome',
                                             'endereco', 'capacidade', 'data_hora_registro', 'umidade',
                                             'temperatura', 'ph', 'observacoes'])
            if df.empty:
                print("Não há registros.")
            else:
                print(df)
    except oracledb.DatabaseError as Error:
        print(f"Erro ao ler registros: {Error}")

# Função para buscar registro por ID
def get(id: int) -> None:
    print(f"----- CONSULTAR SILO (ID: {id}) -----\n")
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM SILOS WHERE id = {id}")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['id', 'nome_produto', 'tipo_produto', 'quantidade', 'silo_nome',
                                             'endereco', 'capacidade', 'data_hora_registro', 'umidade',
                                             'temperatura', 'ph', 'observacoes'])
            if df.empty:
                print(f"Não há registro com o ID: {id}")
            else:
                print(df)
    except oracledb.DatabaseError as Error:
        print(f"Erro ao ler registro: {Error}")

# Função para apagar registro por ID
def delete(id: int) -> bool:
    print(f"----- APAGAR SILO (ID: {id}) -----")
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM SILOS WHERE id = :1", (id,))
            conn.commit()
        print("Registro apagado com sucesso!")
        return True
    except oracledb.DatabaseError as Error:
        print(f"Erro ao excluir: {Error}")
        return False

# Função para listar IDs e Nomes dos Silos
def get_id_nome() -> None:
    print("----- LISTAR SILOS (ID e Nome) -----\n")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, silo_nome FROM SILOS")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['id', 'silo_nome'])
            if df.empty:
                print("Não há registros.")
            else:
                print(df)
    except oracledb.DatabaseError as Error:
        print(f"Erro ao ler registros: {Error}")

def gerar_relatorio() -> bool:
    def margem(i: int) -> str:
        retorno = "    "
        for _ in range(0, i):
            retorno += "    "
        return retorno

    def obter_valor_por_tipo(tipo: int) -> float:
        valores_por_tipo = {
            1: 1440.97,  # Milho
            2: 1784.67,  # Soja
            3: 1255.00,  # Arroz
            4: 1432.76,  # Trigo
            5: 3103.00   # Feijão
        }
        return valores_por_tipo.get(tipo, 0)

    def condicao_adequada(tipo: int, valor: float, tipo_validacao: int) -> bool:
        cultura_escolhida = tuple()

        if tipo == 1:
            cultura_escolhida = milho
        elif tipo == 2:
            cultura_escolhida = soja
        elif tipo == 3:
            cultura_escolhida = arroz
        elif tipo == 4:
            cultura_escolhida = trigo
        elif tipo == 5:
            cultura_escolhida = feijao

        if tipo_validacao == 1:
            return cultura_escolhida[3] <= valor <= cultura_escolhida[4]
        elif tipo_validacao == 2:
            return cultura_escolhida[5] <= valor <= cultura_escolhida[6]
        elif tipo_validacao == 3:
            return cultura_escolhida[7] <= valor <= cultura_escolhida[8]

    try:
        diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
        caminho = os.path.join(diretorio_raiz, 'arquivos', 'relatorio.txt')

        with open(caminho, "w") as arq:
            arq.seek(0)
            texto = "Relatório dos silos: \n\n"

            texto += margem(0) + "* Listagem de silos:\n"

            lista_silos = list()
            leitura = "SELECT * FROM SILOS"

            with conn.cursor() as cursor:
                cursor.execute(leitura)
                data = cursor.fetchall()

            for dt in data:
                lista_silos.append(dt)

            df = pd.DataFrame(lista_silos, columns=['id', 'nome_produto', 'tipo_produto', 'quantidade', 'silo_nome',
                                                    'endereco', 'capacidade', 'data_hora_registro', 'umidade',
                                                    'temperatura', 'ph', 'observacoes'])

            if df.empty:
                texto += "Não há registros no banco de dados\n"
            else:
                texto += df.to_string() + "\n\n"

                texto += margem(0) + "* Valor total em mercadorias: R$" + str((df['quantidade'] * df['tipo_produto'].apply(obter_valor_por_tipo)).sum()) + "\n\n"

                texto += margem(0) + "* Silos com umidade inadequada:\n"
                for _, linha in df.iterrows():
                    if not condicao_adequada(linha['tipo_produto'], linha['umidade'], 1):
                        texto += margem(1) + "* " + linha['silo_nome'] + "\n"

                texto += margem(0) + "* Silos com temperatura inadequada:\n"
                for _, linha in df.iterrows():
                    if not condicao_adequada(linha['tipo_produto'], linha['temperatura'], 2):
                        texto += margem(1) + "* " + linha['silo_nome'] + "\n"

                texto += margem(0) + "* Silos com pH inadequado:\n"
                for _, linha in df.iterrows():
                    if not condicao_adequada(linha['tipo_produto'], linha['ph'], 3):
                        texto += margem(1) + "* " + linha['silo_nome'] + "\n"

            arq.write(texto)

        print("Relatório gerado com sucesso!")
        return True

    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
        return False
    except IOError as e:
        print(f"Erro de entrada/saída: {e}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return False

# Função de backup
def backup():
    print("----- BACKUP -----\n")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM SILOS")
            data = cursor.fetchall()

            # Capturar dinamicamente os nomes das colunas
            colunas = [desc[0] for desc in cursor.description]
            print(f"Colunas retornadas: {colunas}")  # Verificar as colunas

            # Criar DataFrame com base nas colunas retornadas
            df = pd.DataFrame(data, columns=colunas)

            # Verificar se a coluna 'DATA_HORA_REGISTRO' existe antes de convertê-la
            if 'DATA_HORA_REGISTRO' in df.columns:
                # Converter os campos datetime (Timestamp) para string ISO
                df['DATA_HORA_REGISTRO'] = df['DATA_HORA_REGISTRO'].apply(
                    lambda x: x.isoformat() if isinstance(x, datetime) else x
                )

            # Converter DataFrame para lista de dicionários
            backup_data = df.to_dict(orient='records')

            # Caminho para salvar o arquivo backup.json
            caminho = Path(__file__).parent / 'arquivos' / 'backup.json'
            caminho.parent.mkdir(parents=True, exist_ok=True)  # Criar diretório se não existir

            # Salvar dados no arquivo JSON
            with open(caminho, 'w') as f:
                json.dump(backup_data, f, indent=4)

            print("Backup realizado com sucesso!")

    except Exception as e:
        print(f"Erro durante o backup: {e}")


# Função para restaurar backup
def restaurar_backup():
    print("----- RESTAURAR BACKUP -----\n")
    try:
        # Definir o caminho para o backup
        caminho = Path(__file__).parent / 'arquivos' / 'backup.json'

        # Verificar se o arquivo de backup existe
        if not caminho.exists():
            raise FileNotFoundError("Arquivo de backup não encontrado.")

        # Carregar o conteúdo do arquivo JSON
        with open(caminho, "r") as arquivo_json:
            lista_dicionarios = json.load(arquivo_json)

        # Verificar se o arquivo contém dados
        if not lista_dicionarios:
            raise ValueError("O arquivo de backup está vazio ou os dados estão mal formatados.")

        # Iniciar a transação de restauração
        with conn.cursor() as cursor:
            for registro in lista_dicionarios:
                # Certificar-se de que todos os campos estão presentes no registro, exceto 'ID'
                required_keys = ['NOME_PRODUTO', 'TIPO_PRODUTO', 'QUANTIDADE', 'SILO_NOME', 'ENDERECO',
                                 'CAPACIDADE', 'DATA_HORA_REGISTRO', 'UMIDADE', 'TEMPERATURA', 'PH', 'OBSERVACOES']

                # Filtrar o registro para remover o campo 'ID' e garantir que os campos necessários estejam presentes
                registro_filtrado = {key: registro[key] for key in required_keys if key in registro}

                # Verificar se o registro contém todos os campos necessários
                if len(registro_filtrado) != len(required_keys):
                    raise ValueError(f"Registro incompleto encontrado: {registro}")

                # Preparar a consulta com os 11 valores (excluindo o 'ID')
                consulta = """
                    INSERT INTO SILOS (NOME_PRODUTO, TIPO_PRODUTO, QUANTIDADE, SILO_NOME, ENDERECO, CAPACIDADE, 
                                       DATA_HORA_REGISTRO, UMIDADE, TEMPERATURA, PH, OBSERVACOES) 
                    VALUES (:1, :2, :3, :4, :5, :6, TO_DATE(:7, 'YYYY-MM-DD"T"HH24:MI:SS'), :8, :9, :10, :11)
                """
                # Executar a consulta SQL para cada registro
                cursor.execute(consulta, (
                    registro_filtrado['NOME_PRODUTO'], registro_filtrado['TIPO_PRODUTO'],
                    registro_filtrado['QUANTIDADE'], registro_filtrado['SILO_NOME'],
                    registro_filtrado['ENDERECO'], registro_filtrado['CAPACIDADE'],
                    registro_filtrado['DATA_HORA_REGISTRO'], registro_filtrado['UMIDADE'],
                    registro_filtrado['TEMPERATURA'], registro_filtrado['PH'],
                    registro_filtrado['OBSERVACOES']
                ))

            # Confirmar a transação no banco de dados
            conn.commit()

        print("Backup restaurado com sucesso!")

    except (FileNotFoundError, ValueError) as e:
        print(f"Erro: {e}")
    except oracledb.DatabaseError as e:
        print(f"Erro no banco de dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

