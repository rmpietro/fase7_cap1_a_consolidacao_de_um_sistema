import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

# Adicionar import boto3 para integração AWS SNS
try:
    import boto3
except ImportError:
    boto3 = None

st.set_page_config(
    page_title="Enviar Alerta SNS",
    page_icon="📤",
    layout="wide"
)

st.markdown('<h1 class="main-header">📤 Enviar Alerta SNS</h1>', unsafe_allow_html=True)
st.info("Envie uma mensagem customizada para todos os assinantes do tópico SNS configurado na AWS.")

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

if boto3 is None:
    st.error("O pacote boto3 não está instalado. Por favor, instale com: pip install boto3")
else:
    # Formulário para adicionar novo assinante de email
    with st.form("sns_add_subscriber_form"):
        st.markdown("#### ➕ Adicionar novo assinante de email")
        new_email = st.text_input("Email do novo assinante", value="")
        add_submitted = st.form_submit_button("Adicionar Assinante")

    if add_submitted and new_email:
        try:
            sns = boto3.client(
                'sns',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
            response = sns.subscribe(
                TopicArn='arn:aws:sns:us-east-1:102792232287:alerta-sensor-fase3',
                Protocol='email',
                Endpoint=new_email,
                ReturnSubscriptionArn=True
            )
            st.success(f"Convite enviado para {new_email}. Peça para o usuário confirmar o email recebido da AWS para ativar a assinatura.")
        except Exception as e:
            st.error(f"Erro ao adicionar assinante: {e}")

    # Formulário para mensagem customizada
    with st.form("sns_form"):
        st.markdown("#### ✉️ Enviar mensagem customizada")
        subject = st.text_input("Assunto da Mensagem", value="Alerta do Sistema YOLOv5")
        message = st.text_area("Mensagem", value="Digite sua mensagem de alerta aqui.")
        submitted = st.form_submit_button("Enviar Mensagem")

    if submitted:
        try:
            sns = boto3.client(
                'sns',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
            response = sns.publish(
                TopicArn='arn:aws:sns:us-east-1:102792232287:alerta-sensor-fase3',
                Message=message,
                Subject=subject
            )
            st.success(f"Mensagem enviada com sucesso! MessageId: {response['MessageId']}")
        except Exception as e:
            st.error(f"Erro ao enviar mensagem SNS: {e}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    📤 <strong>Envio de Alerta SNS</strong> - Notificações AWS para o projeto FIAP
</div>
""", unsafe_allow_html=True) 