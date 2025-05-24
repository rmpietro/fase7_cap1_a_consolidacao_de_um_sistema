import streamlit as st
import pandas as pd
import sys
import os
import json
import oracledb
import requests
from datetime import datetime, date
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# Adicionar diretório pai ao PYTHONPATH
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent.parent
fase3_dir = root_dir / "src" / "fase3" / "src"

if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
if str(fase3_dir) not in sys.path:
    sys.path.append(str(fase3_dir))

# Adicionar import boto3 para integração AWS SNS
try:
    import boto3
except ImportError:
    boto3 = None

# Configuração da página
st.set_page_config(
    page_title="Sistema de Monitoramento de Culturas",
    page_icon="🌱",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #228B22;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #32CD32;
        border-bottom: 2px solid #90EE90;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    .metric-container {
        background-color: #F0FFF0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #32CD32;
    }
    .info-box {
        background-color: #E6F3FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #007BFF;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3CD;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFC107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D4EDDA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28A745;
        margin: 1rem 0;
    }
    .status-connected {
        color: #28A745;
        font-weight: bold;
    }
    .status-disconnected {
        color: #DC3545;
        font-weight: bold;
    }
    .sensor-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #DEE2E6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Estado da sessão para conexão com banco
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'user_credentials' not in st.session_state:
    st.session_state.user_credentials = {'username': '', 'password': ''}
if 'tables_created' not in st.session_state:
    st.session_state.tables_created = False
if 'data_imported' not in st.session_state:
    st.session_state.data_imported = False

# Funções do banco de dados
def connect_database(username, password):
    """Conectar ao banco de dados Oracle"""
    try:
        conn = oracledb.connect(user=username, password=password, dsn='oracle.fiap.com.br:1521/ORCL')
        st.session_state.db_connection = conn
        st.session_state.db_connected = True
        st.session_state.user_credentials = {'username': username, 'password': password}
        return True
    except oracledb.DatabaseError as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        st.session_state.db_connected = False
        return False

def close_connection():
    """Fechar conexão com banco"""
    if st.session_state.db_connection:
        try:
            st.session_state.db_connection.close()
            st.session_state.db_connected = False
            st.session_state.db_connection = None
        except Exception as e:
            st.error(f"Erro ao fechar conexão: {e}")

def check_tables_exist():
    """Verificar se as tabelas existem"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM user_tables 
                WHERE table_name IN ('AREA_CULTIVO', 'LEITURAS', 'SENSOR', 'TIPO_CULTURA')
            """)
            return cursor.fetchone()[0] == 4
    except Exception as e:
        st.error(f"Erro ao verificar tabelas: {e}")
        return False

def create_tables():
    """Criar tabelas no banco de dados"""
    try:
        if check_tables_exist():
            st.info("📋 Estrutura de banco de dados já existe.")
            st.session_state.tables_created = True
            return True
        
        ddl_commands = """
        CREATE TABLE tipo_cultura (
            id_cultura NUMBER PRIMARY KEY,
            nome VARCHAR2(50),
            data_plantio DATE
        );
        
        CREATE TABLE area_cultivo (
            id_area NUMBER PRIMARY KEY,
            id_cultura NUMBER,
            area_extensao NUMBER(10, 2),
            end_localizacao VARCHAR2(100),
            FOREIGN KEY (id_cultura) REFERENCES tipo_cultura(id_cultura)
        );
        
        CREATE TABLE sensor (
            id_sensor NUMBER PRIMARY KEY,
            id_area NUMBER,
            descricao VARCHAR2(100),
            tipo VARCHAR2(50),
            modelo VARCHAR2(50),
            FOREIGN KEY (id_area) REFERENCES area_cultivo(id_area)
        );
        
        CREATE TABLE leituras (
            id_leitura NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            timestamp TIMESTAMP,
            temp NUMBER(5, 2),
            humid NUMBER(5, 2),
            P VARCHAR2(20),
            K VARCHAR2(20),
            pH NUMBER(5, 2),
            estado_irrigacao VARCHAR2(20),
            motivo_irrigacao VARCHAR2(255),
            id_sensor NUMBER,
            FOREIGN KEY (id_sensor) REFERENCES sensor(id_sensor)
        )
        """
        
        ddl_blocks = [block.strip() for block in ddl_commands.split(';') if block.strip()]
        
        with st.session_state.db_connection.cursor() as cursor:
            for block in ddl_blocks:
                cursor.execute(block)
        
        st.session_state.db_connection.commit()
        st.success("✅ Todas as tabelas foram criadas com sucesso!")
        st.session_state.tables_created = True
        return True
        
    except oracledb.DatabaseError as e:
        st.error(f"❌ Erro ao criar tabelas: {e}")
        return False

