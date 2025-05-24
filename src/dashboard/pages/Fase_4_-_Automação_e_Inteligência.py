import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

# Adicionar diretório pai ao PYTHONPATH
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dados.data_analysis import SensorDataAnalyzer

# Configuração da página
st.set_page_config(
    page_title="Análise Avançada de Dados Agrícolas",
    page_icon="📊",
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
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E6F3FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #007BFF;
        margin: 1rem 0;
    }
    .analysis-card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #DEE2E6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">📊 Fase 4 - Automação e Inteligência - Análise de Dados</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Análise Exploratória e Modelos Preditivos</h2>', unsafe_allow_html=True)

# Menu de seleção
st.sidebar.title("📊 Menu de Análises")
analysis_options = [
    "📊 Análise Exploratória",
    "🤖 Modelo Preditivo"
]

selected_analysis = st.sidebar.selectbox("Selecione o tipo de análise:", analysis_options)

# Função para carregar os dados
@st.cache_data
def load_data():
    try:
        farm_tech_analyzer = SensorDataAnalyzer()
        return farm_tech_analyzer.load_data()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar dados
df = load_data()

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique se o sistema está configurado corretamente.")
    st.stop()

# Conteúdo baseado na seleção
if selected_analysis == "📊 Análise Exploratória":
    st.markdown('<h2 class="section-header">📊 Análise Exploratória dos Dados</h2>', unsafe_allow_html=True)
    
    # Informações gerais dos dados
    st.markdown("""
    <div class="info-box">
        <h4>📋 Visão Geral dos Dados</h4>
        <p>Esta seção apresenta análises detalhadas dos dados coletados pelos sensores agrícolas, 
        incluindo distribuições, correlações e padrões nos dados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total de Registros", len(df))
    
    with col2:
        st.metric("🌡️ Temp. Média", f"{df['temp'].mean():.1f}°C" if 'temp' in df.columns else "N/A")
    
    with col3:
        st.metric("💧 Umid. Média", f"{df['hum'].mean():.1f}%" if 'hum' in df.columns else "N/A")
    
    with col4:
        st.metric("⚗️ pH Médio", f"{df['pH'].mean():.2f}" if 'pH' in df.columns else "N/A")
    
    # Análise Univariada
    st.markdown("### 📈 Análise Univariada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if all(col in df.columns for col in ['temp', 'hum', 'pH']):
            # Box plots para variáveis numéricas
            fig_box = px.box(df, y=['temp', 'hum', 'pH'],
                             title="📊 Distribuição das Variáveis Numéricas")
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("⚠️ Colunas necessárias não encontradas para o box plot")
    
    with col2:
        if 'temp' in df.columns:
            # Histogramas
            fig_hist = px.histogram(df, x='temp', title="🌡️ Distribuição da Temperatura", 
                                   nbins=20, color_discrete_sequence=['#32CD32'])
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("⚠️ Coluna 'temp' não encontrada")
    
    # Análise Bivariada
    st.markdown("### 🔍 Análise Bivariada")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if all(col in df.columns for col in ['temp', 'hum', 'estado_irrigacao']):
            # Scatter plot
            fig_scatter = px.scatter(df, x='temp', y='hum',
                                   color='estado_irrigacao',
                                   title="🌡️💧 Temperatura vs Umidade",
                                   labels={'temp': 'Temperatura (°C)', 'hum': 'Umidade (%)'})
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("⚠️ Colunas necessárias não encontradas para o scatter plot")
    
    with col4:
        if all(col in df.columns for col in ['pH', 'estado_irrigacao']):
            # Violin plot
            fig_violin = px.violin(df, y='pH', x='estado_irrigacao',
                                 title="⚗️ Distribuição do pH por Estado de Irrigação",
                                 labels={'pH': 'pH', 'estado_irrigacao': 'Estado de Irrigação'})
            fig_violin.update_layout(height=400)
            st.plotly_chart(fig_violin, use_container_width=True)
        else:
            st.warning("⚠️ Colunas necessárias não encontradas para o violin plot")
    
    # Análise de Correlação
    st.markdown("### 🔗 Análise de Correlação")
    
    if all(col in df.columns for col in ['temp', 'hum', 'pH']):
        numeric_cols = df[['temp', 'hum', 'pH']].corr()
        fig_corr = px.imshow(numeric_cols,
                           title="🔗 Mapa de Correlação entre Variáveis",
                           color_continuous_scale='RdBu',
                           aspect="auto")
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Interpretação da correlação
        st.markdown("""
        <div class="analysis-card">
            <h4>💡 Interpretação das Correlações</h4>
            <ul>
                <li><strong>Correlação positiva:</strong> Valores próximos a +1 indicam que as variáveis aumentam juntas</li>
                <li><strong>Correlação negativa:</strong> Valores próximos a -1 indicam que uma variável aumenta quando a outra diminui</li>
                <li><strong>Sem correlação:</strong> Valores próximos a 0 indicam que não há relação linear entre as variáveis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Colunas numéricas necessárias não encontradas para análise de correlação")

elif selected_analysis == "🤖 Modelo Preditivo":
    st.markdown('<h2 class="section-header">🤖 Modelo Preditivo</h2>', unsafe_allow_html=True)
    
    # Informações sobre o modelo
    st.markdown("""
    <div class="info-box">
        <h4>🎯 Sobre o Modelo Preditivo</h4>
        <p>Este modelo utiliza técnicas de Machine Learning para prever o comportamento do sistema de irrigação 
        baseado nas condições ambientais e do solo coletadas pelos sensores.</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Treinar modelo
        with st.spinner("🔄 Treinando modelo preditivo..."):
            analyzer = SensorDataAnalyzer()
            results = analyzer.train_model()
        
        # Métricas do modelo
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <h3>🎯 Acurácia do Modelo</h3>
                <h2 style="color: #228B22;">{:.2%}</h2>
            </div>
            """.format(results['accuracy']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-container">
                <h3>📊 Tipo de Modelo</h3>
                <h4 style="color: #228B22;">Random Forest</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-container">
                <h3>🔍 Variáveis Analisadas</h3>
                <h4 style="color: #228B22;">Temp, Umidade, pH</h4>
            </div>
            """, unsafe_allow_html=True)
        
        # Feature Importance
        st.markdown("### 📈 Importância das Variáveis")
        
        st.markdown("""
        <div class="analysis-card">
            <p>O gráfico abaixo mostra quais variáveis têm maior influência nas previsões do modelo. 
            Quanto maior a barra, mais importante é a variável para determinar o estado da irrigação.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'feature_importance' in results:
            fig_importance = px.bar(results['feature_importance'],
                                  x='feature', y='importance',
                                  title="📊 Importância das Variáveis no Modelo",
                                  labels={'feature': 'Variável', 'importance': 'Importância'},
                                  color='importance',
                                  color_continuous_scale='Viridis')
            fig_importance.update_layout(height=500)
            st.plotly_chart(fig_importance, use_container_width=True)
        
        # Previsões para as próximas 24 horas
        st.markdown("### 🔮 Previsões para as Próximas 24 Horas")
        
        try:
            predictions = analyzer.predict_next_24h()
            
            if predictions:
                # Converter previsões para DataFrame
                pred_df = pd.DataFrame(predictions)
                pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'])
                
                # Estatísticas das previsões
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_prob = pred_df['probabilidade'].mean()
                    st.metric("📊 Prob. Média", f"{avg_prob:.2%}")
                
                with col2:
                    max_prob = pred_df['probabilidade'].max()
                    st.metric("📈 Prob. Máxima", f"{max_prob:.2%}")
                
                with col3:
                    high_prob_count = len(pred_df[pred_df['probabilidade'] > 0.7])
                    st.metric("⚠️ Alertas (>70%)", high_prob_count)
                
                # Gráfico de probabilidade das previsões
                fig_pred = px.line(pred_df, x='timestamp', y='probabilidade',
                                 title="🔮 Probabilidade de Irrigação nas Próximas 24h",
                                 labels={'probabilidade': 'Probabilidade de Irrigação',
                                        'timestamp': 'Horário'},
                                 line_shape='spline')
                
                # Adicionar linha de referência
                fig_pred.add_hline(y=0.7, line_dash="dash", line_color="red", 
                                 annotation_text="Limiar de Alerta (70%)")
                
                fig_pred.update_layout(height=500)
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # Tabela com as previsões
                st.markdown("### 📋 Detalhes das Previsões")
                
                # Formatar a tabela
                pred_display = pred_df.copy()
                pred_display['probabilidade'] = pred_display['probabilidade'].apply(lambda x: f"{x:.2%}")
                pred_display['timestamp'] = pred_display['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
                
                # Selecionar apenas as colunas que queremos mostrar
                pred_display = pred_display[['timestamp', 'previsao', 'probabilidade']].copy()
                pred_display.columns = ['Data/Hora', 'Previsão', 'Probabilidade de Irrigação']
                
                st.dataframe(pred_display.reset_index(drop=True), use_container_width=True)
                
                # Recomendações baseadas nas previsões
                high_prob_periods = pred_df[pred_df['probabilidade'] > 0.7]
                
                if len(high_prob_periods) > 0:
                    st.markdown("""
                    <div class="analysis-card" style="border-left: 5px solid #FFC107;">
                        <h4>⚠️ Recomendações</h4>
                        <p>O modelo identificou <strong>{}</strong> período(s) com alta probabilidade de necessidade de irrigação (>70%). 
                        Monitore especialmente estes horários para otimizar o uso de recursos hídricos.</p>
                    </div>
                    """.format(len(high_prob_periods)), unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="analysis-card" style="border-left: 5px solid #28A745;">
                        <h4>✅ Status Normal</h4>
                        <p>As previsões indicam que não há períodos de alta necessidade de irrigação nas próximas 24 horas. 
                        Continue monitorando as condições do solo.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.warning("⚠️ Não foi possível gerar previsões. Verifique os dados dos sensores.")
        
        except Exception as e:
            st.error(f"❌ Erro ao gerar previsões: {e}")
    
    except Exception as e:
        st.error(f"❌ Erro ao treinar modelo: {e}")
        
        # Mostrar informações sobre o que seria exibido
        st.markdown("""
        <div class="analysis-card">
            <h4>📋 Funcionalidades do Modelo Preditivo</h4>
            <ul>
                <li><strong>Treinamento:</strong> Modelo Random Forest baseado em dados históricos</li>
                <li><strong>Variáveis:</strong> Temperatura, umidade e pH do solo</li>
                <li><strong>Previsão:</strong> Probabilidade de necessidade de irrigação</li>
                <li><strong>Período:</strong> Previsões para as próximas 24 horas</li>
                <li><strong>Alertas:</strong> Identificação de períodos críticos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Sidebar com informações adicionais
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Sobre as Análises")

if selected_analysis == "📊 Análise Exploratória":
    st.sidebar.markdown("""
    **Análise Exploratória:**
    - Distribuição das variáveis
    - Correlações entre sensores
    - Padrões nos dados
    - Outliers e anomalias
    """)
else:
    st.sidebar.markdown("""
    **Modelo Preditivo:**
    - Algoritmo Random Forest
    - Previsão de irrigação
    - Importância das variáveis
    - Alertas inteligentes
    """) 