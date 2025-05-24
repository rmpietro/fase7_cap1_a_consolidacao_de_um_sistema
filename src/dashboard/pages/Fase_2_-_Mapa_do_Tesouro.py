import streamlit as st
import os
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.parent

st.set_page_config(
    page_title="Fase 2 - Mapa do Tesouro",
    page_icon="🗺️",
    layout="wide"
)

st.markdown('<h1 class="main-header">🗺️ Fase 2 - Mapa do Tesouro</h1>', unsafe_allow_html=True)
st.info("Projeto de modelagem de dados para um sistema de armazenamento (banco de dados) e análise dos dados coletados por sensores agrícolas com o fim de prover informação, recomendação de ajustes imediatos ou previsões futuras na quantidade de insumos (incluindo água) aplicados na plantação.")

# Mostrar imagem do modelo relacional
modelo_relacional_path = str(root_dir / "src" / "fase2" / "mapa_tesouro" / "datamodeler" / "Modelo_Relacional_DataModeler.png")
if os.path.exists(modelo_relacional_path):
    st.image(modelo_relacional_path, caption="Modelo Relacional (DataModeler)", use_column_width=True)
else:
    st.warning("Imagem do Modelo Relacional não encontrada.")

# Mostrar imagem do DER
der_path = str(root_dir / "src" / "fase2" / "mapa_tesouro" / "wwwsqldesigner" / "farmtech_DER.png")
if os.path.exists(der_path):
    st.image(der_path, caption="DER (SQL Designer)", use_column_width=True)
else:
    st.warning("Imagem do DER não encontrada.")

# Mostrar DDL em expander
ddl_path = root_dir / "src" / "fase2" / "mapa_tesouro" / "wwwsqldesigner" / "farmtech_DDL.sql"
if os.path.exists(ddl_path):
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_content = f.read(2000)  # Mostra os primeiros 2000 caracteres
    with st.expander("Ver DDL completo (SQL)"):
        st.code(ddl_content, language="sql")
else:
    st.warning("Arquivo DDL não encontrado.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    🗺️ <strong>Fase 2 - Mapa do Tesouro</strong> - Modelagem de Dados Agrícolas
</div>
""", unsafe_allow_html=True) 