def check_data_exists():
    """Verificar se dados já foram importados"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM LEITURAS")
            return cursor.fetchone()[0] > 0
    except Exception:
        return False

def import_json_data():
    """Importar dados do JSON para o banco"""
    try:
        if check_data_exists():
            st.info("📋 Dados já foram importados anteriormente.")
            st.session_state.data_imported = True
            return True
        
        # Dados JSON embutidos (simulando o arquivo dados_app.json)
        json_data = {
            "tipo_cultura": [
                {"id_cultura": 1, "nome": "Soja", "data_plantio": "2024-03-15"},
                {"id_cultura": 2, "nome": "Milho", "data_plantio": "2024-02-20"}
            ],
            "area_cultivo": [
                {"id_area": 1, "id_cultura": 1, "area_extensao": 150.50, "end_localizacao": "Setor A - Fazenda Sao Joao"},
                {"id_area": 2, "id_cultura": 2, "area_extensao": 200.75, "end_localizacao": "Setor B - Fazenda Sao Joao"}
            ],
            "sensor": [
                {"id_sensor": 1, "id_area": 1, "descricao": "Sensor de umidade do solo", "tipo": "Umidade", "modelo": "DHT22"},
                {"id_sensor": 2, "id_area": 1, "descricao": "Sensor de temperatura", "tipo": "Temperatura", "modelo": "DHT22"},
                {"id_sensor": 3, "id_area": 1, "descricao": "Sensor de nutriente P", "tipo": "Sensor P", "modelo": "Sensor P"},
                {"id_sensor": 4, "id_area": 1, "descricao": "Sensor de nutriente K", "tipo": "Sensor K", "modelo": "Sensor K"},
                {"id_sensor": 5, "id_area": 1, "descricao": "Sensor de pH do solo", "tipo": "Sensor pH", "modelo": "LDR Adaptado"}
            ],
            "leituras": [[
                {"timestamp": "2024-11-12T10:30:00", "temp": 28.40, "humid": 60.0, "P": "presente", "K": "presente", "pH": 6.76, 
                 "irrigacao": {"estado": "desligada", "motivo": "Solo suficientemente umido com nutrientes e temperatura adequada."}},
                {"timestamp": "2024-11-12T10:00:00", "temp": 29.50, "humid": 62.0, "P": "presente", "K": "presente", "pH": 7.0, 
                 "irrigacao": {"estado": "desligada", "motivo": "Solo suficientemente umido com nutrientes e temperatura adequada."}},
                {"timestamp": "2024-11-11T10:00:00", "temp": 37.20, "humid": 59.5, "P": "presente", "K": "presente", "pH": 6.76, 
                 "irrigacao": {"estado": "ligada", "motivo": "Solo umido com temperatura alta."}},
                {"timestamp": "2024-11-10T10:00:00", "temp": 36.50, "humid": 57.5, "P": "presente", "K": "presente", "pH": 6.9, 
                 "irrigacao": {"estado": "ligada", "motivo": "Solo umido com temperatura alta."}},
                {"timestamp": "2024-10-30T09:30:00", "temp": 28.10, "humid": 51.5, "P": "presente", "K": "presente", "pH": 6.8, 
                 "irrigacao": {"estado": "ligada", "motivo": "Solo seco, pouca humidade."}},
                {"timestamp": "2024-10-30T09:00:00", "temp": 28.10, "humid": 49.9, "P": "presente", "K": "presente", "pH": 6.96, 
                 "irrigacao": {"estado": "ligada", "motivo": "Solo seco, pouca humidade."}},
                {"timestamp": "2024-10-29T08:00:00", "temp": 30.00, "humid": 60.0, "P": "presente", "K": "nao-presente", "pH": 7.78, 
                 "irrigacao": {"estado": "ligada", "motivo": "pH basico e nutrientes ausentes no solo."}},
                {"timestamp": "2024-10-29T08:15:00", "temp": 30.50, "humid": 61.5, "P": "nao-presente", "K": "nao-presente", "pH": 7.98, 
                 "irrigacao": {"estado": "ligada", "motivo": "pH basico e nutrientes ausentes no solo."}}
            ]]
        }
        
        with st.session_state.db_connection.cursor() as cursor:
            # Inserir tipos de cultura
            for cultura in json_data["tipo_cultura"]:
                cursor.execute("""
                    INSERT INTO tipo_cultura (id_cultura, nome, data_plantio)
                    VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
                """, [cultura["id_cultura"], cultura["nome"], cultura["data_plantio"]])
            
            # Inserir áreas de cultivo
            for area in json_data["area_cultivo"]:
                cursor.execute("""
                    INSERT INTO area_cultivo (id_area, id_cultura, area_extensao, end_localizacao)
                    VALUES (:1, :2, :3, :4)
                """, [area["id_area"], area["id_cultura"], area["area_extensao"], area["end_localizacao"]])
            
            # Inserir sensores
            for sensor in json_data["sensor"]:
                cursor.execute("""
                    INSERT INTO sensor (id_sensor, id_area, descricao, tipo, modelo)
                    VALUES (:1, :2, :3, :4, :5)
                """, [sensor["id_sensor"], sensor["id_area"], sensor["descricao"], sensor["tipo"], sensor["modelo"]])
            
            # Inserir leituras
            for leitura_list in json_data["leituras"]:
                for leitura in leitura_list:
                    cursor.execute("""
                        INSERT INTO leituras (timestamp, temp, humid, P, K, pH, estado_irrigacao, motivo_irrigacao, id_sensor)
                        VALUES (TO_TIMESTAMP(:1, 'YYYY-MM-DD"T"HH24:MI:SS'), :2, :3, :4, :5, :6, :7, :8, :9)
                    """, [leitura["timestamp"], leitura["temp"], leitura["humid"], leitura["P"], leitura["K"], 
                         leitura["pH"], leitura["irrigacao"]["estado"], leitura["irrigacao"]["motivo"], 1])
        
        st.session_state.db_connection.commit()
        st.success("✅ Dados importados com sucesso!")
        st.session_state.data_imported = True
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao importar dados: {e}")
        return False

def get_weather_forecast():
    """Obter previsão de chuva para Presidente Prudente"""
    try:
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': -22.1256,
            'lon': -51.3889,
            'appid': "48380355e6896ab9c1318bc85deca9c3",
            'units': 'metric',
            'cnt': 5
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        forecast_data = []
        for item in data['list']:
            data_hora = item['dt_txt']
            chuva = item.get('rain', {}).get('3h', 0)
            temp = item['main']['temp']
            humidity = item['main']['humidity']
            
            forecast_data.append({
                "Data e Hora": data_hora,
                "Temperatura (°C)": temp,
                "Umidade (%)": humidity,
                "Previsão de Chuva (mm)": chuva
            })
        
        return pd.DataFrame(forecast_data)
        
    except Exception as e:
        st.error(f"❌ Erro ao obter previsão meteorológica: {e}")
        return pd.DataFrame()

def get_table_data(table_name):
    """Buscar dados de uma tabela"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(data, columns=columns)
    except Exception as e:
        st.error(f"Erro ao buscar dados da tabela {table_name}: {e}")
        return pd.DataFrame()

