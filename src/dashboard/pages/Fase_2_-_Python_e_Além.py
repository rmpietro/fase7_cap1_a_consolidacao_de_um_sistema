import streamlit as st
import pandas as pd
import sys
import os
import json
import oracledb
from datetime import datetime
from pathlib import Path
import io

# Adicionar diretório pai ao PYTHONPATH
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent.parent
fase2_dir = root_dir / "src" / "fase2" / "src"

if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
if str(fase2_dir) not in sys.path:
    sys.path.append(str(fase2_dir))

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gerenciamento de Silos",
    page_icon="🌾",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #8B4513;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #A0522D;
        border-bottom: 2px solid #DEB887;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    .metric-container {
        background-color: #FFF8DC;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #DAA520;
    }
    .info-box {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4169E1;
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
</style>
""", unsafe_allow_html=True)

# Definição de produtos (conforme o sistema original)
PRODUTOS = {
    1: {"nome": "Milho", "valor": 1440.97, "umidade_min": 13.0, "umidade_max": 14.1, 
        "temp_min": 15.0, "temp_max": 25.1, "ph_min": 6.0, "ph_max": 7.6},
    2: {"nome": "Soja", "valor": 1784.67, "umidade_min": 11.0, "umidade_max": 13.1,
        "temp_min": 15.0, "temp_max": 25.1, "ph_min": 6.0, "ph_max": 7.6},
    3: {"nome": "Arroz", "valor": 1255.00, "umidade_min": 12.0, "umidade_max": 14.1,
        "temp_min": 10.0, "temp_max": 25.1, "ph_min": 6.0, "ph_max": 7.1},
    4: {"nome": "Trigo", "valor": 1432.76, "umidade_min": 12.0, "umidade_max": 14.1,
        "temp_min": 10.0, "temp_max": 25.1, "ph_min": 5.5, "ph_max": 6.6},
    5: {"nome": "Feijão", "valor": 3103.00, "umidade_min": 11.0, "umidade_max": 13.1,
        "temp_min": 15.0, "temp_max": 25.1, "ph_min": 5.8, "ph_max": 6.9}
}

# Estado da sessão para conexão com banco
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'user_credentials' not in st.session_state:
    st.session_state.user_credentials = {'username': '', 'password': ''}

# Funções do banco de dados
def connect_database(username, password):
    """Conectar ao banco de dados Oracle"""
    try:
        oracledb.defaults.fetch_lobs = False
        conn = oracledb.connect(user=username, password=password, dsn='oracle.fiap.com.br:1521/ORCL')
        st.session_state.db_connection = conn
        st.session_state.db_connected = True
        st.session_state.user_credentials = {'username': username, 'password': password}
        
        # Verificar/criar tabela
        check_and_create_table()
        return True
    except oracledb.DatabaseError as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        st.session_state.db_connected = False
        return False

def check_and_create_table():
    """Verificar se a tabela SILOS existe e criá-la se necessário"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = 'SILOS'")
            if cursor.fetchone()[0] == 0:
                # Criar tabela
                create_table_sql = """
                CREATE TABLE SILOS (
                    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nome_produto VARCHAR2(100),
                    tipo_produto INTEGER,
                    quantidade FLOAT,
                    silo_nome VARCHAR2(100),
                    endereco VARCHAR2(255),
                    capacidade FLOAT,
                    data_hora_registro DATE,
                    umidade FLOAT,
                    temperatura FLOAT,
                    ph FLOAT,
                    observacoes CLOB
                )
                """
                cursor.execute(create_table_sql)
                st.session_state.db_connection.commit()
                st.success("✅ Tabela SILOS criada com sucesso!")
            else:
                st.info("ℹ️ Tabela SILOS encontrada no banco de dados.")
    except oracledb.DatabaseError as e:
        st.error(f"Erro ao verificar/criar tabela: {e}")

def close_connection():
    """Fechar conexão com banco"""
    if st.session_state.db_connection:
        try:
            st.session_state.db_connection.close()
            st.session_state.db_connected = False
            st.session_state.db_connection = None
        except Exception as e:
            st.error(f"Erro ao fechar conexão: {e}")

