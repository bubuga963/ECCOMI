import os
import json
import pandas as pd
import streamlit as st

# 1. Configuração da Página (Layout Limpo sem chamada de Sidebar)
st.set_page_config(
    page_title="Eccomi",
    layout="wide"
)

# 2. CSS Estrito: Cores Preto e Branco, Fonte Nunito, Sem Hacks Destrutivos
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

    .stApp, .stApp > header {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* Força ocultação total de qualquer elemento de barra lateral que o Streamlit tente injetar */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], div[data-testid="collapsedControl"] {
        display: none !important;
        width: 0 !important;
        visibility: hidden !important;
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

# 3. Criação e Verificação das Pastas de Dados
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

# 4. Controle de Navegação via Session State (Sem dependência de URL)
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
# ROTEAMENTO E PÁGINAS DO SISTEMA
# ==========================================

# --- 1. PÁGINA INICIAL REAL (HOME) ---
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
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Painel de Eventos", use_container_width=True): 
            navegar('painel')
    with col2:
        if st.button("Cadastrar Novo Evento", use_container_width=True): 
            navegar('cadastrar')
    with col3:
        if st.button("Arquivo e Ocorrências", use_container_width=True): 
            navegar('arquivo')


# --- 2. PAINEL DE EVENTOS ---
elif st.session_state.pagina == 'painel':
    if st.button("Voltar à Página Inicial"): 
        navegar('home')
    
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
                except:
                    pass
            
            if os.path.exists(caminho_inf_g):
                try:
                    with open(caminho_inf_g, "r", encoding="utf-8") as f:
                        inf_j = json.load(f)
                        local_g = inf_j.get('local', 'Não informado')
                        horario_g = inf_j.get('horario', 'Não informado')
                except:
                    pass

            st.markdown(f"""
                <div class="card-evento">
                    <h3 style="margin-bottom: 5px;">{g.replace('_', ' ')}</h3>
                    <p><b>Local:</b> {local_g} | <b>Horário/Data:</b> {horario_g}</p>
                    <p><b>Participantes:</b> {presentes_p} presentes de {total_p} no total</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Botões Nativos e Alinhados
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button(f"Abrir Evento", key=f"btn_{g}", use_container_width=True): 
                    abrir_evento(g, cat_param)
            with col_b2:
                if st.button("Arquivar Evento", key=f"arq_{g}", use_container_width=True):
                    os.rename(caminho_g, os.path.join(PASTA_ARQUIVO, f"{g}.xlsx"))
                    st.rerun()
            with col_b3:
                if st.button("Excluir Evento", key=f"del_{g}", use_container_width=True):
                    os.remove(caminho_g)
                    if os.path.exists(caminho_inf_g): 
                        os.remove(caminho_inf_g)
                    st.rerun()
            
            # Resolução do Upload via Expander Nativo
            with st.expander("Atualizar Planilha do Evento (Upload)"):
                novo_excel = st.file_uploader(f"Substituir planilha (.xlsx) para {g}:", type=["xlsx"], key=f"up_{g}")
                if novo_excel is not None:
                    df_novo = pd.read_excel(novo_excel)
                    df_novo.to_excel(caminho_g, index=False)
                    st.success("Planilha atualizada com sucesso!")
            
            st.markdown("<hr style='border: 1px solid #CCC;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento cadastrado nesta categoria.")


# --- 3. ÁREA INTERNA DO EVENTO SELECIONADO ---
elif st.session_state.pagina == 'evento_interno' and st.session_state.evento_ativo:
    if st.button("Voltar ao Painel"): 
        navegar('painel')
    
    g_ativo = st.session_state.evento_ativo
    pasta_alvo = PASTA_VIAGENS if st.session_state.cat_ativa == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{g_ativo}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{g_ativo}_info.json")
    
    if os.path.exists(caminho_arquivo):
        st.markdown(f"<h1>Evento: {g_ativo.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #000;'>", unsafe_allow_html=True)
        
        info_data = {}
        if os.path.exists(caminho_info):
            with open(caminho_info, "r", encoding="utf-8") as f: 
                info_data = json.load(f)

        aba_info, aba_chamada, aba_saida = st.tabs(["Informações e Logística", "Entrada (Embarque)", "Saída (Desembarque)"])
        
        with aba_info:
            st.markdown("<h3>Detalhes Operacionais</h3>", unsafe_allow_html=True)
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
                        with open(caminho_info, "w", encoding="utf-8") as f: 
                            json.dump(novo_dict, f, ensure_ascii=False)
                        st.success("Salvo com sucesso!")
                        st.rerun()

        df = pd.read_excel(caminho_arquivo)
        col_id = df.columns[0]
        col_nome = df.columns[1]
        col_ficha = df.columns[5] if len(df.columns) > 5 else df.columns[-1]
        
        if 'Status Entrada' not in df.columns: 
            df['Status Entrada'] = "Pendente"
        if 'Status Saida' not in df.columns: 
            df['Status Saida'] = "Pendente"

        with aba_chamada:
            pesquisa = st.text_input("Pesquisar nome/ID:", key="pesq_ent")
            df_filt = df[df[col_nome].astype(str).str.contains(pesquisa, case=False, na=False) | df[col_id].astype(str).str.contains(pesquisa, case=False, na=False)] if pesquisa else df
            
            st.markdown(f"<p><b>Total Presentes:</b> {len(df[df['Status Entrada'] == 'Presente'])} de {len(df)}</p>", unsafe_allow_html=True)
            with st.form("form_ent"):
                novos_status = {}
                for i, row in df_filt.iterrows():
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).lower() not in ["", "nao ha.", "nenhum"] else None
                    st.markdown(f"<div><b>{row[col_id]} - {row[col_nome]}</b></div>", unsafe_allow_html=True)
                    s_atual = str(row['Status Entrada']) if pd.notna(row['Status Entrada']) else "Pendente"
                    novos_status[i] = st.radio(
                        f"Status para {row[col_nome]}:", 
                        ["Pendente", "Presente", "Faltou"], 
                        index=["Pendente", "Presente", "Faltou"].index(s_atual) if s_atual in ["Pendente", "Presente", "Faltou"] else 0, 
                        key=f"ent_{i}", 
                        horizontal=True, 
                        label_visibility="collapsed"
                    )
                    if ficha: 
                        st.markdown(f"<div class='alerta-medico'>ALERTA MÉDICO: {ficha}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='border: 0.5px solid #CCC;'>", unsafe_allow_html=True)
                
                if st.form_submit_button("Salvar Chamada de Entrada"):
                    for idx, val in novos_status.items(): 
                        df.at[idx, 'Status Entrada'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Chamada salva com sucesso!")
                    st.rerun()

        with aba_saida:
            with st.form("form_sai"):
                novos_status_s = {}
                for i, row in df.iterrows():
                    st.markdown(f"<div><b>{row[col_id]} - {row[col_nome]}</b></div>", unsafe_allow_html=True)
                    s_atual_s = str(row['Status Saida']) if pd.notna(row['Status Saida']) else "Pendente"
                    novos_status_s[i] = st.radio(
                        f"Saída para {row[col_nome]}:", 
                        ["Pendente", "Entregue", "Atenção"], 
                        index=["Pendente", "Entregue", "Atenção"].index(s_atual_s) if s_atual_s in ["Pendente", "Entregue", "Atenção"] else 0, 
                        key=f"sai_{i}", 
                        horizontal=True, 
                        label_visibility="collapsed"
                    )
                    st.markdown("<hr style='border: 0.5px solid #CCC;'>", unsafe_allow_html=True)
                
                if st.form_submit_button("Salvar Saída"):
                    for idx, val in novos_status_s.items(): 
                        df.at[idx, 'Status Saida'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Saída salva com sucesso!")
                    st.rerun()


# --- 4. CADASTRAR EVENTO ---
elif st.session_state.pagina == 'cadastrar':
    if st.button("Voltar à Página Inicial"): 
        navegar('home')
    st.markdown("<h1>CADASTRAR NOVO EVENTO</h1>", unsafe_allow_html=True)
    
    categoria_evento = st.radio("Selecione a Categoria:", ["Viagens e Excursões", "Festas e Eventos"])
    PASTA = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    
    with st.form("form_cad"):
        nome_grupo = st.text_input("Nome do Evento:")
        if st.form_submit_button("Criar Evento") and nome_grupo.strip():
            caminho = os.path.join(PASTA, f"{nome_grupo.strip().replace(' ', '_')}.xlsx")
            if not os.path.exists(caminho):
                pd.DataFrame({"CPF/ID": ["000"], "Nome": ["Exemplo"], "Ficha Médica": ["Nenhum"]}).to_excel(caminho, index=False)
                st.success("Evento Criado!")
                st.rerun()
            else: 
                st.warning("Evento já existe.")


# --- 5. ARQUIVOS E PASSADOS ---
elif st.session_state.pagina == 'arquivo':
    if st.button("Voltar à Página Inicial"): 
        navegar('home')
    st.markdown("<h1>EVENTOS ARQUIVADOS</h1>", unsafe_allow_html=True)
    
    arquivados = listar_grupos(PASTA_ARQUIVO)
    if arquivados:
        for arq in arquivados:
            st.markdown(f'<div class="card-evento"><b>{arq.replace("_", " ")}</b></div>', unsafe_allow_html=True)
            if st.button(f"Desarquivar {arq}"):
                os.rename(os.path.join(PASTA_ARQUIVO, f"{arq}.xlsx"), os.path.join(PASTA_VIAGENS, f"{arq}.xlsx"))
                st.rerun()
    else:
        st.info("Nenhum evento arquivado no momento.")