def insert_tipo_cultura(id_cultura, nome, data_plantio):
    """Inserir tipo de cultura"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tipo_cultura (id_cultura, nome, data_plantio)
                VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
            """, [id_cultura, nome, data_plantio.strftime('%Y-%m-%d')])
            st.session_state.db_connection.commit()
        return True, "Tipo de cultura criado com sucesso!"
    except Exception as e:
        return False, f"Erro ao criar tipo de cultura: {e}"

def insert_area_cultivo(id_area, id_cultura, area_extensao, end_localizacao):
    """Inserir área de cultivo"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO area_cultivo (id_area, id_cultura, area_extensao, end_localizacao)
                VALUES (:1, :2, :3, :4)
            """, [id_area, id_cultura, area_extensao, end_localizacao])
            st.session_state.db_connection.commit()
        return True, "Área de cultivo criada com sucesso!"
    except Exception as e:
        return False, f"Erro ao criar área de cultivo: {e}"

def insert_sensor(id_sensor, id_area, descricao, tipo, modelo):
    """Inserir sensor"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sensor (id_sensor, id_area, descricao, tipo, modelo)
                VALUES (:1, :2, :3, :4, :5)
            """, [id_sensor, id_area, descricao, tipo, modelo])
            st.session_state.db_connection.commit()
        return True, "Sensor criado com sucesso!"
    except Exception as e:
        return False, f"Erro ao criar sensor: {e}"

