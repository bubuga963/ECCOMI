import os
import json
import io
import pandas as pd
import streamlit as st

# 1. Configuração de Página com suporte nativo completo
st.set_page_config(
    page_title="Eccomi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Limpo (Permite a renderização correta de fontes e ícones nativos do Streamlit)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }

    h1, h2, h3, p, span, div, label {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
    }

    p, span, label, div {
        font-size: 14px !important;
    }

    .card-evento {
        border: 1px solid #000000;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 15px;
        background-color: #FFFFFF;
    }
    
    .alerta-medico {
        border: 2px solid #000000;
        padding: 10px;
        font-weight: bold;
        margin-top: 5px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Gerenciamento de Pastas
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

# 4. Estado de Navegação
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'evento_ativo' not in st.session_state:
    st.session_state.evento_ativo = None
if 'cat_ativa' not in st.session_state:
    st.session_state.cat_ativa = None

def navegar(destino):
    st.session_state.pagina = destino
    st.rerun()

def abrir_evento(evento, cat):
    st.session_state.evento_ativo = evento
    st.session_state.cat_ativa = cat
    st.session_state.pagina = 'evento_interno'
    st.rerun()

def listar_grupos(pasta):
    if os.path.exists(pasta):
        return sorted([f.replace(".xlsx", "") for f in os.listdir(pasta) if f.endswith(".xlsx")])
    return []

# ==========================================
# BARRA LATERAL NATIVA (Ícones do sistema habilitados)
# ==========================================
with st.sidebar:
    st.markdown("## ECCOMI")
    st.markdown("---")
    st.markdown("### Menu Principal")
    if st.button("Página Inicial", use_container_width=True):
        navegar('home')
    if st.button("Painel de Eventos", use_container_width=True):
        navegar('painel')
    if st.button("Cadastrar Evento", use_container_width=True):
        navegar('cadastrar')
    if st.button("Eventos Arquivados", use_container_width=True):
        navegar('arquivo')


# ==========================================
# ESTRUTURA DAS PÁGINAS
# ==========================================

# --- 1. PÁGINA INICIAL (HOME) ---
if st.session_state.pagina == 'home':
    st.markdown("<h1>ECCOMI</h1>", unsafe_allow_html=True)
    st.markdown("<p><b>Sistema B2B de Gestão de Eventos, Controle de Embarque e Segurança.</b></p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #000;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="card-evento">
            <h3>Bem-vindo ao Eccomi</h3>
            <p>Plataforma operacional desenvolvida para agências de turismo, excursões e escolas. Elimine planilhas de papel em campo com chamadas rápidas, alertas médicos em destaque e relatórios de embarque seguros.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    col1, col2, col
