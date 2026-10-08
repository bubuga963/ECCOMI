import os
import json
import pandas as pd
import streamlit as st

# 1. Configuração Base (Layout expandido e título)
st.set_page_config(
    page_title="Eccomi",
    layout="wide"
)

# 2. CSS Seguro (Apenas Cores Preto e Branco e Fonte Nunito - Sem hacks destrutivos)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    
    /* Aplica Nunito e fundo branco a toda a aplicação */
    .stApp, .stApp > header {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    
    h1, h2, h3, p, span, div, label {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
    }
    
    /* Tamanho de fonte seguro para leitura em campo (mínimo 14px na web para legibilidade mobile) */
    p, span, label, div {
        font-size: 14px !important;
    }

    /* Estilos das caixas de informação e cartões */
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

# 3. Criação de Pastas de Dados
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

# 4. Gestão de Navegação Sólida (Session State)
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
# ROTEAMENTO DAS PÁGINAS (SEM BARRA LATERAL)
# ==========================================

# --- PÁGINA INICIAL (HOME) ---
if st.session_state.pagina == 'home':
    st.markdown("<h1>ECCOMI</h1>", unsafe_allow_html=True)
    st.markdown("<p><b>Sistema B2B de Gestão de Eventos, Controle de Embarque e Segurança.</b></p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #000;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="card-evento">
            <h3>Bem-vindo ao Eccomi</h3>
            <p>A sua ferramenta cirúrgica de campo. Substitua planilhas de papel e grupos de WhatsApp por um controle rápido, alertas médicos imediatos e chamadas seguras. Selecione uma opção abaixo para começar:</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Espaçamento
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📁 Painel de Eventos", use_container_width=True): navegar('painel')
    with col2:
        if st.button("➕ Cadastrar Novo Evento", use_container_width=True): navegar('cadastrar')
    with col3:
        if st.button("🗄️ Arquivo e Ocorrências", use_container_width=True): navegar('arquivo')


# --- PAINEL GERAL DE EVENTOS ---
elif st.session_state.pagina == 'painel':
    if st.button("⬅ Voltar à Página Inicial"): navegar('home')
    
    st.markdown("<h1>PAINEL DE EVENTOS</h1>", unsafe_allow_html=True)
    categoria_evento = st.radio("Selecione o Tipo de Operação:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    
    PASTA_GRUPOS = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    cat_param = "viagens" if categoria_evento == "Viagens e Excursões" else "festas"
    grupos_disponiveis = listar_grupos(PASTA_GRUPOS)
    
    st.markdown("<hr style='border: 1px solid #000;'>", unsafe_allow_html=True)
    termo_busca = st.text_input("Buscar evento por nome:")
    
    if grupos_disponiveis:
        eventos_filtrados = [g for g in grupos_disponiveis if termo_busca.lower() in g.lower()] if termo_busca else grupos_disponiveis
        
        for g in eventos_filtrados:
            caminho_g = os.path.join(PASTA_GRUPOS, f"{g}.xlsx")
            caminho_inf_g = os.path.join(PASTA_INFO, f"{g}_info.json")
            
            total_p, presentes_p = 0, 0
            local_g, horario_g = "Não informado", "Não informado"
            
            if os.path.exists(caminho_g):
                try:
                    df_g = pd.read_excel(caminho_g)
                    total_p = len(df_g)
                    if 'Status Entrada' in df_g.columns:
                        presentes_p = len(df_g[df_g['Status Entrada'] == "Presente"])
                except: pass
            
            if os.path.exists(caminho_inf_g):
                try:
                    with open(caminho_inf_g, "r", encoding="utf-8") as f:
                        inf_j = json.load(f)
                        local_g = inf_j.get('local', 'Não informado')
                        horario_g = inf_j.get('horario', 'Não informado')
                except: pass

            st.markdown(f"""
                <div class="card-evento">
                    <h3 style="margin-bottom: 5px;">{g.replace('_', ' ')}</h3>
                    <p><b>Local:</b> {local_g} | <b>Horário/Data:</b> {horario_g}</p>
                    <p><b>Participantes:</b> {presentes_p} presentes de {total_p} no total</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Formato correto e limpo para os botões e upload no Streamlit
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button(f"Abrir: {g.replace('_', ' ')}", use_container_width=True): 
                    abrir_evento(g, cat_param)
            with col_b2:
                if st.button(f"Arquivar Evento", key=f"arq_{g}", use_container_width=True):
                    os.rename(caminho_g, os.path.join(PASTA_ARQUIVO, f"{g}.xlsx"))
                    st.rerun()
            with col_b3:
                if st.button(f"Excluir Evento", key=f"del_{g}", use_container_width=True):
                    os.remove(caminho_g)
                    if os.path.exists(caminho_inf_g): os.remove(caminho_inf_g)
                    st.rerun()
            
            # O Upload deve ficar num Expander nativo (parece um botão longo que abre para revelar o uploader)
            with st.expander("Atualizar Planilha do Evento (Upload)"):
                novo_excel = st.file_uploader(f"Substituir planilha para {g}:", type=["xlsx"], key=f"up_{g}")
                if novo_excel is not None:
                    df_novo = pd.read_excel(novo_excel)
                    df_novo.to_excel(caminho_g, index=False)
                    st.success("Planilha atualizada com sucesso!")
            
            st.markdown("<hr style='border: 1px solid #CCC;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento cadastrado nesta categoria.")


# --- ÁREA INTERNA DO EVENTO SELECIONADO ---
elif st.session_state.pagina == 'evento_interno' and st.session_state.evento_ativo:
    if st.button("⬅ Voltar ao Painel"): navegar('painel')
    
    g_ativo = st.session_state.evento_ativo
    pasta_alvo = PASTA_VIAGENS if st.session_state.cat_ativa == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{g_ativo}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{g_ativo}_info.json")
    
    if os.path.exists(caminho_arquivo):
        st.markdown(f"<h1>Evento: {g_ativo.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #000;'>", unsafe_allow_html=True)
        
        info_data = {}
        if os.path.exists(caminho_info):
            with open(caminho_info, "r", encoding="utf-8") as f: info_data = json.load(f)

        aba_info, aba_chamada, aba_saida = st.tabs(["Informações", "Entrada (Embarque)", "Saída (Desembarque)"])
        
        with aba_info:
            st.markdown("<h3>Detalhes do Evento</h3>", unsafe_allow_html=True)
            link_drive = info_data.get('drive_fotos', 'Não informado')
            link_html = f'<a href="{link_drive}" target="_blank">{link_drive}</a>' if link_drive.startswith('http') else link_drive
            
            st.markdown(f"""
                <div class="card-evento">
                    <b>Local:</b> {info_data.get('local', 'Não informado')}<br>
                    <b>Telefone Local:</b> {info_data.get('tel_local', 'Não informado')}<br>
                    <b>Horário:</b> {info_data.get('horario', 'Não informado')}<br>
                    <b>Roteiro:</b> {info_data.get('roteiro', 'Não informado')}<br>
                    <b>Transporte:</b> {info_data.get('transporte', 'Não informado')} | Motorista: {info_data.get('motorista', 'Não informado')}<br>
                    <b>Equipe:</b> {info_data.get('equipe', 'Não informado')}<br>
                    <b>Fotos/Drive:</b> {link_html}
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Editar Informações do Evento"):
                with st.form("form_info"):
                    loc = st.text_input("Local:", value=info_data.get('local', ''))
                    t_loc = st.text_input("Telefone:", value=info_data.get('tel_local', ''))
                    hor = st.text_input("Horário:", value=info_data.get('horario', ''))
                    rot = st.text_area("Roteiro:", value=info_data.get('roteiro', ''))
                    trans = st.text_input("Transporte/Placa:", value=info_data.get('transporte', ''))
                    mot = st.text_input("Motorista/Tel:", value=info_data.get('motorista', ''))
                    eqp = st.text_area("Equipe Responsável:", value=info_data.get('equipe', ''))
                    drive = st.text_input("Link Google Drive:", value=info_data.get('drive_fotos', ''))
                    if st.form_submit_button("Salvar Dados"):
                        novo_dict = {"local": loc, "tel_local": t_loc, "horario": hor, "roteiro": rot, "transporte": trans, "motorista": mot, "equipe": eqp, "drive_fotos": drive}
                        with open(caminho_info, "w", encoding="utf-8") as f: json.dump(novo_dict, f, ensure_ascii=False)
                        st.success("Salvo!")
                        st.rerun()

        df = pd.read_excel(caminho_arquivo)
        col_id = df.columns[0]
        col_nome = df.columns[1]
        col_ficha = df.columns[5] if len(df.columns) > 5 else df.columns[-1]
        
        if 'Status Entrada' not in df.columns: df['Status Entrada'] = "Pendente"
        if 'Status Saida' not in df.columns: df['Status Saida'] = "Pendente"

        with aba_chamada:
            pesquisa = st.text_input("Pesquisar nome/ID:", key="pesq_ent")
            df_filt = df[df[col_nome].astype(str).str.contains(pesquisa, case=False, na=False) | df[col_id].astype(str).str.contains(pesquisa, case=False, na=False)] if pesquisa else df
            
            st.markdown(f"<p><b>Total Presentes:</b> {len(df[df['Status Entrada'] == 'Presente'])} de {len(df)}</p>", unsafe_allow_html=True)
            with st.form("form_ent"):
                novos_status = {}
                for i, row in df_filt.iterrows():
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).lower() not in ["", "nao ha.", "nenhum"] else None
                    st.markdown(f"<div style