def insert_leitura(timestamp, temp, humid, p, k, ph, estado_irrigacao, motivo_irrigacao, id_sensor):
    """Inserir leitura"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO leituras (timestamp, temp, humid, P, K, pH, estado_irrigacao, motivo_irrigacao, id_sensor)
                VALUES (TO_TIMESTAMP(:1, 'YYYY-MM-DD HH24:MI:SS'), :2, :3, :4, :5, :6, :7, :8, :9)
            """, [timestamp.strftime('%Y-%m-%d %H:%M:%S'), temp, humid, p, k, ph, estado_irrigacao, motivo_irrigacao, id_sensor])
            st.session_state.db_connection.commit()
        # Enviar alerta SNS após inserir leitura
        if boto3 is not None:
            try:
                sns = boto3.client(
                    'sns',
                    region_name=AWS_REGION,
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY
                )
                mensagem = (
                    f"Nova leitura registrada:\n"
                    f"Data/Hora: {timestamp}\n"
                    f"Sensor: {id_sensor}\n"
                    f"Temperatura: {temp}°C\n"
                    f"Umidade: {humid}%\n"
                    f"pH: {ph}\n"
                    f"P: {p}, K: {k}\n"
                    f"Irrigação: {estado_irrigacao}\n"
                    f"Motivo: {motivo_irrigacao}"
                )
                sns.publish(
                    TopicArn='arn:aws:sns:us-east-1:102792232287:alerta-sensor-fase3',
                    Message=mensagem,
                    Subject='Nova leitura de sensor registrada'
                )
            except Exception as e:
                st.warning(f'Leitura registrada, mas não foi possível enviar alerta SNS: {e}')
        return True, "Leitura criada com sucesso!"
    except Exception as e:
        return False, f"Erro ao criar leitura: {e}"

# Header principal
st.markdown('<h1 class="main-header">🌱 Fase 3 - Máquina Agrícola - Monitoramento de Culturas</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Controle Inteligente de Agricultura</h2>', unsafe_allow_html=True)

# Status da conexão
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.session_state.db_connected:
        st.markdown('<p class="status-connected">🟢 Conectado ao Banco de Dados</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-disconnected">🔴 Desconectado do Banco de Dados</p>', unsafe_allow_html=True)

with col2:
    if st.session_state.db_connected and st.button("🔌 Desconectar"):
        close_connection()
        st.rerun()

with col3:
    if st.button("🔄 Reconectar"):
        if st.session_state.user_credentials['username']:
            connect_database(st.session_state.user_credentials['username'], 
                           st.session_state.user_credentials['password'])
            st.rerun()

