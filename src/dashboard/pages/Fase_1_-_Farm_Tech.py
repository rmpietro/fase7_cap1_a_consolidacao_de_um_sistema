import streamlit as st
import pandas as pd
import sys
import os
import subprocess
import requests
from pathlib import Path
import plotly.express as px
from datetime import datetime

# Adicionar diretório pai ao PYTHONPATH para poder importar os módulos
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent.parent
fase1_dir = root_dir / "src" / "fase1"

if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
if str(fase1_dir) not in sys.path:
    sys.path.append(str(fase1_dir))

# Importando os módulos da fase1
try:
    import area_calculation
    from agricultural_input_calc import calculate_input_consumption
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - Sistema de Agricultura Digital",
    page_icon="🌱",
    layout="wide"
)

# CSS customizado pelo grupo para melhorar a aparência, mas mantendo um tema agro
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #228B22;
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
    .topology-container {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Estado da sessão para armazenar dados
if 'area_metrics' not in st.session_state:
    st.session_state.area_metrics = {}
if 'corn_area_total' not in st.session_state:
    st.session_state.corn_area_total = 0
if 'sugarcane_area_total' not in st.session_state:
    st.session_state.sugarcane_area_total = 0
if 'corn_input_consumption' not in st.session_state:
    st.session_state.corn_input_consumption = None
if 'sugarcane_input_consumption' not in st.session_state:
    st.session_state.sugarcane_input_consumption = None

# Função para exibir a topologia
def display_topology():
    topology_text = """
                                                      
                L1                                    
         ┌──────────────┐                             
        ┌───────────────┐                             
       ┌│███████████████│                             
    R1 └│███████████████│                             
        │▢▢▢▢▢▢▢▢▢▢▢│                             
       ┌│███████████████│                             
       └│███████████████│  ┌──────────────────────────┐
        │▢▢▢▢▢▢▢▢▢▢▢│  │ ██       Milho           │
       ┌│███████████████│  │ ██  (Cultivo em ruas     │
       └│███████████████│  │ ██    horizontais)       │
       ┌│─ ─ ─ ─ ─ ─ ─ ─│  └──────────────────────────┘
       ││░░░▢░░░▢░░░▢░░░│ ┌──────────────────────────┐
       ││░░░▢░░░▢░░░▢░░░│ │ ░░   Cana-de-Açúcar      │
       ││░░░▢░░░▢░░░▢░░░│ │ ░░  (Cultivo em ruas     │
       ││░░░▢░░░▢░░░▢░░░│ │ ░░     verticais)        │
    L2 ││░░░▢░░░▢░░░▢░░░│ └──────────────────────────┘
       ││░░░▢░░░▢░░░▢░░░│                             
       ││░░░▢░░░▢░░░▢░░░│                             
       ││░░░▢░░░▢░░░▢░░░│                             
       ││░░░▢░░░▢░░░▢░░░│                             
       ││░░░▢░░░▢░░░▢░░░│                             
       └ ─ ─ ─ ─ ─ ─ ─ ─────────────── ┐                   
        ╲░░░▢░░░▢░░░▢░░░▢░░░▢░░░▢││                   
         ╲░░▢░░░▢░░░▢░░░▢░░░▢░░░▢││                   
          ╲░▢░░░▢░░░▢░░░▢░░░▢░░░▢││ L3                
           ╲▢░░░▢░░░▢░░░▢░░░▢░░░▢││                   
            ╲░░░▢░░░▢░░░▢░░░▢░░░░▢││                   
             ─────────────────────┘┘                   
             └──┘                                     
              R2                                      
    """
    return topology_text

# Função para apagar arquivos CSV
def delete_csv_data_files():
    csv_files = [
        'csv/corn_data_output.csv',
        'csv/sugarcane_data_output.csv',
        'csv/corn_stats_R.csv',
        'csv/sugarcane_stats_R.csv',
        'csv/weather_forecast_R.csv'
    ]
    
    deleted_files = []
    for file_path in csv_files:
        full_path = fase1_dir / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                deleted_files.append(file_path)
            except Exception as e:
                st.error(f"Erro ao deletar {file_path}: {e}")
    
    return deleted_files

# Header principal
st.markdown('<h1 class="main-header">🏞️ Fase 1 - Farm Tech</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Sistema de Agricultura Digital</h2>', unsafe_allow_html=True)

# Informações sobre o sistema
st.markdown("""
<div class="info-box">
    <h4>📋 Sobre o Sistema</h4>
    <p>O sistema é responsável por fazer a gestão das duas culturas de <strong>cana-de-açúcar</strong> e <strong>milho</strong> 
    nas fazendas e calcular o consumo de insumos necessários para o plantio, cultivo e colheita.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para navegação
st.sidebar.title("🌾 Menu do Sistema")
menu_options = [
    "🏠 Início",
    "📏 Medidas do Terreno",
    "✏️ Atualizar Medidas",
    "🗑️ Apagar Dados",
    "🧮 Calcular Insumos",
    "📊 Análise Estatística",
    "🌤️ Previsão Meteorológica"
]

selected_option = st.sidebar.selectbox("Selecione uma opção:", menu_options)

# Verificar se há medidas suficientes para certas opções
has_sufficient_data = len(st.session_state.area_metrics) >= 5

# Conteúdo principal baseado na opção selecionada
if selected_option == "🏠 Início":
    st.markdown('<h2 class="section-header">🌱 Bem-vindo ao FarmTech Solutions</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h4>🌽 Milho</h4>
            <p>Cultivo em ruas horizontais</p>
            <p>Sistema de medição: L1 × R1</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h4>🌾 Cana-de-açúcar</h4>
            <p>Cultivo em ruas verticais</p>
            <p>Sistema de medição: L2, L3 × R2</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <h4>📊 Status dos Dados</h4>
            <p><strong>Medidas:</strong> {}/5</p>
            <p><strong>Status:</strong> {}</p>
        </div>
        """.format(
            len(st.session_state.area_metrics),
            "✅ Completo" if has_sufficient_data else "⏳ Pendente"
        ), unsafe_allow_html=True)

    if has_sufficient_data:
        st.success("✅ Todas as medidas foram informadas! Você pode usar todas as funcionalidades do sistema.")
    else:
        st.warning("⚠️ Complete a entrada de medidas do terreno para acessar todas as funcionalidades. Acesse o menu ao lado e selecione a opção adequada.")

elif selected_option == "📏 Medidas do Terreno":
    st.markdown('<h2 class="section-header">📏 Entrada de Medidas do Terreno</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>🗺️ Topologia da Área de Cultivo</h4>
        <p>Informe o valor de cada medida para as arestas do terreno e para as ruas de plantio, 
        conforme as referências nomeadas no diagrama:</p>
        <ul>
            <li><strong>L1, L2 e L3:</strong> Medidas laterais do terreno cultivado</li>
            <li><strong>R1 e R2:</strong> Medidas de largura das ruas de plantio</li>
            <li><strong>Milho:</strong> Plantio delineado com 2 ruas horizontais</li>
            <li><strong>Cana-de-açúcar:</strong> Plantio delineado com 4 e 6 ruas verticais</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibir topologia
    st.markdown("### 🗺️ Diagrama da Topologia")
    st.markdown(f'<div class="topology-container">{display_topology()}', unsafe_allow_html=True)
    
    # Formulário para entrada de medidas
    st.markdown("### 📝 Formulário de Medidas")
    
    with st.form("medidas_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            l1 = st.number_input(
                "L1 - Extensão das ruas de plantio de MILHO (metros)",
                min_value=0.0,
                value=float(st.session_state.area_metrics.get('L1', 0)),
                step=0.1,
                help="Comprimento das ruas de plantio horizontal do milho"
            )
            
            r1 = st.number_input(
                "R1 - Largura das ruas de plantio de MILHO (metros)",
                min_value=0.0,
                value=float(st.session_state.area_metrics.get('R1', 0)),
                step=0.1,
                help="Largura das ruas de plantio do milho"
            )
            
            l2 = st.number_input(
                "L2 - Extensão das ruas de plantio de CANA-DE-AÇÚCAR (Área 1) (metros)",
                min_value=0.0,
                value=float(st.session_state.area_metrics.get('L2', 0)),
                step=0.1,
                help="Comprimento das ruas na primeira área de cana-de-açúcar"
            )
        
        with col2:
            r2 = st.number_input(
                "R2 - Largura das ruas de plantio de CANA-DE-AÇÚCAR (metros)",
                min_value=0.0,
                value=float(st.session_state.area_metrics.get('R2', 0)),
                step=0.1,
                help="Largura das ruas para ambas as áreas de cana-de-açúcar"
            )
            
            l3 = st.number_input(
                "L3 - Extensão das ruas de plantio de CANA-DE-AÇÚCAR (Área 2) (metros)",
                min_value=0.0,
                value=float(st.session_state.area_metrics.get('L3', 0)),
                step=0.1,
                help="Comprimento das ruas na segunda área de cana-de-açúcar"
            )
        
        submitted = st.form_submit_button("💾 Salvar Medidas", use_container_width=True)
        
        if submitted:
            if all([l1 > 0, r1 > 0, l2 > 0, r2 > 0, l3 > 0]):
                st.session_state.area_metrics = {
                    'L1': l1,
                    'R1': r1,
                    'L2': l2,
                    'R2': r2,
                    'L3': l3
                }
                st.markdown("""
                <div class="success-message">
                    ✅ <strong>Medidas recebidas e atualizadas com sucesso!</strong><br>
                    Agora você pode acessar todas as funcionalidades do sistema.
                </div>
                """, unsafe_allow_html=True)
                st.rerun()
            else:
                st.error("❌ Por favor, informe valores válidos (maiores que zero) para todas as medidas.")

elif selected_option == "✏️ Atualizar Medidas":
    st.markdown('<h2 class="section-header">✏️ Atualizar Medidas Existentes</h2>', unsafe_allow_html=True)
    
    if not has_sufficient_data:
        st.warning("⚠️ Não há medidas suficientes informadas para atualização. Complete a entrada de medidas primeiro.")
    else:
        st.info("📝 Selecione a medida que deseja atualizar e informe o novo valor:")
        
        # Seletor de medida
        measure_options = {
            'L1': f"L1 - Extensão MILHO (atual: {st.session_state.area_metrics['L1']} m)",
            'R1': f"R1 - Largura MILHO (atual: {st.session_state.area_metrics['R1']} m)",
            'L2': f"L2 - Extensão CANA Área 1 (atual: {st.session_state.area_metrics['L2']} m)",
            'R2': f"R2 - Largura CANA (atual: {st.session_state.area_metrics['R2']} m)",
            'L3': f"L3 - Extensão CANA Área 2 (atual: {st.session_state.area_metrics['L3']} m)"
        }
        
        selected_measure = st.selectbox("Selecione a medida para atualizar:", list(measure_options.keys()), 
                                      format_func=lambda x: measure_options[x])
        
        current_value = st.session_state.area_metrics[selected_measure]
        new_value = st.number_input(
            f"Novo valor para {selected_measure} (metros):",
            min_value=0.0,
            value=current_value,
            step=0.1
        )
        
        if st.button("🔄 Atualizar Medida", use_container_width=True):
            if new_value > 0:
                st.session_state.area_metrics[selected_measure] = new_value
                st.success(f"✅ Medida {selected_measure} atualizada com sucesso para {new_value} metros!")
                st.rerun()
            else:
                st.error("❌ O valor deve ser maior que zero.")

elif selected_option == "🗑️ Apagar Dados":
    st.markdown('<h2 class="section-header">🗑️ Apagar Dados do Sistema</h2>', unsafe_allow_html=True)
    
    if not has_sufficient_data:
        st.info("ℹ️ Não há medidas informadas para apagar.")
    else:
        st.warning("⚠️ Esta ação irá apagar todas as medidas e arquivos de transferência gerados.")
        
        # Mostrar dados atuais
        st.markdown("### 📋 Dados Atuais:")
        df_current = pd.DataFrame(list(st.session_state.area_metrics.items()), 
                                 columns=['Medida', 'Valor (m)'])
        st.dataframe(df_current.reset_index(drop=True), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Confirmar Exclusão", use_container_width=True, type="primary"):
                # Apagar dados da sessão
                st.session_state.area_metrics = {}
                st.session_state.corn_area_total = 0
                st.session_state.sugarcane_area_total = 0
                st.session_state.corn_input_consumption = None
                st.session_state.sugarcane_input_consumption = None
                
                # Apagar arquivos CSV
                deleted_files = delete_csv_data_files()
                
                st.success("✅ Medidas e arquivos de transferência apagados com sucesso!")
                if deleted_files:
                    st.info(f"📁 Arquivos removidos: {', '.join(deleted_files)}")
                st.rerun()
        
        with col2:
            st.button("❌ Cancelar", use_container_width=True)

elif selected_option == "🧮 Calcular Insumos":
    st.markdown('<h2 class="section-header">🧮 Cálculo de Consumo de Insumos</h2>', unsafe_allow_html=True)
    
    if not has_sufficient_data:
        st.warning("⚠️ Não há medidas informadas para os cálculos. Complete a entrada de medidas primeiro.")
    else:
        # Calcular áreas
        corn_area_total = area_calculation.corn_area_calculation(3, st.session_state.area_metrics['L1'], st.session_state.area_metrics['R1'])
        sugarcane_area_total = area_calculation.sugar_cane_area_calculation(4, 6, st.session_state.area_metrics['L2'], st.session_state.area_metrics['L3'], st.session_state.area_metrics['R2'])
        
        # Atualizar estado da sessão
        st.session_state.corn_area_total = corn_area_total
        st.session_state.sugarcane_area_total = sugarcane_area_total
        
        # Exibir áreas calculadas
        st.markdown("### 📐 Áreas Totais Calculadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h4>🌽 Área de Plantio - Milho</h4>
                <p><strong>{corn_area_total:,.2f} m²</strong></p>
                <p>{(corn_area_total / 1_000_000):,.4f} km²</p>
                <p>{(corn_area_total / 10_000):,.2f} hectares</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h4>🌾 Área de Plantio - Cana-de-açúcar</h4>
                <p><strong>{sugarcane_area_total:,.2f} m²</strong></p>
                <p>{(sugarcane_area_total / 1_000_000):,.4f} km²</p>
                <p>{(sugarcane_area_total / 10_000):,.2f} hectares</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Calcular consumo de insumos
        st.markdown("### 🧪 Consumo de Insumos por Mês")
        
        if st.button("🔄 Calcular Consumo de Insumos", use_container_width=True):
            try:
                corn_input_consumption = calculate_input_consumption(corn_area_total, "milho")
                sugarcane_input_consumption = calculate_input_consumption(sugarcane_area_total, "cana")
                
                # Armazenar na sessão
                st.session_state.corn_input_consumption = corn_input_consumption
                st.session_state.sugarcane_input_consumption = sugarcane_input_consumption
                
                st.success("✅ Cálculo de insumos realizado com sucesso!")
                
            except Exception as e:
                st.error(f"❌ Erro ao calcular insumos: {e}")
        
        # Exibir resultados se disponíveis
        if st.session_state.corn_input_consumption is not None:
            st.markdown("#### 🌽 Milho - Resultados em Kg ou L por metro quadrado")
            st.dataframe(st.session_state.corn_input_consumption.reset_index(drop=True), use_container_width=True)
            
            st.markdown("#### 🌾 Cana-de-açúcar - Resultados em Kg ou L por metro quadrado")
            st.dataframe(st.session_state.sugarcane_input_consumption.reset_index(drop=True), use_container_width=True)
            
            # Botão para salvar CSV
            if st.button("💾 Exportar Dados para CSV", use_container_width=True):
                try:
                    csv_dir = fase1_dir / "csv"
                    csv_dir.mkdir(exist_ok=True)
                    
                    corn_csv_path = csv_dir / "corn_data_output.csv"
                    sugarcane_csv_path = csv_dir / "sugarcane_data_output.csv"
                    
                    st.session_state.corn_input_consumption.to_csv(corn_csv_path, index=False)
                    st.session_state.sugarcane_input_consumption.to_csv(sugarcane_csv_path, index=False)
                    
                    st.success("✅ Dados exportados com sucesso para arquivos CSV!")
                    st.info(f"📁 Arquivos salvos em: {csv_dir}")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao exportar CSV: {e}")

elif selected_option == "📊 Análise Estatística":
    st.markdown('<h2 class="section-header">📊 Análise Estatística dos Insumos</h2>', unsafe_allow_html=True)
    
    # Verificar se existem arquivos CSV
    csv_dir = fase1_dir / "csv"
    corn_csv = csv_dir / "corn_data_output.csv"
    sugarcane_csv = csv_dir / "sugarcane_data_output.csv"
    
    if not (corn_csv.exists() and sugarcane_csv.exists()):
        st.warning("⚠️ Não há dados de consumo de insumos para gerar estatísticas. Execute o cálculo de insumos primeiro.")
        
        if st.button("🧮 Ir para Cálculo de Insumos"):
            st.session_state.selected_option = "🧮 Calcular Insumos"
            st.rerun()
    else:
        st.info("📊 Executando análise estatística usando scripts R...")
        
        if st.button("🔄 Gerar Estatísticas", use_container_width=True):
            try:
                # Executar script R
                r_script_path = fase1_dir / "R" / "crop_statistics.R"
                
                if r_script_path.exists():
                    with st.spinner("⏳ Executando análise estatística..."):
                        result = subprocess.run(
                            ["Rscript", "--no-echo", str(r_script_path)],
                            cwd=str(fase1_dir),
                            capture_output=True,
                            text=True
                        )
                    
                    if result.returncode == 0:
                        # Ler resultados
                        corn_stats_path = csv_dir / "corn_stats_R.csv"
                        sugarcane_stats_path = csv_dir / "sugarcane_stats_R.csv"
                        
                        if corn_stats_path.exists() and sugarcane_stats_path.exists():
                            corn_stats = pd.read_csv(corn_stats_path)
                            sugarcane_stats = pd.read_csv(sugarcane_stats_path)
                            
                            st.success("✅ Análise estatística concluída!")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### 🌽 Milho - Estatísticas Anuais")
                                st.dataframe(corn_stats.reset_index(drop=True), use_container_width=True)
                            
                            with col2:
                                st.markdown("#### 🌾 Cana-de-açúcar - Estatísticas Anuais")
                                st.dataframe(sugarcane_stats.reset_index(drop=True), use_container_width=True)
                        else:
                            st.error("❌ Arquivos de estatísticas não foram gerados.")
                    else:
                        st.error(f"❌ Erro ao executar script R: {result.stderr}")
                else:
                    st.error("❌ Script R não encontrado. Verifique se o arquivo crop_statistics.R existe.")
                    
            except Exception as e:
                st.error(f"❌ Erro ao executar análise estatística: {e}")

elif selected_option == "🌤️ Previsão Meteorológica":
    st.markdown('<h2 class="section-header">🌤️ Previsão Meteorológica</h2>', unsafe_allow_html=True)
    
    st.info("🌍 Obtendo dados de previsão meteorológica para Presidente Prudente - SP (localização das fazendas)")
    
    def get_weather_forecast():
        """Obter previsão meteorológica usando OpenWeatherMap API"""
        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': -22.1256,  # Presidente Prudente latitude
                'lon': -51.3889,  # Presidente Prudente longitude
                'appid': "48380355e6896ab9c1318bc85deca9c3",
                'units': 'metric',
                'cnt': 40  # 5 days * 8 (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                forecast_data = []
                for item in data['list']:
                    date_str = item['dt_txt']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Considerar apenas as previsões do meio-dia (12:00) para resumo diário
                    if date_obj.hour == 12:
                        chuva = item.get('rain', {}).get('3h', 0)
                        temp_max = item['main']['temp_max']
                        temp_min = item['main']['temp_min']
                        humidity = item['main']['humidity']
                        description = item['weather'][0]['description']
                        
                        forecast_data.append({
                            "Data": date_obj.strftime('%d/%m/%Y'),
                            "Descrição": description.title(),
                            "Temp. Máxima (°C)": f"{temp_max:.1f}",
                            "Temp. Mínima (°C)": f"{temp_min:.1f}",
                            "Umidade (%)": f"{humidity}",
                            "Chuva (mm)": f"{chuva:.1f}"
                        })
                
                return pd.DataFrame(forecast_data)
            else:
                st.error(f"❌ Erro na API: {response.status_code}")
                return pd.DataFrame()
                
        except requests.exceptions.Timeout:
            st.error("❌ Timeout: A requisição demorou muito para responder")
            return pd.DataFrame()
        except requests.exceptions.ConnectionError:
            st.error("❌ Erro de conexão: Verifique sua conexão com a internet")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Erro ao obter dados meteorológicos: {e}")
            return pd.DataFrame()
    
    if st.button("🔄 Buscar Previsão do Tempo", use_container_width=True):
        with st.spinner("⏳ Buscando dados meteorológicos..."):
            weather_data = get_weather_forecast()
            
            if not weather_data.empty:
                st.success("✅ Dados meteorológicos obtidos com sucesso!")
                
                # Exibir dados
                st.markdown("#### 🌤️ Previsão para os próximos 5 dias")
                st.dataframe(weather_data.reset_index(drop=True), use_container_width=True)
                
                # Gráficos
                col1, col2 = st.columns(2)
                
                with col1:
                    # Converter temperaturas para numérico para plotagem
                    weather_plot = weather_data.copy()
                    weather_plot['Temp_Max_Numeric'] = weather_plot['Temp. Máxima (°C)'].astype(float)
                    weather_plot['Temp_Min_Numeric'] = weather_plot['Temp. Mínima (°C)'].astype(float)
                    
                    fig_temp = px.line(weather_plot, x='Data', y=['Temp_Max_Numeric', 'Temp_Min_Numeric'],
                                      title="🌡️ Variação de Temperatura",
                                      labels={'value': 'Temperatura (°C)', 'variable': 'Tipo'})
                    fig_temp.update_layout(height=400)
                    st.plotly_chart(fig_temp, use_container_width=True)
                
                with col2:
                    weather_plot['Chuva_Numeric'] = weather_plot['Chuva (mm)'].astype(float)
                    fig_rain = px.bar(weather_plot, x='Data', y='Chuva_Numeric',
                                     title="🌧️ Previsão de Chuva",
                                     labels={'Chuva_Numeric': 'Chuva (mm)'})
                    fig_rain.update_layout(height=400)
                    st.plotly_chart(fig_rain, use_container_width=True)
                
                # Salvar dados em CSV
                try:
                    csv_dir = fase1_dir / "csv"
                    csv_dir.mkdir(exist_ok=True)
                    
                    weather_csv_path = csv_dir / "weather_forecast_python.csv"
                    weather_data.to_csv(weather_csv_path, index=False)
                    st.info(f"📁 Dados salvos em: {weather_csv_path}")
                    
                except Exception as e:
                    st.warning(f"⚠️ Não foi possível salvar CSV: {e}")
                
                # Análise dos dados
                st.markdown("#### 📊 Análise dos Dados Meteorológicos")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    temp_max_avg = weather_plot['Temp_Max_Numeric'].mean()
                    st.metric("🌡️ Temp. Máx. Média", f"{temp_max_avg:.1f}°C")
                
                with col2:
                    temp_min_avg = weather_plot['Temp_Min_Numeric'].mean()
                    st.metric("🌡️ Temp. Mín. Média", f"{temp_min_avg:.1f}°C")
                
                with col3:
                    total_rain = weather_plot['Chuva_Numeric'].sum()
                    st.metric("🌧️ Chuva Total", f"{total_rain:.1f} mm")
                
                # Recomendações
                st.markdown("#### 💡 Recomendações Agrícolas")
                
                if total_rain < 10:
                    st.warning("⚠️ **Baixa previsão de chuva:** Considere planejar irrigação adicional para as culturas.")
                elif total_rain > 50:
                    st.info("💧 **Alta previsão de chuva:** Boa condição natural para as culturas. Monitore drenagem.")
                else:
                    st.success("✅ **Chuva moderada:** Condições adequadas para agricultura.")
                
                if temp_max_avg > 35:
                    st.warning("🌡️ **Temperaturas altas:** Monitore stress térmico nas plantas e considere irrigação resfriamento.")
                elif temp_max_avg < 20:
                    st.info("❄️ **Temperaturas amenas:** Atenção para culturas sensíveis ao frio.")
    
    # Informações adicionais
    st.markdown("""
    <div class="info-box">
        <h4>📍 Informações sobre a Previsão</h4>
        <ul>
            <li><strong>Localização:</strong> Presidente Prudente, São Paulo</li>
            <li><strong>Coordenadas:</strong> 22.1256°S, 51.3889°W</li>
            <li><strong>Período:</strong> Próximos 5 dias</li>
            <li><strong>Fonte:</strong> OpenWeatherMap API</li>
            <li><strong>Atualização:</strong> Dados em tempo real a cada 3 horas</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