def validate_silo_data(tipo_produto, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, ph):
    """Validar dados do silo"""
    errors = []
    
    if tipo_produto < 1 or tipo_produto > 5:
        errors.append("O produto deve ser um número de 1 a 5.")
    
    if quantidade < 0:
        errors.append("A quantidade deve ser maior ou igual a zero.")
    
    if not nome_silo.strip():
        errors.append("O nome do silo não pode ser vazio.")
    
    if not endereco.strip():
        errors.append("O endereço do silo não pode ser vazio.")
    
    if capacidade <= 0:
        errors.append("A capacidade deve ser maior que zero.")
    
    if capacidade < quantidade:
        errors.append("A quantidade não pode ser maior que a capacidade.")
    
    if not (0 <= umidade <= 100):
        errors.append("A umidade deve estar entre 0% e 100%.")
    
    if not (-10 <= temperatura <= 50):
        errors.append("A temperatura deve estar entre -10°C e 50°C.")
    
    if not (0 <= ph <= 14):
        errors.append("O pH deve estar entre 0 e 14.")
    
    return errors

def insert_silo(tipo_produto, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, ph, observacoes):
    """Inserir novo silo no banco"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            nome_produto = PRODUTOS[tipo_produto]["nome"]
            
            sql = """
            INSERT INTO SILOS(nome_produto, tipo_produto, quantidade, silo_nome, endereco, capacidade, 
                              data_hora_registro, umidade, temperatura, ph, observacoes) 
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)
            """
            
            cursor.execute(sql, (nome_produto, tipo_produto, quantidade, nome_silo, endereco, capacidade,
                                datetime.now(), umidade, temperatura, ph, observacoes))
            st.session_state.db_connection.commit()
        return True, "Silo cadastrado com sucesso!"
    except oracledb.DatabaseError as e:
        return False, f"Erro ao cadastrar silo: {e}"

def get_all_silos():
    """Buscar todos os silos"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM SILOS ORDER BY id")
            data = cursor.fetchall()
            columns = ['ID', 'Produto', 'Tipo', 'Quantidade (t)', 'Nome do Silo', 'Endereço', 
                      'Capacidade (t)', 'Data/Hora', 'Umidade (%)', 'Temperatura (°C)', 'pH', 'Observações']
            return pd.DataFrame(data, columns=columns)
    except oracledb.DatabaseError as e:
        st.error(f"Erro ao buscar silos: {e}")
        return pd.DataFrame()

def get_silo_by_id(silo_id):
    """Buscar silo por ID"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM SILOS WHERE id = :1", (silo_id,))
            data = cursor.fetchall()
            columns = ['ID', 'Produto', 'Tipo', 'Quantidade (t)', 'Nome do Silo', 'Endereço', 
                      'Capacidade (t)', 'Data/Hora', 'Umidade (%)', 'Temperatura (°C)', 'pH', 'Observações']
            return pd.DataFrame(data, columns=columns)
    except oracledb.DatabaseError as e:
        st.error(f"Erro ao buscar silo: {e}")
        return pd.DataFrame()

def update_silo(silo_id, tipo_produto, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, ph, observacoes):
    """Atualizar silo existente"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            nome_produto = PRODUTOS[tipo_produto]["nome"]
            
            sql = """
            UPDATE SILOS SET nome_produto = :1, tipo_produto = :2, quantidade = :3, 
            silo_nome = :4, endereco = :5, capacidade = :6, umidade = :7, temperatura = :8, 
            ph = :9, observacoes = :10 WHERE id = :11
            """
            
            cursor.execute(sql, (nome_produto, tipo_produto, quantidade, nome_silo, endereco, capacidade,
                                umidade, temperatura, ph, observacoes, silo_id))
            st.session_state.db_connection.commit()
        return True, "Silo atualizado com sucesso!"
    except oracledb.DatabaseError as e:
        return False, f"Erro ao atualizar silo: {e}"