# Tela de login se não conectado
if not st.session_state.db_connected:
    st.markdown("""
    <div class="info-box">
        <h4>🔐 Credenciais de Acesso</h4>
        <p>Para começar, informe suas credenciais de acesso ao banco de dados Oracle da FIAP:</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("👤 Usuário (RMXXXXXX)", value=st.session_state.user_credentials['username'])
        password = st.text_input("🔑 Senha", type="password")
        
        if st.form_submit_button("🔐 Conectar ao Banco", use_container_width=True):
            if username and password:
                if connect_database(username, password):
                    st.success("✅ Conectado com sucesso!")
                    st.rerun()
            else:
                st.error("❌ Por favor, informe usuário e senha.")

else:
    # Menu principal
    st.sidebar.title("🌱 Menu do Sistema")
    menu_options = [
        "🏠 Dashboard",
        "🗃️ Gerenciar Banco de Dados",
        "📊 Visualizar Dados",
        "➕ Inserir Dados",
        "🌤️ Previsão Meteorológica"
    ]
    
    selected_option = st.sidebar.selectbox("Selecione uma opção:", menu_options)
    
    # Conteúdo baseado na seleção
    if selected_option == "🏠 Dashboard":
        st.markdown('<h2 class="section-header">📊 Dashboard do Sistema</h2>', unsafe_allow_html=True)
        
        # Verificar status do sistema
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tables_exist = check_tables_exist()
            status = "✅ Criadas" if tables_exist else "❌ Não criadas"
            st.metric("🗃️ Tabelas", status)
        
        with col2:
            data_exists = check_data_exists()
            status = "✅ Importados" if data_exists else "❌ Não importados"
            st.metric("📦 Dados", status)
        
        with col3:
            if tables_exist:
                df_culturas = get_table_data("TIPO_CULTURA")
                st.metric("🌾 Culturas", len(df_culturas))
            else:
                st.metric("🌾 Culturas", "N/A")
        
        with col4:
            if tables_exist:
                df_sensores = get_table_data("SENSOR")
                st.metric("📡 Sensores", len(df_sensores))
            else:
                st.metric("📡 Sensores", "N/A")
        
        # Gráficos e dados recentes
        if tables_exist and data_exists:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Leituras Recentes de Temperatura")
                df_leituras = get_table_data("LEITURAS")
                if not df_leituras.empty:
                    df_temp = df_leituras.sort_values('TIMESTAMP').tail(10)
                    fig = px.line(df_temp, x='TIMESTAMP', y='TEMP', 
                                title="Temperatura ao Longo do Tempo")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 💧 Leituras Recentes de Umidade")
                if not df_leituras.empty:
                    df_humid = df_leituras.sort_values('TIMESTAMP').tail(10)
                    fig = px.line(df_humid, x='TIMESTAMP', y='HUMID', 
                                title="Umidade ao Longo do Tempo", 
                                line_shape='spline')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Status de irrigação
            st.markdown("### 💦 Status Atual de Irrigação")
            if not df_leituras.empty:
                ultima_leitura = df_leituras.sort_values('TIMESTAMP').iloc[-1]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_cor = "🟢" if ultima_leitura['ESTADO_IRRIGACAO'] == 'ligada' else "🔴"
                    st.metric("💦 Irrigação", f"{status_cor} {ultima_leitura['ESTADO_IRRIGACAO'].title()}")
                
                with col2:
                    st.metric("🌡️ Temperatura", f"{ultima_leitura['TEMP']}°C")
                
                with col3:
                    st.metric("💧 Umidade", f"{ultima_leitura['HUMID']}%")
                
                st.info(f"💡 **Motivo:** {ultima_leitura['MOTIVO_IRRIGACAO']}")
        else:
            st.warning("⚠️ Configure o banco de dados e importe os dados para ver o dashboard completo.")
    
    elif selected_option == "🗃️ Gerenciar Banco de Dados":
        st.markdown('<h2 class="section-header">🗃️ Gerenciamento do Banco de Dados</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🏗️ Criar Tabelas", "📥 Importar Dados"])
        
        with tab1:
            st.markdown("### 🏗️ Criação de Tabelas")
            
            if check_tables_exist():
                st.success("✅ Todas as tabelas já existem no banco de dados!")
                
                # Mostrar estrutura das tabelas
                st.markdown("#### 📋 Estrutura das Tabelas:")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **🌾 TIPO_CULTURA**
                    - ID_CULTURA (NUMBER)
                    - NOME (VARCHAR2)
                    - DATA_PLANTIO (DATE)
                    """)
                    
                    st.markdown("""
                    **🏞️ AREA_CULTIVO**
                    - ID_AREA (NUMBER)
                    - ID_CULTURA (NUMBER)
                    - AREA_EXTENSAO (NUMBER)
                    - END_LOCALIZACAO (VARCHAR2)
                    """)
                
                with col2:
                    st.markdown("""
                    **📡 SENSOR**
                    - ID_SENSOR (NUMBER)
                    - ID_AREA (NUMBER)
                    - DESCRICAO (VARCHAR2)
                    - TIPO (VARCHAR2)
                    - MODELO (VARCHAR2)
                    """)
                    
                    st.markdown("""
                    **📊 LEITURAS**
                    - ID_LEITURA (NUMBER)
                    - TIMESTAMP (TIMESTAMP)
                    - TEMP, HUMID, P, K, pH
                    - ESTADO_IRRIGACAO, MOTIVO_IRRIGACAO
                    - ID_SENSOR (NUMBER)
                    """)
            else:
                st.info("ℹ️ As tabelas ainda não foram criadas no banco de dados.")
                
                if st.button("🏗️ Criar Tabelas", use_container_width=True, type="primary"):
                    with st.spinner("⏳ Criando tabelas..."):
                        if create_tables():
                            st.rerun()
        
        with tab2:
            st.markdown("### 📥 Importação de Dados")
            
            if not check_tables_exist():
                st.error("❌ Crie as tabelas primeiro antes de importar os dados.")
            elif check_data_exists():
                st.success("✅ Dados já foram importados anteriormente!")
                
                # Mostrar estatísticas dos dados
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    df_culturas = get_table_data("TIPO_CULTURA")
                    st.metric("🌾 Culturas", len(df_culturas))
                
                with col2:
                    df_areas = get_table_data("AREA_CULTIVO")
                    st.metric("🏞️ Áreas", len(df_areas))
                
                with col3:
                    df_sensores = get_table_data("SENSOR")
                    st.metric("📡 Sensores", len(df_sensores))
                
                with col4:
                    df_leituras = get_table_data("LEITURAS")
                    st.metric("📊 Leituras", len(df_leituras))
            else:
                st.info("ℹ️ Os dados ainda não foram importados.")
                
                st.markdown("""
                <div class="info-box">
                    <h4>📋 Dados a serem Importados</h4>
                    <ul>
                        <li><strong>Tipos de Cultura:</strong> Soja e Milho</li>
                        <li><strong>Áreas de Cultivo:</strong> 2 setores da Fazenda São João</li>
                        <li><strong>Sensores:</strong> 5 sensores (umidade, temperatura, P, K, pH)</li>
                        <li><strong>Leituras:</strong> Dados históricos de monitoramento</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📥 Importar Dados do JSON", use_container_width=True, type="primary"):
                    with st.spinner("⏳ Importando dados..."):
                        if import_json_data():
                            st.rerun()
    
    elif selected_option == "📊 Visualizar Dados":
        st.markdown('<h2 class="section-header">📊 Visualização de Dados</h2>', unsafe_allow_html=True)
        
        if not check_tables_exist():
            st.error("❌ Crie as tabelas primeiro.")
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["🌾 Culturas", "🏞️ Áreas", "📡 Sensores", "📊 Leituras"])
            
            with tab1:
                st.markdown("### 🌾 Tipos de Cultura")
                df_culturas = get_table_data("TIPO_CULTURA")
                if not df_culturas.empty:
                    st.dataframe(df_culturas.reset_index(drop=True), use_container_width=True)
                else:
                    st.info("ℹ️ Nenhuma cultura cadastrada.")
            
            with tab2:
                st.markdown("### 🏞️ Áreas de Cultivo")
                df_areas = get_table_data("AREA_CULTIVO")
                if not df_areas.empty:
                    st.dataframe(df_areas.reset_index(drop=True), use_container_width=True)
                    
                    # Gráfico de área por cultura
                    if len(df_areas) > 0:
                        fig = px.bar(df_areas, x='ID_AREA', y='AREA_EXTENSAO', 
                                   title="Extensão das Áreas de Cultivo")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ Nenhuma área cadastrada.")
            
            with tab3:
                st.markdown("### 📡 Sensores")
                df_sensores = get_table_data("SENSOR")
                if not df_sensores.empty:
                    st.dataframe(df_sensores.reset_index(drop=True), use_container_width=True)
                    
                    # Distribuição por tipo de sensor
                    if len(df_sensores) > 0:
                        tipo_count = df_sensores['TIPO'].value_counts()
                        fig = px.pie(values=tipo_count.values, names=tipo_count.index,
                                   title="Distribuição de Sensores por Tipo")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ Nenhum sensor cadastrado.")
            
            with tab4:
                st.markdown("### 📊 Leituras dos Sensores")
                df_leituras = get_table_data("LEITURAS")
                if not df_leituras.empty:
                    st.dataframe(df_leituras.reset_index(drop=True), use_container_width=True)
                    
                    # Gráficos de análise
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.scatter(df_leituras, x='TEMP', y='HUMID', 
                                       color='ESTADO_IRRIGACAO',
                                       title="Relação Temperatura x Umidade")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.histogram(df_leituras, x='PH', 
                                         title="Distribuição de pH")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Status de irrigação
                    irrigacao_count = df_leituras['ESTADO_IRRIGACAO'].value_counts()
                    fig = px.pie(values=irrigacao_count.values, names=irrigacao_count.index,
                               title="Status de Irrigação")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ Nenhuma leitura registrada.")
    
    elif selected_option == "➕ Inserir Dados":
        st.markdown('<h2 class="section-header">➕ Inserção de Dados</h2>', unsafe_allow_html=True)
        
        if not check_tables_exist():
            st.error("❌ Crie as tabelas primeiro.")
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["🌾 Nova Cultura", "🏞️ Nova Área", "📡 Novo Sensor", "📊 Nova Leitura"])
            
            with tab1:
                st.markdown("### 🌾 Cadastrar Tipo de Cultura")
                
                with st.form("form_cultura"):
                    id_cultura = st.number_input("🆔 ID da Cultura", min_value=1, step=1)
                    nome = st.text_input("🌾 Nome da Cultura")
                    data_plantio = st.date_input("📅 Data de Plantio", value=date.today())
                    
                    if st.form_submit_button("💾 Cadastrar Cultura", use_container_width=True):
                        if nome.strip():
                            success, message = insert_tipo_cultura(id_cultura, nome, data_plantio)
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Nome da cultura é obrigatório.")
            
            with tab2:
                st.markdown("### 🏞️ Cadastrar Área de Cultivo")
                
                # Buscar culturas disponíveis
                df_culturas = get_table_data("TIPO_CULTURA")
                
                if df_culturas.empty:
                    st.warning("⚠️ Cadastre pelo menos uma cultura primeiro.")
                else:
                    with st.form("form_area"):
                        id_area = st.number_input("🆔 ID da Área", min_value=1, step=1)
                        id_cultura = st.selectbox("🌾 Cultura", 
                                                options=df_culturas['ID_CULTURA'].tolist(),
                                                format_func=lambda x: f"{x} - {df_culturas[df_culturas['ID_CULTURA']==x]['NOME'].iloc[0]}")
                        area_extensao = st.number_input("📐 Área (hectares)", min_value=0.0, step=0.1)
                        end_localizacao = st.text_input("📍 Localização")
                        
                        if st.form_submit_button("💾 Cadastrar Área", use_container_width=True):
                            if end_localizacao.strip() and area_extensao > 0:
                                success, message = insert_area_cultivo(id_area, id_cultura, area_extensao, end_localizacao)
                                if success:
                                    st.success(f"✅ {message}")
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.error("❌ Preencha todos os campos obrigatórios.")
            
            with tab3:
                st.markdown("### 📡 Cadastrar Sensor")
                
                # Buscar áreas disponíveis
                df_areas = get_table_data("AREA_CULTIVO")
                
                if df_areas.empty:
                    st.warning("⚠️ Cadastre pelo menos uma área primeiro.")
                else:
                    with st.form("form_sensor"):
                        id_sensor = st.number_input("🆔 ID do Sensor", min_value=1, step=1)
                        id_area = st.selectbox("🏞️ Área", 
                                             options=df_areas['ID_AREA'].tolist(),
                                             format_func=lambda x: f"{x} - {df_areas[df_areas['ID_AREA']==x]['END_LOCALIZACAO'].iloc[0]}")
                        descricao = st.text_input("📝 Descrição")
                        tipo = st.selectbox("🔧 Tipo", ["Umidade", "Temperatura", "Sensor P", "Sensor K", "Sensor pH"])
                        modelo = st.text_input("🏷️ Modelo")
                        
                        if st.form_submit_button("💾 Cadastrar Sensor", use_container_width=True):
                            if all([descricao.strip(), modelo.strip()]):
                                success, message = insert_sensor(id_sensor, id_area, descricao, tipo, modelo)
                                if success:
                                    st.success(f"✅ {message}")
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.error("❌ Preencha todos os campos obrigatórios.")
            
            with tab4:
                st.markdown("### 📊 Registrar Leitura")
                
                # Buscar sensores disponíveis
                df_sensores = get_table_data("SENSOR")
                
                if df_sensores.empty:
                    st.warning("⚠️ Cadastre pelo menos um sensor primeiro.")
                else:
                    with st.form("form_leitura"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            data_leitura = st.date_input("📅 Data da Leitura", value=date.today())
                            hora_leitura = st.time_input("🕐 Hora da Leitura", value=datetime.now().time())
                            # Combinar data e hora em datetime
                            timestamp = datetime.combine(data_leitura, hora_leitura)
                            
                            id_sensor = st.selectbox("📡 Sensor", 
                                                   options=df_sensores['ID_SENSOR'].tolist(),
                                                   format_func=lambda x: f"{x} - {df_sensores[df_sensores['ID_SENSOR']==x]['DESCRICAO'].iloc[0]}")
                            temp = st.number_input("🌡️ Temperatura (°C)", min_value=-10.0, max_value=50.0, step=0.1)
                            humid = st.number_input("💧 Umidade (%)", min_value=0.0, max_value=100.0, step=0.1)
                            ph = st.number_input("⚗️ pH", min_value=0.0, max_value=14.0, step=0.1)
                        
                        with col2:
                            p = st.selectbox("🧪 Fósforo (P)", ["presente", "nao-presente"])
                            k = st.selectbox("🧪 Potássio (K)", ["presente", "nao-presente"])
                            estado_irrigacao = st.selectbox("💦 Estado Irrigação", ["ligada", "desligada"])
                            motivo_irrigacao = st.text_area("💡 Motivo da Irrigação")
                        
                        if st.form_submit_button("💾 Registrar Leitura", use_container_width=True):
                            if motivo_irrigacao.strip():
                                success, message = insert_leitura(timestamp, temp, humid, p, k, ph, 
                                                                 estado_irrigacao, motivo_irrigacao, id_sensor)
                                if success:
                                    st.success(f"✅ {message}")
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.error("❌ Motivo da irrigação é obrigatório.")
    
    elif selected_option == "🌤️ Previsão Meteorológica":
        st.markdown('<h2 class="section-header">🌤️ Previsão Meteorológica</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h4>🌍 Previsão para Presidente Prudente - SP</h4>
            <p>Dados meteorológicos em tempo real para auxiliar no monitoramento das culturas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Obter Previsão Meteorológica", use_container_width=True, type="primary"):
            with st.spinner("⏳ Buscando dados meteorológicos..."):
                df_weather = get_weather_forecast()
                
                if not df_weather.empty:
                    st.success("✅ Previsão meteorológica obtida com sucesso!")
                    
                    st.markdown("### 📊 Dados Meteorológicos")
                    st.dataframe(df_weather.reset_index(drop=True), use_container_width=True)
                    
                    # Gráficos
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.line(df_weather, x='Data e Hora', y='Temperatura (°C)',
                                    title="🌡️ Previsão de Temperatura")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(df_weather, x='Data e Hora', y='Previsão de Chuva (mm)',
                                   title="🌧️ Previsão de Chuva")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Resumo
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        temp_media = df_weather['Temperatura (°C)'].mean()
                        st.metric("🌡️ Temp. Média", f"{temp_media:.1f}°C")
                    
                    with col2:
                        chuva_total = df_weather['Previsão de Chuva (mm)'].sum()
                        st.metric("🌧️ Chuva Total", f"{chuva_total:.1f} mm")
                    
                    with col3:
                        umidade_media = df_weather['Umidade (%)'].mean()
                        st.metric("💧 Umid. Média", f"{umidade_media:.1f}%")
