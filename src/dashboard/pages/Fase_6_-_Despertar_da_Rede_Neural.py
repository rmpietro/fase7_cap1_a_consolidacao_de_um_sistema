import streamlit as st
import pandas as pd
import sys
import os
import subprocess
import shutil
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yaml
import json
import time

# Adicionar import boto3 para integração AWS SNS
try:
    import boto3
except ImportError:
    boto3 = None

# Adicionar diretório pai ao PYTHONPATH para poder importar os módulos
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent.parent
fase6_dir = root_dir / "src" / "fase6"

if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
if str(fase6_dir) not in sys.path:
    sys.path.append(str(fase6_dir))

# Configuração da página
st.set_page_config(
    page_title="Fase 6 - Despertar da Rede Neural - Sistema de Detecção de Objetos",
    page_icon="🤖",
    layout="wide"
)

# CSS customizado para o tema de IA/ML
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E4057;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1f77b4;
        border-bottom: 2px solid #87CEEB;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    .metric-container {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .training-container {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        white-space: pre-wrap;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
    }
    .step-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Estado da sessão para armazenar dados
if 'yolo_setup_complete' not in st.session_state:
    st.session_state.yolo_setup_complete = False
if 'training_complete' not in st.session_state:
    st.session_state.training_complete = False
if 'validation_complete' not in st.session_state:
    st.session_state.validation_complete = False
if 'model_path' not in st.session_state:
    st.session_state.model_path = None
if 'training_log' not in st.session_state:
    st.session_state.training_log = []

# Funções auxiliares
def check_yolo_installation():
    """Verificar se o YOLOv5 está instalado"""
    yolo_path = fase6_dir / "yolov5"
    return yolo_path.exists() and (yolo_path / "train.py").exists()

def update_yaml_paths():
    """Atualizar paths no arquivo YAML para a estrutura atual do projeto"""
    yaml_path = fase6_dir / "copo_globo.yaml"
    
    if yaml_path.exists():
        # Lê o arquivo YAML atual
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualiza os caminhos para a estrutura local
        updated_content = f"""train: {fase6_dir}/images/train/
val: {fase6_dir}/images/val/
test: {fase6_dir}/test/

names: # Defina aqui as labels do seu dataset
  0: "COPO"
  1: "GLOBO DE NEVE"
  # ...
"""
        
        # Salva o arquivo atualizado
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True
    return False