def delete_silo(silo_id):
    """Deletar silo"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("DELETE FROM SILOS WHERE id = :1", (silo_id,))
            st.session_state.db_connection.commit()
        return True, "Silo excluído com sucesso!"
    except oracledb.DatabaseError as e:
        return False, f"Erro ao excluir silo: {e}"

def check_condition_adequacy(tipo_produto, valor, tipo_validacao):
    """Verificar se condições estão adequadas"""
    produto = PRODUTOS[tipo_produto]
    
    if tipo_validacao == 1:  # Umidade
        return produto["umidade_min"] <= valor <= produto["umidade_max"]
    elif tipo_validacao == 2:  # Temperatura
        return produto["temp_min"] <= valor <= produto["temp_max"]
    elif tipo_validacao == 3:  # pH
        return produto["ph_min"] <= valor <= produto["ph_max"]
    
    return False

def generate_report():
    """Gerar relatório completo"""
    try:
        df = get_all_silos()
        if df.empty:
            return "Não há registros no banco de dados para gerar relatório."
        
        report = "RELATÓRIO DOS SILOS\n"
        report += "=" * 50 + "\n\n"
        
        # Listagem de silos
        report += "LISTAGEM COMPLETA DOS SILOS:\n"
        report += "-" * 30 + "\n"
        report += df.to_string(index=False) + "\n\n"
        
        # Valor total em mercadorias
        valor_total = sum(df['Quantidade (t)'] * df['Tipo'].apply(lambda x: PRODUTOS[x]["valor"]))
        report += f"VALOR TOTAL EM MERCADORIAS: R$ {valor_total:,.2f}\n\n"
        
        # Silos com condições inadequadas
        report += "SILOS COM CONDIÇÕES INADEQUADAS:\n"
        report += "-" * 30 + "\n"
        
        # Umidade inadequada
        report += "• Umidade inadequada:\n"
        for _, row in df.iterrows():
            if not check_condition_adequacy(row['Tipo'], row['Umidade (%)'], 1):
                produto = PRODUTOS[row['Tipo']]
                report += f"  - {row['Nome do Silo']} (Umidade: {row['Umidade (%)']}% - Ideal: {produto['umidade_min']}%-{produto['umidade_max']}%)\n"
        
        # Temperatura inadequada
        report += "\n• Temperatura inadequada:\n"
        for _, row in df.iterrows():
            if not check_condition_adequacy(row['Tipo'], row['Temperatura (°C)'], 2):
                produto = PRODUTOS[row['Tipo']]
                report += f"  - {row['Nome do Silo']} (Temp: {row['Temperatura (°C)']}°C - Ideal: {produto['temp_min']}°C-{produto['temp_max']}°C)\n"
        
        # pH inadequado
        report += "\n• pH inadequado:\n"
        for _, row in df.iterrows():
            if not check_condition_adequacy(row['Tipo'], row['pH'], 3):
                produto = PRODUTOS[row['Tipo']]
                report += f"  - {row['Nome do Silo']} (pH: {row['pH']} - Ideal: {produto['ph_min']}-{produto['ph_max']})\n"
        
        return report
    except Exception as e:
        return f"Erro ao gerar relatório: {e}"

def backup_data():
    """Fazer backup dos dados"""
    try:
        with st.session_state.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM SILOS")
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            df = pd.DataFrame(data, columns=columns)
            
            # Converter datetime para string
            if 'DATA_HORA_REGISTRO' in df.columns:
                df['DATA_HORA_REGISTRO'] = df['DATA_HORA_REGISTRO'].apply(
                    lambda x: x.isoformat() if isinstance(x, datetime) else x
                )
            
            backup_data = df.to_dict(orient='records')
            return json.dumps(backup_data, indent=4)
    except Exception as e:
        st.error(f"Erro ao fazer backup: {e}")
        return None

def restore_backup(backup_json):
    """Restaurar dados do backup"""
    try:
        data = json.loads(backup_json)
        
        with st.session_state.db_connection.cursor() as cursor:
            for record in data:
                sql = """
                INSERT INTO SILOS (NOME_PRODUTO, TIPO_PRODUTO, QUANTIDADE, SILO_NOME, ENDERECO, CAPACIDADE, 
                                   DATA_HORA_REGISTRO, UMIDADE, TEMPERATURA, PH, OBSERVACOES) 
                VALUES (:1, :2, :3, :4, :5, :6, TO_DATE(:7, 'YYYY-MM-DD"T"HH24:MI:SS'), :8, :9, :10, :11)
                """
                cursor.execute(sql, (
                    record['NOME_PRODUTO'], record['TIPO_PRODUTO'],
                    record['QUANTIDADE'], record['SILO_NOME'],
                    record['ENDERECO'], record['CAPACIDADE'],
                    record['DATA_HORA_REGISTRO'], record['UMIDADE'],
                    record['TEMPERATURA'], record['PH'],
                    record['OBSERVACOES']
                ))
            
            st.session_state.db_connection.commit()
        return True, "Backup restaurado com sucesso!"
    except Exception as e:
        return False, f"Erro ao restaurar backup: {e}"

# Header principal
st.markdown('<h1 class="main-header">🏗️ Fase 2 - Python e Além - Silos</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Controle e Qualidade dos Grãos Armazenados</h2>', unsafe_allow_html=True)

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
    st.sidebar.title("🌾 Menu do Sistema")
    menu_options = [
        "🏠 Início",
        "➕ Cadastrar Silo",
        "👁️ Consultar Silo",
        "📋 Listar Todos os Silos",
        "✏️ Alterar Silo",
        "🗑️ Excluir Silo",
        "📊 Gerar Relatório",
        "💾 Backup de Dados",
        "📥 Restaurar Backup"
    ]
    
    selected_option = st.sidebar.selectbox("Selecione uma opção:", menu_options)
    
    # Conteúdo baseado na seleção
    if selected_option == "🏠 Início":
        st.markdown('<h2 class="section-header">📊 Dashboard do Sistema</h2>', unsafe_allow_html=True)
        
        # Buscar dados para dashboard
        df_silos = get_all_silos()
        
        if not df_silos.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_silos = len(df_silos)
                st.metric("🏗️ Total de Silos", total_silos)
            
            with col2:
                total_quantidade = df_silos['Quantidade (t)'].sum()
                st.metric("📦 Quantidade Total", f"{total_quantidade:.1f}t")
            
            with col3:
                total_capacidade = df_silos['Capacidade (t)'].sum()
                st.metric("🏭 Capacidade Total", f"{total_capacidade:.1f}t")
            
            with col4:
                valor_total = sum(df_silos['Quantidade (t)'] * df_silos['Tipo'].apply(lambda x: PRODUTOS[x]["valor"]))
                st.metric("💰 Valor Total", f"R$ {valor_total:,.0f}")
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Distribuição por Produto")
                produtos_count = df_silos['Produto'].value_counts()
                st.bar_chart(produtos_count)
            
            with col2:
                st.markdown("### ⚠️ Alertas de Qualidade")
                alertas = []
                for _, row in df_silos.iterrows():
                    if not check_condition_adequacy(row['Tipo'], row['Umidade (%)'], 1):
                        alertas.append(f"🌡️ {row['Nome do Silo']}: Umidade inadequada")
                    if not check_condition_adequacy(row['Tipo'], row['Temperatura (°C)'], 2):
                        alertas.append(f"🌡️ {row['Nome do Silo']}: Temperatura inadequada")
                    if not check_condition_adequacy(row['Tipo'], row['pH'], 3):
                        alertas.append(f"⚗️ {row['Nome do Silo']}: pH inadequado")
                
                if alertas:
                    for alerta in alertas[:5]:  # Mostrar apenas os primeiros 5
                        st.warning(alerta)
                    if len(alertas) > 5:
                        st.info(f"... e mais {len(alertas) - 5} alertas")
                else:
                    st.success("✅ Todos os silos em condições adequadas!")
        else:
            st.info("ℹ️ Nenhum silo cadastrado ainda. Use o menu para cadastrar o primeiro silo.")
    
    elif selected_option == "➕ Cadastrar Silo":
        st.markdown('<h2 class="section-header">➕ Cadastrar Novo Silo</h2>', unsafe_allow_html=True)
        
        # Product selection outside form for dynamic updates
        st.markdown("### 🌾 Seleção do Produto")
        tipo_produto = st.selectbox("🌾 Produto Armazenado", 
                                  options=list(PRODUTOS.keys()),
                                  format_func=lambda x: f"{x} - {PRODUTOS[x]['nome']}")
        
        # Display ideal parameters dynamically
        produto_info = PRODUTOS[tipo_produto]
        st.markdown("### 📊 Parâmetros Ideais de Armazenamento")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="info-box">
                <h4>🌡️ Umidade</h4>
                <p><strong>Ideal para {produto_info['nome']}:</strong></p>
                <p>{produto_info['umidade_min']}% - {produto_info['umidade_max']}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-box">
                <h4>🌡️ Temperatura</h4>
                <p><strong>Ideal para {produto_info['nome']}:</strong></p>
                <p>{produto_info['temp_min']}°C - {produto_info['temp_max']}°C</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="info-box">
                <h4>⚗️ pH</h4>
                <p><strong>Ideal para {produto_info['nome']}:</strong></p>
                <p>{produto_info['ph_min']} - {produto_info['ph_max']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Form for silo data entry
        st.markdown("### 📝 Dados do Silo")
        with st.form("cadastrar_silo"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_silo = st.text_input("🏗️ Nome do Silo", help="Nome identificador do silo")
                capacidade = st.number_input("📦 Capacidade Máxima (toneladas)", min_value=0.0, step=0.1)
                quantidade = st.number_input("⚖️ Quantidade Armazenada (toneladas)", min_value=0.0, step=0.1)
                endereco = st.text_area("📍 Endereço do Silo", help="Localização física do silo")
            
            with col2:
                st.markdown(f"**Produto Selecionado:** {produto_info['nome']}")
                
                umidade = st.number_input("🌡️ Umidade Atual (%)", 
                                        min_value=0.0, max_value=100.0, step=0.1,
                                        help=f"Ideal: {produto_info['umidade_min']}% - {produto_info['umidade_max']}%")
                
                temperatura = st.number_input("🌡️ Temperatura Atual (°C)", 
                                            min_value=-10.0, max_value=50.0, step=0.1,
                                            help=f"Ideal: {produto_info['temp_min']}°C - {produto_info['temp_max']}°C")
                
                ph = st.number_input("⚗️ pH Atual", 
                                   min_value=0.0, max_value=14.0, step=0.1,
                                   help=f"Ideal: {produto_info['ph_min']} - {produto_info['ph_max']}")
                
                observacoes = st.text_area("📝 Observações", placeholder="Observações adicionais (opcional)")
            
            if st.form_submit_button("💾 Cadastrar Silo", use_container_width=True):
                errors = validate_silo_data(tipo_produto, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, ph)
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    if not observacoes.strip():
                        observacoes = "Sem observações"
                    
                    success, message = insert_silo(tipo_produto, quantidade, nome_silo, endereco, 
                                                 capacidade, umidade, temperatura, ph, observacoes)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
    
    elif selected_option == "👁️ Consultar Silo":
        st.markdown('<h2 class="section-header">👁️ Consultar Silo Específico</h2>', unsafe_allow_html=True)
        
        # Mostrar lista de IDs e nomes
        df_silos = get_all_silos()
        if not df_silos.empty:
            st.markdown("### 📋 Silos Disponíveis:")
            silos_info = df_silos[['ID', 'Nome do Silo', 'Produto']].copy()
            st.dataframe(silos_info.reset_index(drop=True), use_container_width=True)
            
            silo_id = st.number_input("🔍 ID do Silo para Consulta", min_value=1, step=1)
            
            if st.button("🔍 Consultar Silo", use_container_width=True):
                df_silo = get_silo_by_id(silo_id)
                if not df_silo.empty:
                    st.markdown("### 📄 Detalhes do Silo:")
                    st.dataframe(df_silo.reset_index(drop=True), use_container_width=True)
                    
                    # Verificar condições
                    row = df_silo.iloc[0]
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        umidade_ok = check_condition_adequacy(row['Tipo'], row['Umidade (%)'], 1)
                        status = "✅ Adequada" if umidade_ok else "⚠️ Inadequada"
                        st.metric("🌡️ Umidade", f"{row['Umidade (%)']}%", status)
                    
                    with col2:
                        temp_ok = check_condition_adequacy(row['Tipo'], row['Temperatura (°C)'], 2)
                        status = "✅ Adequada" if temp_ok else "⚠️ Inadequada"
                        st.metric("🌡️ Temperatura", f"{row['Temperatura (°C)']}°C", status)
                    
                    with col3:
                        ph_ok = check_condition_adequacy(row['Tipo'], row['pH'], 3)
                        status = "✅ Adequado" if ph_ok else "⚠️ Inadequado"
                        st.metric("⚗️ pH", f"{row['pH']}", status)
                else:
                    st.error(f"❌ Nenhum silo encontrado com ID {silo_id}")
        else:
            st.info("ℹ️ Nenhum silo cadastrado ainda.")
    
    elif selected_option == "📋 Listar Todos os Silos":
        st.markdown('<h2 class="section-header">📋 Lista Completa de Silos</h2>', unsafe_allow_html=True)
        
        df_silos = get_all_silos()
        if not df_silos.empty:
            st.markdown(f"### 📊 Total de {len(df_silos)} silos cadastrados")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                produtos_filtro = st.multiselect("🌾 Filtrar por Produto", 
                                               options=df_silos['Produto'].unique(),
                                               default=df_silos['Produto'].unique())
            with col2:
                mostrar_alertas = st.checkbox("⚠️ Mostrar apenas silos com alertas", False)
            
            # Aplicar filtros
            df_filtrado = df_silos[df_silos['Produto'].isin(produtos_filtro)]
            
            if mostrar_alertas:
                indices_alerta = []
                for idx, row in df_filtrado.iterrows():
                    if (not check_condition_adequacy(row['Tipo'], row['Umidade (%)'], 1) or
                        not check_condition_adequacy(row['Tipo'], row['Temperatura (°C)'], 2) or
                        not check_condition_adequacy(row['Tipo'], row['pH'], 3)):
                        indices_alerta.append(idx)
                df_filtrado = df_filtrado.loc[indices_alerta]
            
            st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)
            
            # Botão para download CSV
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="📥 Baixar como CSV",
                data=csv,
                file_name=f"silos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ Nenhum silo cadastrado ainda.")
    
    elif selected_option == "✏️ Alterar Silo":
        st.markdown('<h2 class="section-header">✏️ Alterar Silo Existente</h2>', unsafe_allow_html=True)
        
        df_silos = get_all_silos()
        if not df_silos.empty:
            # Seleção do silo
            st.markdown("### 📋 Selecionar Silo para Alteração:")
            silos_info = df_silos[['ID', 'Nome do Silo', 'Produto']].copy()
            st.dataframe(silos_info.reset_index(drop=True), use_container_width=True)
            
            silo_id = st.number_input("🔍 ID do Silo para Alterar", min_value=1, step=1)
            
            if st.button("📝 Carregar Dados do Silo"):
                df_silo = get_silo_by_id(silo_id)
                if not df_silo.empty:
                    st.session_state.silo_para_editar = df_silo.iloc[0].to_dict()
                    st.success(f"✅ Dados do silo {silo_id} carregados!")
                else:
                    st.error(f"❌ Silo com ID {silo_id} não encontrado!")
            
            # Formulário de edição
            if 'silo_para_editar' in st.session_state:
                st.markdown("### ✏️ Editar Dados:")
                silo_data = st.session_state.silo_para_editar
                
                with st.form("alterar_silo"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nome_silo = st.text_input("🏗️ Nome do Silo", value=silo_data['Nome do Silo'])
                        capacidade = st.number_input("📦 Capacidade Máxima (toneladas)", 
                                                   value=float(silo_data['Capacidade (t)']), min_value=0.0, step=0.1)
                        tipo_produto = st.selectbox("🌾 Produto Armazenado", 
                                                  options=list(PRODUTOS.keys()),
                                                  index=silo_data['Tipo']-1,
                                                  format_func=lambda x: f"{x} - {PRODUTOS[x]['nome']}")
                        quantidade = st.number_input("⚖️ Quantidade Armazenada (toneladas)", 
                                                   value=float(silo_data['Quantidade (t)']), min_value=0.0, step=0.1)
                        endereco = st.text_area("📍 Endereço do Silo", value=silo_data['Endereço'])
                    
                    with col2:
                        umidade = st.number_input("🌡️ Umidade Atual (%)", 
                                                value=float(silo_data['Umidade (%)']), min_value=0.0, max_value=100.0, step=0.1)
                        temperatura = st.number_input("🌡️ Temperatura Atual (°C)", 
                                                    value=float(silo_data['Temperatura (°C)']), min_value=-10.0, max_value=50.0, step=0.1)
                        ph = st.number_input("⚗️ pH Atual", 
                                           value=float(silo_data['pH']), min_value=0.0, max_value=14.0, step=0.1)
                        observacoes = st.text_area("📝 Observações", value=silo_data['Observações'])
                    
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        errors = validate_silo_data(tipo_produto, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, ph)
                        
                        if errors:
                            for error in errors:
                                st.error(f"❌ {error}")
                        else:
                            success, message = update_silo(silo_data['ID'], tipo_produto, quantidade, nome_silo, 
                                                         endereco, capacidade, umidade, temperatura, ph, observacoes)
                            if success:
                                st.success(f"✅ {message}")
                                del st.session_state.silo_para_editar
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            st.info("ℹ️ Nenhum silo cadastrado ainda.")
    
    elif selected_option == "🗑️ Excluir Silo":
        st.markdown('<h2 class="section-header">🗑️ Excluir Silo</h2>', unsafe_allow_html=True)
        
        df_silos = get_all_silos()
        if not df_silos.empty:
            st.markdown("### 📋 Silos Disponíveis:")
            silos_info = df_silos[['ID', 'Nome do Silo', 'Produto']].copy()
            st.dataframe(silos_info.reset_index(drop=True), use_container_width=True)
            
            silo_id = st.number_input("🗑️ ID do Silo para Excluir", min_value=1, step=1)
            
            # Mostrar dados do silo selecionado
            if st.button("👁️ Visualizar Silo"):
                df_silo = get_silo_by_id(silo_id)
                if not df_silo.empty:
                    st.markdown("### 📄 Dados do Silo a ser Excluído:")
                    st.dataframe(df_silo.reset_index(drop=True), use_container_width=True)
                    st.session_state.silo_para_excluir = silo_id
                else:
                    st.error(f"❌ Silo com ID {silo_id} não encontrado!")
            
            # Confirmação de exclusão
            if 'silo_para_excluir' in st.session_state:
                st.markdown("""
                <div class="warning-box">
                    <h4>⚠️ Confirmação de Exclusão</h4>
                    <p>Esta ação não pode ser desfeita. Tem certeza que deseja excluir este silo?</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirmar Exclusão", use_container_width=True, type="primary"):
                        success, message = delete_silo(st.session_state.silo_para_excluir)
                        if success:
                            st.success(f"✅ {message}")
                            del st.session_state.silo_para_excluir
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                with col2:
                    if st.button("❌ Cancelar", use_container_width=True):
                        del st.session_state.silo_para_excluir
                        st.rerun()
        else:
            st.info("ℹ️ Nenhum silo cadastrado ainda.")
    
    elif selected_option == "📊 Gerar Relatório":
        st.markdown('<h2 class="section-header">📊 Relatório Completo dos Silos</h2>', unsafe_allow_html=True)
        
        if st.button("📊 Gerar Relatório", use_container_width=True):
            with st.spinner("Gerando relatório..."):
                relatorio = generate_report()
                st.text_area("📄 Relatório dos Silos", relatorio, height=400)
                
                # Download do relatório
                st.download_button(
                    label="📥 Baixar Relatório",
                    data=relatorio,
                    file_name=f"relatorio_silos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    elif selected_option == "💾 Backup de Dados":
        st.markdown('<h2 class="section-header">💾 Backup de Dados</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h4>📋 Sobre o Backup</h4>
            <p>O backup exporta todos os dados dos silos em formato JSON, que pode ser usado para restaurar os dados posteriormente.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 Gerar Backup", use_container_width=True):
            with st.spinner("Gerando backup..."):
                backup_json = backup_data()
                if backup_json:
                    st.success("✅ Backup gerado com sucesso!")
                    
                    # Mostrar preview do backup
                    st.text_area("📄 Preview do Backup (JSON)", backup_json[:500] + "..." if len(backup_json) > 500 else backup_json, height=200)
                    
                    # Download do backup
                    st.download_button(
                        label="📥 Baixar Backup",
                        data=backup_json,
                        file_name=f"backup_silos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
    
    elif selected_option == "📥 Restaurar Backup":
        st.markdown('<h2 class="section-header">📥 Restaurar Backup</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Atenção</h4>
            <p>A restauração do backup irá <strong>adicionar</strong> os dados ao banco existente. 
            Se desejar substituir completamente os dados, exclua os registros existentes primeiro.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload do arquivo
        uploaded_file = st.file_uploader("📁 Selecione o arquivo de backup (JSON)", type="json")
        
        if uploaded_file is not None:
            try:
                backup_content = uploaded_file.read().decode('utf-8')
                
                # Preview do backup
                st.markdown("### 👁️ Preview do Backup:")
                data = json.loads(backup_content)
                st.write(f"📊 Total de registros: {len(data)}")
                
                if data:
                    df_preview = pd.DataFrame(data[:5])  # Mostrar apenas os primeiros 5
                    st.dataframe(df_preview.reset_index(drop=True), use_container_width=True)
                    
                    if len(data) > 5:
                        st.info(f"... e mais {len(data) - 5} registros")
                
                # Confirmação
                if st.button("📥 Confirmar Restauração", use_container_width=True, type="primary"):
                    with st.spinner("Restaurando backup..."):
                        success, message = restore_backup(backup_content)
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
            
            except json.JSONDecodeError:
                st.error("❌ Arquivo JSON inválido!")
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {e}")
