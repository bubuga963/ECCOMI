import os
import json
import io
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO BASE (Layout Wide, Ocultação da Barra Lateral)
# ==============================================================================
st.set_page_config(
    page_title="Eccomi | Operações",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. DESIGN SYSTEM (Preto, Branco, Nunito, Alinhamento Perfeito)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

    /* Fundo e Fonte Global */
    .stApp, .stApp > header {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }

    /* MATADOR DE BUGS: Oculta a barra lateral e o botão expansor fantasma que mostrava a palavra */
    [data-testid="collapsedControl"], 
    [data-testid="stSidebar"], 
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        visibility: hidden !important;
    }

    /* Força a fonte nos textos normais, mas não quebra ícones internos do Streamlit se existirem */
    h1, h2, h3, p, span:not(.material-symbols-rounded), div, label, li {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
    }

    /* Padronização de Botões (Comum e Download) */
    div.stButton > button, 
    div.stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 4px !important;
        width: 100% !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
        transition: 0.3s;
    }

    div.stButton > button:hover, 
    div.stDownloadButton > button:hover {
        background-color: #E0E0E0 !important;
        border: 1px solid #000000 !important;
        color: #000000 !important;
    }

    /* Limpeza do Botão de Upload (File Uploader) */
    [data-testid="stFileUploader"] {
        border: 1px dashed #000000 !important;
        border-radius: 4px !important;
        padding: 10px !important;
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
        padding: 0 !important;
    }

    /* Cards e Alertas */
    .card-evento {
        border: 1px solid #000000;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
        background-color: #FFFFFF;
        box-shadow: 2px 2px 0px #000000; /* Toque profissional B2B */
    }

    .alerta-medico {
        border: 2px solid #000000;
        padding: 12px;
        font-weight: bold;
        margin-top: 5px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
        text-transform: uppercase;
    }
    
    hr {
        border-top: 1px solid #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. GESTÃO DE DIRETÓRIOS
# ==============================================================================
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

# ==============================================================================
# 4. MOTOR DE NAVEGAÇÃO INTERNA
# ==============================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'evento_ativo' not in st.session_state:
    st.session_state.evento_ativo = None
if 'cat_ativa' not in st.session_state:
    st.session_state.cat_ativa = None

def navegar(destino):
    st.session_state.pagina = destino
    st.rerun()

def listar_grupos(pasta):
    if os.path.exists(pasta):
        return sorted([f.replace(".xlsx", "") for f in os.listdir(pasta) if f.endswith(".xlsx")])
    return []

# ==============================================================================
# 5. ROTEAMENTO DE PÁGINAS
# ==============================================================================

# ---------------------------------------------------------
# PÁGINA 1: HOME (PÁGINA INICIAL REAL E EXCLUSIVA)
# ---------------------------------------------------------
if st.session_state.pagina == 'home':
    st.markdown("<h1 style='text-align: center; font-size: 40px;'>ECCOMI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'><b>Sistema Executivo B2B de Gestão de Embarque e Segurança</b></p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="card-evento" style="text-align: center;">
            <h2>Painel de Controle</h2>
            <p>Selecione abaixo a operação desejada para iniciar a gestão logística, conferência de passageiros ou cadastrar novas turmas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("📊 Acessar Painel de Eventos", use_container_width=True): navegar('painel')
        st.write("")
        if st.button("➕ Cadastrar Novo Evento", use_container_width=True): navegar('cadastrar')
        st.write("")
        if st.button("📁 Arquivo de Eventos Encerrados", use_container_width=True): navegar('arquivo')

# ---------------------------------------------------------
# PÁGINA 2: PAINEL DE EVENTOS (LISTAGEM E GESTÃO GERAL)
# ---------------------------------------------------------
elif st.session_state.pagina == 'painel':
    col_voltar, _ = st.columns([1, 4])
    with col_voltar:
        if st.button("⬅ Voltar para a Página Inicial"): navegar('home')
    
    st.markdown("<h1>PAINEL DE EVENTOS</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    categoria_evento = st.radio("Selecione o Setor Operacional:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    PASTA_GRUPOS = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    cat_param = "viagens" if categoria_evento == "Viagens e Excursões" else "festas"
    
    grupos_disponiveis = listar_grupos(PASTA_GRUPOS)
    termo_busca = st.text_input("🔍 Buscar evento específico (digite o nome):")
    
    if grupos_disponiveis:
        eventos_filtrados = [g for g in grupos_disponiveis if termo_busca.lower() in g.lower()] if termo_busca else grupos_disponiveis
        
        for g in eventos_filtrados:
            caminho_g = os.path.join(PASTA_GRUPOS, f"{g}.xlsx")
            caminho_inf_g = os.path.join(PASTA_INFO, f"{g}_info.json")
            
            total_p, presentes_p = 0, 0
            local_g, horario_g, status_g = "Pendente", "Pendente", "Em Andamento"
            
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
                        local_g = inf_j.get('local', 'Pendente')
                        horario_g = inf_j.get('horario', 'Pendente')
                        status_g = inf_j.get('status_evento', 'Em Andamento')
                except: pass

            st.markdown(f"""
                <div class="card-evento">
                    <h2 style="margin-top:0;">{g.replace('_', ' ')}</h2>
                    <p><b>Local:</b> {local_g} | <b>Horário:</b> {horario_g} | <b>Status:</b> {status_g}</p>
                    <p><b>Check-in:</b> {presentes_p} presentes (de {total_p} cadastrados no total)</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Botões de Ação perfeitamente alinhados
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button(f"Abrir Evento", key=f"abrir_{g}"):
                    st.session_state.evento_ativo = g
                    st.session_state.cat_ativa = cat_param
                    navegar('evento_interno')
            with c2:
                # O Expander mantém o design limpo para o uploader
                with st.popover("Substituir Planilha"):
                    novo_excel = st.file_uploader(f"Upload .xlsx ({g})", type=["xlsx"], key=f"up_{g}", label_visibility="collapsed")
                    if novo_excel is not None:
                        df_novo = pd.read_excel(novo_excel)
                        df_novo.to_excel(caminho_g, index=False)
                        st.success("Planilha atualizada!")
            with c3:
                if st.button("Arquivar Evento", key=f"arq_{g}"):
                    os.rename(caminho_g, os.path.join(PASTA_ARQUIVO, f"{g}.xlsx"))
                    st.rerun()
            with c4:
                if st.button("Excluir Evento", key=f"del_{g}"):
                    os.remove(caminho_g)
                    if os.path.exists(caminho_inf_g): os.remove(caminho_inf_g)
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento ativo no momento.")

# ---------------------------------------------------------
# PÁGINA 3: INTERIOR DO EVENTO (OPERAÇÃO E EXPORTAÇÃO)
# ---------------------------------------------------------
elif st.session_state.pagina == 'evento_interno' and st.session_state.evento_ativo:
    col_voltar, _ = st.columns([1, 4])
    with col_voltar:
        if st.button("⬅ Voltar ao Painel"): navegar('painel')
    
    g_ativo = st.session_state.evento_ativo
    pasta_alvo = PASTA_VIAGENS if st.session_state.cat_ativa == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{g_ativo}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{g_ativo}_info.json")
    
    if os.path.exists(caminho_arquivo):
        st.markdown(f"<h1>OPERAÇÃO: {g_ativo.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        
        info_data = {}
        if os.path.exists(caminho_info):
            with open(caminho_info, "r", encoding="utf-8") as f: 
                info_data = json.load(f)

        df = pd.read_excel(caminho_arquivo)
        col_id = df.columns[0]
        col_nome = df.columns[1]
        col_ficha = df.columns[5] if len(df.columns) > 5 else df.columns[-1]
        
        if 'Status Entrada' not in df.columns: df['Status Entrada'] = "Pendente"
        if 'Status Saida' not in df.columns: df['Status Saida'] = "Pendente"

        aba_info, aba_entrada, aba_saida = st.tabs(["1. Logística e Fechamento", "2. Check-in (Embarque)", "3. Check-out (Desembarque)"])
        
        with aba_info:
            st.markdown("### Resumo Logístico")
            st.markdown(f"""
                <div class="card-evento">
                    <b>Status:</b> {info_data.get('status_evento', 'Em Andamento')}<br>
                    <b>Local:</b> {info_data.get('local', '-')} | <b>Tel:</b> {info_data.get('tel_local', '-')}<br>
                    <b>Horário:</b> {info_data.get('horario', '-')}<br>
                    <b>Transporte:</b> {info_data.get('transporte', '-')} | <b>Motorista:</b> {info_data.get('motorista', '-')}<br>
                    <b>Link Google Drive:</b> {info_data.get('drive_fotos', '-')}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📥 Fechamento e Exportação")
            # --- MOTOR DE EXPORTAÇÃO CORRIGIDO ---
            total_part = len(df)
            total_pres = len(df[df['Status Entrada'] == 'Presente'])
            total_falt = len(df[df['Status Entrada'] == 'Faltou'])
            total_entregue = len(df[df['Status Saida'] == 'Entregue'])

            df_resumo = pd.DataFrame([
                {"INDICADOR": "Nome do Evento", "DADO": g_ativo.replace('_', ' ')},
                {"INDICADOR": "Local / Horário", "DADO": f"{info_data.get('local', '-')} / {info_data.get('horario', '-')}"},
                {"INDICADOR": "Total Cadastrados", "DADO": total_part},
                {"INDICADOR": "Total Presentes (Entrada)", "DADO": total_pres},
                {"INDICADOR": "Total Faltas", "DADO": total_falt},
                {"INDICADOR": "Total Entregues c/ Segurança (Saída)", "DADO": total_entregue}
            ])

            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_resumo.to_excel(writer, sheet_name="Resumo_Auditoria", index=False)
                df.to_excel(writer, sheet_name="Lista_Operacional", index=False)
            dados_excel = output_excel.getvalue()

            st.download_button(
                label="Fazer Download do Relatório Final (.xlsx)",
                data=dados_excel,
                file_name=f"Fechamento_{g_ativo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.markdown("<hr>", unsafe_allow_html=True)
            
            with st.expander("Editar Informações do Evento"):
                with st.form("form_editar_info"):
                    status_op = st.selectbox("Status:", ["Em Andamento", "Finalizado", "Cancelado"], index=["Em Andamento", "Finalizado", "Cancelado"].index(info_data.get('status_evento', 'Em Andamento')))
                    loc = st.text_input("Local:", value=info_data.get('local', ''))
                    t_loc = st.text_input("Telefone Local:", value=info_data.get('tel_local', ''))
                    hor = st.text_input("Horário/Data:", value=info_data.get('horario', ''))
                    trans = st.text_input("Placa Transporte:", value=info_data.get('transporte', ''))
                    mot = st.text_input("Motorista/Tel:", value=info_data.get('motorista', ''))
                    drive = st.text_input("Link Google Drive (Fotos):", value=info_data.get('drive_fotos', ''))
                    
                    if st.form_submit_button("Salvar Edições"):
                        novo_dict = {"status_evento": status_op, "local": loc, "tel_local": t_loc, "horario": hor, "transporte": trans, "motorista": mot, "drive_fotos": drive}
                        with open(caminho_info, "w", encoding="utf-8") as f: 
                            json.dump(novo_dict, f, ensure_ascii=False)
                        st.success("Salvo!")
                        st.rerun()

        with aba_entrada:
            st.markdown(f"<b>Progresso:</b> {len(df[df['Status Entrada'] == 'Presente'])} presentes de {len(df)}.", unsafe_allow_html=True)
            pesquisa = st.text_input("🔍 Filtrar participante (Nome ou ID):", key="pesq_ent")
            df_filt = df[df[col_nome].astype(str).str.contains(pesquisa, case=False, na=False) | df[col_id].astype(str).str.contains(pesquisa, case=False, na=False)] if pesquisa else df
            
            with st.form("form_ent"):
                novos_status = {}
                for i, row in df_filt.iterrows():
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).lower() not in ["", "nao ha.", "nenhum"] else None
                    st.markdown(f"<div style='font-size: 16px; margin-top:10px;'><b>{row[col_id]} - {row[col_nome]}</b></div>", unsafe_allow_html=True)
                    s_atual = str(row['Status Entrada']) if pd.notna(row['Status Entrada']) else "Pendente"
                    novos_status[i] = st.radio(
                        f"Status {row[col_nome]}:", 
                        ["Pendente", "Presente", "Faltou"], 
                        index=["Pendente", "Presente", "Faltou"].index(s_atual) if s_atual in ["Pendente", "Presente", "Faltou"] else 0, 
                        key=f"ent_{i}", horizontal=True, label_visibility="collapsed"
                    )
                    if ficha: 
                        st.markdown(f"<div class='alerta-medico'>ATENÇÃO MÉDICA: {ficha}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
                
                if st.form_submit_button("Salvar Check-in", use_container_width=True):
                    for idx, val in novos_status.items(): df.at[idx, 'Status Entrada'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Check-in atualizado!")
                    st.rerun()

        with aba_saida:
            with st.form("form_sai"):
                novos_status_s = {}
                for i, row in df.iterrows():
                    st.markdown(f"<div style='font-size: 16px; margin-top:10px;'><b>{row[col_id]} - {row[col_nome]}</b></div>", unsafe_allow_html=True)
                    s_atual_s = str(row['Status Saida']) if pd.notna(row['Status Saida']) else "Pendente"
                    novos_status_s[i] = st.radio(
                        f"Saída {row[col_nome]}:", 
                        ["Pendente", "Entregue", "Atenção"], 
                        index=["Pendente", "Entregue", "Atenção"].index(s_atual_s) if s_atual_s in ["Pendente", "Entregue", "Atenção"] else 0, 
                        key=f"sai_{i}", horizontal=True, label_visibility="collapsed"
                    )
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
                
                if st.form_submit_button("Salvar Check-out", use_container_width=True):
                    for idx, val in novos_status_s.items(): df.at[idx, 'Status Saida'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Check-out atualizado!")
                    st.rerun()

# ---------------------------------------------------------
# PÁGINA 4: CADASTRAR EVENTO
# ---------------------------------------------------------
elif st.session_state.pagina == 'cadastrar':
    col_voltar, _ = st.columns([1, 4])
    with col_voltar:
        if st.button("⬅ Voltar para a Página Inicial"): navegar('home')

    st.markdown("<h1>CADASTRAR NOVO EVENTO</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    categoria_evento = st.radio("Selecione a Categoria:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    PASTA = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    
    with st.form("form_cad"):
        nome_grupo = st.text_input("Defina o Nome do Evento (Ex: Escola_Integral_5Ano):")
        if st.form_submit_button("Criar Base do Evento") and nome_grupo.strip():
            caminho = os.path.join(PASTA, f"{nome_grupo.strip().replace(' ', '_')}.xlsx")
            if not os.path.exists(caminho):
                pd.DataFrame({"ID": ["01"], "Nome": ["Exemplo"], "Data Nasc": ["01/01/2010"], "Responsável": ["Maria"], "Telefone": ["000000"], "Ficha Médica": ["Nenhum"]}).to_excel(caminho, index=False)
                st.success("Evento Criado! Retorne ao Painel para operá-lo.")
            else: 
                st.error("Erro: Um evento com este nome já existe.")

# ---------------------------------------------------------
# PÁGINA 5: ARQUIVO
# ---------------------------------------------------------
elif st.session_state.pagina == 'arquivo':
    col_voltar, _ = st.columns([1, 4])
    with col_voltar:
        if st.button("⬅ Voltar para a Página Inicial"): navegar('home')

    st.markdown("<h1>EVENTOS ENCERRADOS (ARQUIVO)</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    arquivados = listar_grupos(PASTA_ARQUIVO)
    if arquivados:
        for arq in arquivados:
            st.markdown(f"<div class='card-evento'><h3>{arq.replace('_', ' ')}</h3></div>", unsafe_allow_html=True)
            if st.button(f"Desarquivar (Restaurar) {arq.replace('_', ' ')}", key=f"des_{arq}"):
                os.rename(os.path.join(PASTA_ARQUIVO, f"{arq}.xlsx"), os.path.join(PASTA_VIAGENS, f"{arq}.xlsx"))
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento arquivado no momento.")