def get_dataset_info():
    """Obter informações sobre o dataset"""
    info = {
        'train_images': 0,
        'val_images': 0,
        'train_labels': 0,
        'val_labels': 0
    }
    
    try:
        train_images_dir = fase6_dir / "images" / "train"
        val_images_dir = fase6_dir / "images" / "val"
        train_labels_dir = fase6_dir / "labels" / "train"
        val_labels_dir = fase6_dir / "labels" / "val"
        
        if train_images_dir.exists():
            info['train_images'] = len([f for f in train_images_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']])
        
        if val_images_dir.exists():
            info['val_images'] = len([f for f in val_images_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']])
        
        if train_labels_dir.exists():
            info['train_labels'] = len([f for f in train_labels_dir.iterdir() if f.is_file() and f.suffix.lower() == '.txt'])
        
        if val_labels_dir.exists():
            info['val_labels'] = len([f for f in val_labels_dir.iterdir() if f.is_file() and f.suffix.lower() == '.txt'])
    
    except Exception as e:
        st.error(f"Erro ao obter informações do dataset: {e}")
    
    return info

def clone_yolo_repository():
    """Clonar o repositório YOLOv5"""
    try:
        yolo_path = fase6_dir / "yolov5"
        if yolo_path.exists():
            shutil.rmtree(yolo_path)
        
        # Mudar para o diretório fase6 antes de clonar
        original_cwd = os.getcwd()
        os.chdir(fase6_dir)
        
        result = subprocess.run(
            ['git', 'clone', 'https://github.com/ultralytics/yolov5.git'],
            capture_output=True,
            text=True,
            cwd=fase6_dir
        )
        
        os.chdir(original_cwd)
        
        return result.returncode == 0, result.stderr if result.returncode != 0 else "YOLOv5 clonado com sucesso!"
    
    except Exception as e:
        return False, str(e)

def install_dependencies():
    """Instalar dependências do YOLOv5"""
    try:
        requirements_path = fase6_dir / "yolov5" / "requirements.txt"
        
        if not requirements_path.exists():
            return False, "Arquivo requirements.txt não encontrado"
        
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0, result.stderr if result.returncode != 0 else "Dependências instaladas com sucesso!"
    
    except Exception as e:
        return False, str(e)

def train_model(img_size='640', batch_size='16', epochs='50', weights='yolov5s.pt'):
    """Treinar o modelo YOLOv5"""
    try:
        yaml_path = fase6_dir / "copo_globo.yaml"
        train_script = fase6_dir / "yolov5" / "train.py"
        
        if not train_script.exists():
            return False, "Script de treinamento não encontrado", None
        
        if not yaml_path.exists():
            return False, "Arquivo YAML de configuração não encontrado", None
        
        # Comando de treinamento
        cmd = [
            sys.executable, str(train_script),
            '--img', img_size,
            '--batch', batch_size,
            '--epochs', epochs,
            '--data', str(yaml_path),
            '--weights', weights,
            '--project', str(fase6_dir / 'runs' / 'train'),
            '--name', 'exp',
            '--exist-ok'
        ]
        
        # Executar treinamento (sem timeout para permitir treinamentos longos)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(fase6_dir),
            timeout=None  # Sem timeout
        )
        
        # Encontrar o caminho do modelo treinado
        model_path = None
        runs_dir = fase6_dir / 'runs' / 'train' / 'exp'
        if runs_dir.exists():
            weights_dir = runs_dir / 'weights'
            if weights_dir.exists():
                best_weights = weights_dir / 'best.pt'
                if best_weights.exists():
                    model_path = str(best_weights)
        
        success = result.returncode == 0
        
        # Preparar mensagem de retorno
        if success:
            message = "Treinamento concluído com sucesso!\n\n"
            if result.stdout:
                # Pegar apenas as últimas linhas do output para não sobrecarregar a interface
                stdout_lines = result.stdout.split('\n')
                last_lines = stdout_lines[-20:] if len(stdout_lines) > 20 else stdout_lines
                message += "=== Últimas linhas do log ===\n" + '\n'.join(last_lines)
        else:
            message = f"Erro no treinamento (código: {result.returncode})\n\n"
            if result.stderr:
                message += "=== Erro ===\n" + result.stderr
            if result.stdout:
                message += "\n=== Output ===\n" + result.stdout
        
        return success, message, model_path
    
    except subprocess.TimeoutExpired:
        return False, "Treinamento interrompido por timeout", None
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}", None

def validate_model(model_path, img_size='640'):
    """Validar o modelo treinado"""
    try:
        yaml_path = fase6_dir / "copo_globo.yaml"
        val_script = fase6_dir / "yolov5" / "val.py"
        
        if not val_script.exists():
            return False, "Script de validação não encontrado"
        
        if not model_path or not Path(model_path).exists():
            return False, "Modelo treinado não encontrado"
        
        # Comando de validação
        cmd = [
            sys.executable, str(val_script),
            '--weights', model_path,
            '--data', str(yaml_path),
            '--img', img_size,
            '--task', 'test'
        ]
        
        # Executar validação
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(fase6_dir)
        )
        
        success = result.returncode == 0
        message = result.stdout if success else result.stderr
        
        return success, message
    
    except Exception as e:
        return False, str(e)

# Header principal
st.markdown('<h1 class="main-header">🤖 Fase 6 - Despertar da Rede Neural</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Sistema de Detecção de Objetos - Copo e Globo de Neve</h2>', unsafe_allow_html=True)

# Informações sobre o sistema
st.markdown("""
<div class="info-box">
    <h4>📋 Despertar da Rede Neural</h4>
    <p>Este sistema implementa o treinamento de um modelo YOLOv5 para detecção de objetos, especificamente 
    <strong>copos</strong> e <strong>globos de neve</strong>. O processo inclui clonagem do repositório, 
    instalação de dependências, treinamento do modelo e validação dos resultados.</p>
    
    <h5>🎯 Classes do Dataset:</h5>
    <ul>
        <li><strong>COPO</strong> (Classe 0)</li>
        <li><strong>GLOBO DE NEVE</strong> (Classe 1)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sidebar para navegação
st.sidebar.title("🔧 Menu do Sistema")
menu_options = [
    "🏠 Início",
    "📊 Informações do Dataset",
    "⚙️ Setup do YOLOv5",
    "🚀 Treinamento do Modelo",
    "✅ Validação do Modelo",
    "📈 Resultados e Métricas",
    "📤 Enviar Alerta SNS"  # Novo item de menu
]

selected_option = st.sidebar.selectbox("Selecione uma opção:", menu_options)

# Verificações de status
yolo_installed = check_yolo_installation()
dataset_info = get_dataset_info()

# Conteúdo principal baseado na opção selecionada
if selected_option == "🏠 Início":
    st.markdown('<h2 class="section-header">🤖 Bem-vindo ao Sistema YOLOv5</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4>📁 Status do YOLOv5</h4>
            <p>{'✅ Instalado' if yolo_installed else '❌ Não instalado'}</p>
            <p>Repositório YOLOv5</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4>🏋️ Treinamento</h4>
            <p>{'✅ Concluído' if st.session_state.training_complete else '⏳ Pendente'}</p>
            <p>Status do modelo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4>✅ Validação</h4>
            <p>{'✅ Concluída' if st.session_state.validation_complete else '⏳ Pendente'}</p>
            <p>Teste do modelo</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Exibir estrutura do dataset
    st.markdown('<h3 class="section-header">📂 Estrutura do Projeto</h3>', unsafe_allow_html=True)
    
    project_structure = f"""
    📁 fase6/
    ├── 📁 images/
    │   ├── 📁 train/ ({dataset_info['train_images']} imagens)
    │   └── 📁 val/ ({dataset_info['val_images']} imagens)
    ├── 📁 labels/
    │   ├── 📁 train/ ({dataset_info['train_labels']} labels)
    │   └── 📁 val/ ({dataset_info['val_labels']} labels)
    ├── 📁 test/
    ├── 📄 copo_globo.yaml
    └── 📄 TiagoAndradeBastos_rm560467_pbl_fase6.ipynb
    """
    
    st.markdown(f"""
    <div class="training-container">
{project_structure}
    </div>
    """, unsafe_allow_html=True)

elif selected_option == "📊 Informações do Dataset":
    st.markdown('<h2 class="section-header">📊 Informações do Dataset</h2>', unsafe_allow_html=True)
    
    # Métricas do dataset
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏋️ Imagens de Treino", dataset_info['train_images'])
    
    with col2:
        st.metric("✅ Imagens de Validação", dataset_info['val_images'])
    
    with col3:
        st.metric("🏷️ Labels de Treino", dataset_info['train_labels'])
    
    with col4:
        st.metric("🏷️ Labels de Validação", dataset_info['val_labels'])
    
    # Gráfico da distribuição
    if dataset_info['train_images'] > 0 or dataset_info['val_images'] > 0:
        fig = go.Figure(data=[
            go.Bar(name='Imagens', x=['Treino', 'Validação'], y=[dataset_info['train_images'], dataset_info['val_images']]),
            go.Bar(name='Labels', x=['Treino', 'Validação'], y=[dataset_info['train_labels'], dataset_info['val_labels']])
        ])
        fig.update_layout(barmode='group', title="Distribuição do Dataset")
        st.plotly_chart(fig, use_container_width=True)
    
    # Verificar arquivo YAML
    yaml_path = fase6_dir / "copo_globo.yaml"
    if yaml_path.exists():
        st.markdown("### 📄 Configuração do Dataset (YAML)")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        st.code(yaml_content, language='yaml')
        
        if st.button("🔄 Atualizar Caminhos do YAML"):
            if update_yaml_paths():
                st.success("✅ Caminhos do YAML atualizados com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar caminhos do YAML")

elif selected_option == "⚙️ Setup do YOLOv5":
    st.markdown('<h2 class="section-header">⚙️ Setup do YOLOv5</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-box">
        <h4>📋 Passos do Setup</h4>
        <ol>
            <li>Clonar repositório YOLOv5 do GitHub</li>
            <li>Instalar dependências necessárias</li>
            <li>Configurar caminhos do dataset</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Status atual
    if yolo_installed:
        st.success("✅ YOLOv5 já está instalado e configurado!")
    else:
        st.warning("⚠️ YOLOv5 não está instalado. Execute o setup abaixo.")
    
    # Passo 1: Clonar repositório
    st.markdown("### 1️⃣ Clonar Repositório YOLOv5")
    
    if st.button("📥 Clonar YOLOv5", use_container_width=True):
        with st.spinner("⏳ Clonando repositório YOLOv5..."):
            success, message = clone_yolo_repository()
            
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ Erro: {message}")
    
    # Passo 2: Instalar dependências
    st.markdown("### 2️⃣ Instalar Dependências")
    
    if yolo_installed:
        if st.button("📦 Instalar/Atualizar Dependências", use_container_width=True):
            with st.spinner("⏳ Instalando dependências..."):
                success, message = install_dependencies()
                
                if success:
                    st.success(f"✅ {message}")
                    st.session_state.yolo_setup_complete = True
                else:
                    st.error(f"❌ Erro: {message}")
    else:
        st.info("ℹ️ Clone o repositório primeiro antes de instalar dependências.")
    
    # Passo 3: Configurar YAML
    st.markdown("### 3️⃣ Configurar Dataset")
    
    if st.button("⚙️ Atualizar Configuração do Dataset", use_container_width=True):
        if update_yaml_paths():
            st.success("✅ Configuração do dataset atualizada!")
        else:
            st.error("❌ Erro ao atualizar configuração")

elif selected_option == "🚀 Treinamento do Modelo":
    st.markdown('<h2 class="section-header">🚀 Treinamento do Modelo YOLOv5</h2>', unsafe_allow_html=True)
    
    if not yolo_installed:
        st.error("❌ YOLOv5 não está instalado. Execute o setup primeiro.")
        st.stop()
    
    # Verificar se existe um treinamento em andamento
    runs_dir = fase6_dir / 'runs' / 'train' / 'exp'
    if runs_dir.exists():
        st.markdown("""
        <div class="warning-message">
            <h4>⚠️ Atenção</h4>
            <p>Existe uma pasta de resultados de treinamento anterior. 
            Um novo treinamento irá sobrescrever os resultados anteriores.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Parâmetros de treinamento
    st.markdown("### ⚙️ Configurações de Treinamento")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        img_size = st.selectbox("Tamanho da Imagem", ['416', '640', '832'], index=1)
    
    with col2:
        batch_size = st.selectbox("Batch Size", ['8', '16', '32', '64'], index=1)
    
    with col3:
        epochs = st.selectbox("Épocas", ['10', '25', '50', '100'], index=2)
    
    with col4:
        weights = st.selectbox("Pesos Base", ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt'], index=0)
    
    # Informações sobre o treinamento
    st.markdown("""
    <div class="info-box">
        <h4>📝 Informações do Treinamento</h4>
        <p><strong>Dataset:</strong> COPO_GLOBO (Copos e Globos de Neve)</p>
        <p><strong>Arquitetura:</strong> YOLOv5 (You Only Look Once)</p>
        <p><strong>Otimizador:</strong> SGD com momentum</p>
        <p><strong>Função de Perda:</strong> Combinação de classificação, localização e confiança</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Estimativa de tempo
    st.markdown("### ⏱️ Estimativa de Tempo de Treinamento")
    
    time_estimates = {
        '10': "2-5 minutos",
        '25': "5-10 minutos", 
        '50': "10-20 minutos",
        '100': "20-40 minutos"
    }
    
    estimated_time = time_estimates.get(epochs, "Tempo variável")
    
    st.info(f"⏱️ **Tempo estimado para {epochs} épocas:** {estimated_time} (pode variar dependendo do hardware)")
    
    # Botão de treinamento
    if st.button("🚀 Iniciar Treinamento", use_container_width=True, type="primary"):
        # Verificações pré-treinamento
        if dataset_info['train_images'] == 0:
            st.error("❌ Nenhuma imagem de treino encontrada!")
            st.stop()
        
        if dataset_info['train_labels'] == 0:
            st.error("❌ Nenhum label de treino encontrado!")
            st.stop()
        
        # Iniciar treinamento
        st.info(f"🏋️ Iniciando treinamento com {epochs} épocas. Este processo pode levar vários minutos...")
        
        # Container para mostrar informações durante o treinamento
        info_container = st.container()
        
        with info_container:
            st.write("⏱️ **Tempo estimado:** O treinamento pode levar de 5 a 30 minutos dependendo do hardware e número de épocas.")
            st.write("🔄 **Status:** Processando...")
            st.write(f"🚀 **Comando:** `python train.py --img {img_size} --batch {batch_size} --epochs {epochs} --data copo_globo.yaml --weights {weights}`")
            st.write("⚠️ **Importante:** O treinamento está rodando em segundo plano. Não feche esta aba!")
        
        with st.spinner("⏳ Executando treinamento do modelo YOLOv5... Por favor, aguarde..."):
            success, message, model_path = train_model(img_size, batch_size, epochs, weights)
            
            if success:
                st.success("✅ Treinamento concluído com sucesso!")
                st.session_state.training_complete = True
                st.session_state.model_path = model_path
                
                # Exibir log do treinamento
                st.markdown("### 📊 Log do Treinamento")
                st.code(message, language='text')
                
                if model_path:
                    st.info(f"📁 Modelo salvo em: {model_path}")
                    
                # Botão para ir para validação
                if st.button("➡️ Ir para Validação", use_container_width=True):
                    st.session_state.selected_option = "✅ Validação do Modelo"
                    st.rerun()
            else:
                st.error(f"❌ Erro no treinamento: {message}")
                
                # Mostrar sugestões de resolução
                st.markdown("""
                <div class="warning-message">
                    <h4>🔧 Possíveis Soluções:</h4>
                    <ul>
                        <li>Reduza o batch size se houver erro de memória</li>
                        <li>Verifique se há espaço suficiente em disco</li>
                        <li>Certifique-se de que as imagens e labels estão corretos</li>
                        <li>Tente usar menos épocas para testes iniciais</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

elif selected_option == "✅ Validação do Modelo":
    st.markdown('<h2 class="section-header">✅ Validação do Modelo</h2>', unsafe_allow_html=True)
    
    if not st.session_state.training_complete:
        st.warning("⚠️ Execute o treinamento do modelo primeiro.")
        st.stop()
    
    if not st.session_state.model_path:
        st.error("❌ Caminho do modelo não encontrado.")
        st.stop()
    
    st.markdown(f"""
    <div class="info-box">
        <h4>🎯 Validação do Modelo</h4>
        <p><strong>Modelo:</strong> {st.session_state.model_path}</p>
        <p><strong>Dataset de Teste:</strong> {dataset_info['val_images']} imagens</p>
        <p><strong>Classes:</strong> COPO, GLOBO DE NEVE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configurações de validação
    img_size_val = st.selectbox("Tamanho da Imagem para Validação", ['416', '640', '832'], index=1, key="val_img_size")
    
    if st.button("🔍 Iniciar Validação", use_container_width=True, type="primary"):
        with st.spinner("⏳ Executando validação do modelo..."):
            success, message = validate_model(st.session_state.model_path, img_size_val)
            
            if success:
                st.success("✅ Validação concluída com sucesso!")
                st.session_state.validation_complete = True
                
                # Exibir resultados da validação
                st.markdown("### 📊 Resultados da Validação")
                st.code(message, language='text')
                
                # Tentar extrair métricas do resultado
                lines = message.split('\n')
                metrics = {}
                for line in lines:
                    if 'mAP' in line:
                        st.metric("Mean Average Precision (mAP)", line.split(':')[-1].strip())
                    elif 'Precision' in line:
                        st.metric("Precisão", line.split(':')[-1].strip())
                    elif 'Recall' in line:
                        st.metric("Recall", line.split(':')[-1].strip())
            else:
                st.error(f"❌ Erro na validação: {message}")

elif selected_option == "📈 Resultados e Métricas":
    st.markdown('<h2 class="section-header">📈 Resultados e Métricas</h2>', unsafe_allow_html=True)
    
    if not st.session_state.validation_complete:
        st.warning("⚠️ Execute a validação do modelo primeiro para ver os resultados.")
        st.stop()
    
    # Verificar se há resultados salvos
    runs_dir = fase6_dir / 'runs' / 'train' / 'exp'
    
    if runs_dir.exists():
        # Exibir métricas de treinamento
        st.markdown("### 📊 Métricas de Treinamento")
        
        # Procurar por arquivos de resultado
        results_file = runs_dir / 'results.csv'
        if results_file.exists():
            try:
                results_df = pd.read_csv(results_file)
                
                # Gráficos de treinamento
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'train/box_loss' in results_df.columns:
                        fig = px.line(results_df, y='train/box_loss', title='Loss de Localização')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'train/obj_loss' in results_df.columns:
                        fig = px.line(results_df, y='train/obj_loss', title='Loss de Objetividade')
                        st.plotly_chart(fig, use_container_width=True)
                
                # Exibir tabela de resultados
                st.markdown("### 📋 Tabela de Resultados")
                st.dataframe(results_df.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erro ao carregar resultados: {e}")
        
        # Verificar se há imagens de resultado
        st.markdown("### 🖼️ Exemplos de Detecção")
        
        # Procurar por imagens de resultado
        results_img_dir = runs_dir
        image_files = []
        
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(list(results_img_dir.glob(ext)))
        
        if image_files:
            selected_image = st.selectbox("Selecione uma imagem de resultado:", [img.name for img in image_files])
            
            if selected_image:
                selected_path = results_img_dir / selected_image
                st.image(str(selected_path), caption=selected_image, use_column_width=True)
        else:
            st.info("ℹ️ Nenhuma imagem de resultado encontrada.")
    
    else:
        st.info("ℹ️ Nenhum resultado de treinamento encontrado.")
    
    # Resumo final
    st.markdown("### 🎯 Resumo do Projeto")
    
    summary_data = {
        'Métrica': [
            'Dataset de Treino',
            'Dataset de Validação',
            'Classes',
            'Modelo Base',
            'Status do Treinamento',
            'Status da Validação'
        ],
        'Valor': [
            f"{dataset_info['train_images']} imagens",
            f"{dataset_info['val_images']} imagens",
            "COPO, GLOBO DE NEVE",
            "YOLOv5",
            "✅ Concluído" if st.session_state.training_complete else "❌ Pendente",
            "✅ Concluída" if st.session_state.validation_complete else "❌ Pendente"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
