import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório pai ao PYTHONPATH
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configuração da página
st.set_page_config(
    page_title="Sistema Integrado de Gestão Agrícola",
    page_icon="🌾",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #228B22;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
        font-style: italic;
    }
    .system-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .system-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    .card-title {
        font-size: 1.5rem;
        color: #228B22;
        font-weight: bold;
        margin-bottom: 1rem;
        border-bottom: 2px solid #90EE90;
        padding-bottom: 0.5rem;
    }
    .card-description {
        color: #555;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .features-list {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #32CD32;
    }
    .welcome-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0fff0 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        border: 2px solid #90EE90;
    }
    .tech-stack {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        border-left: 5px solid #007BFF;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🌾 Sistema Integrado de Gestão Agrícola</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma Completa para Modernização da Agricultura</p>', unsafe_allow_html=True)

# Seção de boas-vindas
st.markdown("""
<div class="welcome-section">
    <h2>🎯 FIAP - Fase 7 - Sistema Integrado das Fases 1, 2, 3, 4 e 6 com um único Dashboard de Acesso</h2>
    <p style="font-size: 1.1rem; margin: 1rem 0;">
        Este sistema oferece acesso aos projetos entregues nas Fases 1, 2, 3, 4 e 6 por meio de páginas individualizadas e menus especializados nas funcionalidades de cada fase.
    </p>
    <p style="font-weight: bold; color: #228B22;">
        🚀 Explore todas as funcionalidades através do menu lateral!
    </p>
</div>
""", unsafe_allow_html=True)

# Integrantes - versão discreta
st.markdown("""
<div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 3px solid #228B22;">
    <p style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #666; font-weight: bold;">👥 Equipe:</p>
    <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem; color: #666;">
        <li>Gustavo Valtrick (RM559575)</li>
        <li>Iago Cotta (RM559655)</li>
        <li>Pedro Scofield (RM560589)</li>
        <li>Rodrigo Mastropietro (RM560081)</li>
        <li>Tiago de Andrade Bastos (RM560467)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sistemas disponíveis
st.markdown("## 📋 Módulos do Sistema")

# Fase 1 - Farm Tech
st.markdown("""
<div class="system-card">
    <div class="card-title">🏞️ Fase 1 - Farm Tech</div>
    <div class="card-description">
        Sistema especializado em medição e cálculo de áreas agrícolas com integração de dados meteorológicos 
        e análise estatística para cultivo de milho e cana-de-açúcar.
    </div>
    <div class="features-list">
        <h4>🔧 Principais Funcionalidades:</h4>
        <ul>
            <li><strong>📐 Medição de Terrenos:</strong> Cálculo preciso de áreas retangulares e triangulares</li>
            <li><strong>🌾 Gestão de Culturas:</strong> Especialização em milho e cana-de-açúcar</li>
            <li><strong>🧪 Cálculo de Insumos:</strong> Determinação automática de fertilizantes e defensivos</li>
            <li><strong>📊 Análise Estatística:</strong> Integração com R para relatórios avançados</li>
            <li><strong>🌤️ Dados Meteorológicos:</strong> Previsão do tempo para Presidente Prudente</li>
            <li><strong>📤 Exportação:</strong> Relatórios em CSV e visualizações de topografia</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Fase 2 - Python e Além - Silos
st.markdown("""
<div class="system-card">
    <div class="card-title">🏗️ Fase 2 - Python e Além - Silos</div>
    <div class="card-description">
        Plataforma completa para monitoramento e controle de qualidade de grãos em silos, 
        com alertas inteligentes e backup de dados.
    </div>
    <div class="features-list">
        <h4>🔧 Principais Funcionalidades:</h4>
        <ul>
            <li><strong>🗃️ Gestão de Silos:</strong> CRUD completo para registro e controle</li>
            <li><strong>🌾 Múltiplos Grãos:</strong> Suporte para Milho, Soja, Arroz, Trigo e Feijão</li>
            <li><strong>🌡️ Monitoramento:</strong> Controle de temperatura, umidade e pH</li>
            <li><strong>⚠️ Alertas Inteligentes:</strong> Notificações automáticas de qualidade</li>
            <li><strong>📊 Relatórios:</strong> Análises detalhadas de condições dos grãos</li>
            <li><strong>💾 Backup/Restore:</strong> Segurança de dados em formato JSON</li>
        </ul>
    </div>
    <div class="features-list" style="margin-top: 1.5rem; background-color: #e7f3ff; border-left: 4px solid #007BFF;">
        <h4>🗺️ Fase 2 - Mapa do Tesouro</h4>
        <div class="card-description">
            Página dedicada à modelagem de dados do sistema, apresentando o DDL, o modelo relacional e o DER do banco de dados agrícola.
        </div>
        <ul>
            <li><strong>📄 DDL Completo:</strong> Visualização do script SQL de criação das tabelas</li>
            <li><strong>🗺️ Modelo Relacional:</strong> Imagem do modelo relacional do banco</li>
            <li><strong>🔗 DER:</strong> Diagrama Entidade-Relacionamento (DER) ilustrativo</li>
            <li><strong>📝 Descrição do Projeto:</strong> Contextualização do objetivo da modelagem</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Fase 3 - Máquina Agrícola - Monitoramento de Culturas
st.markdown("""
<div class="system-card">
    <div class="card-title">🌱 Fase 3 - Máquina Agrícola - Monitoramento de Culturas</div>
    <div class="card-description">
        Sistema avançado de monitoramento com sensores IoT, análise de dados em tempo real 
        e automação de irrigação baseada em inteligência artificial.
    </div>
    <div class="features-list">
        <h4>🔧 Principais Funcionalidades:</h4>
        <ul>
            <li><strong>📡 Sensores IoT:</strong> Monitoramento de temperatura, umidade, pH, P e K</li>
            <li><strong>🗄️ Banco Oracle:</strong> Estrutura robusta com 4 tabelas relacionadas</li>
            <li><strong>💧 Automação:</strong> Sistema inteligente de controle de irrigação</li>
            <li><strong>📈 Visualizações:</strong> Gráficos interativos com Plotly</li>
            <li><strong>🌐 API Meteorológica:</strong> Integração com OpenWeatherMap</li>
            <li><strong>📊 Dashboard:</strong> Métricas em tempo real e alertas</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Fase 4 - Automação e Inteligência - Análise de Dados
st.markdown("""
<div class="system-card">
    <div class="card-title">📊 Fase 4 - Automação e Inteligência - Análise de Dados</div>
    <div class="card-description">
        Módulo de inteligência de dados com análise exploratória e modelos preditivos 
        para otimização das operações agrícolas.
    </div>
    <div class="features-list">
        <h4>🔧 Principais Funcionalidades:</h4>
        <ul>
            <li><strong>📊 Análise Exploratória:</strong> Distribuições, correlações e padrões</li>
            <li><strong>🤖 Machine Learning:</strong> Modelo Random Forest para previsões</li>
            <li><strong>🔮 Previsões:</strong> Probabilidade de irrigação nas próximas 24h</li>
            <li><strong>📈 Feature Importance:</strong> Identificação das variáveis mais relevantes</li>
            <li><strong>⚠️ Alertas Preditivos:</strong> Notificações baseadas em ML</li>
            <li><strong>📋 Recomendações:</strong> Sugestões automáticas de ações</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Fase 6 - Despertar da Rede Neural
st.markdown("""
<div class="system-card">
    <div class="card-title">🤖 Fase 6 - Despertar da Rede Neural</div>
    <div class="card-description">
        Sistema de visão computacional para detecção automática de objetos agrícolas (ex: copos e globos de neve) usando o modelo YOLOv5, com interface para treinamento customizado, validação, visualização de métricas e envio de alertas customizados via AWS SNS.
    </div>
    <div class="features-list">
        <h4>🔧 Principais Funcionalidades:</h4>
        <ul>
            <li><strong>🖼️ Upload e Gerenciamento de Dataset:</strong> Organização de imagens e labels para treinamento</li>
            <li><strong>🏋️ Treinamento Customizado:</strong> Interface para configurar e treinar modelos YOLOv5</li>
            <li><strong>✅ Validação e Métricas:</strong> Avaliação do modelo com métricas e gráficos interativos</li>
            <li><strong>📈 Visualização de Resultados:</strong> Exibição de imagens detectadas e logs do treinamento</li>
            <li><strong>📤 Envio de Alertas SNS:</strong> Disparo de mensagens customizadas para assinantes AWS SNS</li>
            <li><strong>🔄 Integração com Outras Fases:</strong> Possibilidade de uso dos resultados em outros módulos do sistema</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Tecnologias utilizadas
st.markdown("## 🛠️ Stack Tecnológico")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="tech-stack">
        <h4>💻 Frontend & Interface</h4>
        <ul>
            <li><strong>Streamlit:</strong> Framework web moderno</li>
            <li><strong>Plotly:</strong> Visualizações interativas</li>
            <li><strong>CSS3:</strong> Design responsivo</li>
            <li><strong>HTML:</strong> Estruturação de conteúdo</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tech-stack">
        <h4>🗃️ Backend & Dados</h4>
        <ul>
            <li><strong>Oracle Database:</strong> Banco de dados robusto</li>
            <li><strong>Pandas:</strong> Manipulação de dados</li>
            <li><strong>Scikit-learn:</strong> Machine Learning</li>
            <li><strong>OpenWeatherMap API:</strong> Dados meteorológicos</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Instruções de uso
st.markdown("## 🚀 Como Usar o Sistema")

st.markdown("""
<div class="welcome-section">
    <h3>📖 Guia de Navegação</h3>
    <ol style="text-align: left; max-width: 600px; margin: 0 auto;">
        <li><strong>Menu Lateral:</strong> Use a barra lateral para navegar entre os módulos</li>
        <li><strong>Credenciais:</strong> Para sistemas com banco Oracle, use suas credenciais FIAP</li>
        <li><strong>Dados de Teste:</strong> Cada módulo possui dados de exemplo pré-configurados</li>
        <li><strong>Exportação:</strong> Todos os relatórios podem ser exportados</li>
        <li><strong>Responsividade:</strong> Interface otimizada para desktop e mobile</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Estatísticas do sistema
st.markdown("## 📈 Estatísticas do Sistema")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0fff0; border-radius: 10px;">
        <h2 style="color: #228B22; margin: 0;">4</h2>
        <p style="margin: 0; color: #666;">Módulos Integrados</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0fff0; border-radius: 10px;">
        <h2 style="color: #228B22; margin: 0;">15+</h2>
        <p style="margin: 0; color: #666;">Funcionalidades</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0fff0; border-radius: 10px;">
        <h2 style="color: #228B22; margin: 0;">5</h2>
        <p style="margin: 0; color: #666;">Tipos de Grãos</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0fff0; border-radius: 10px;">
        <h2 style="color: #228B22; margin: 0;">24/7</h2>
        <p style="margin: 0; color: #666;">Monitoramento</p>
    </div>
    """, unsafe_allow_html=True)
