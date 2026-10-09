import os
import json
import io
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO GLOBAL DA PÁGINA E DESIGN DE MERCADO (SAAS B2B)
# ==============================================================================
st.set_page_config(
    page_title="Eccomi | Gestão de Eventos",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeção de CSS otimizada, moderna e livre de bugs visuais
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    h1, h2, h3, p, span, div, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #0F172A !important;
    }

    /* Cartões executivos modernos com efeito de elevação */
    .card-evento {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease-in-out;
    }
    
    .card-evento:hover {
        border-color: #CBD5E1;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    /* Alerta médico estilizado com alto contraste para operação */
    .alerta-medico {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        color: #991B1B;
        padding: 12px;
        font-weight: 600;
        border-radius: 0 8px 8px 0;
        margin-top: 8px;
        margin-bottom: 12px;
        font-size: 13px;
    }
    
    /* Estilização limpa dos botões principais do Streamlit */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GESTÃO DE DIRETÓRIOS E PASTAS LOCAIS
# ==============================================================================
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

# ==============================================================================
# CONTROLE DE NAVEGAÇÃO INTERNA (SESSION STATE)
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

def abrir_evento(evento, cat):
    st.session_state.evento_ativo = evento
    st.session_state.cat_ativa = cat
    st.session_state.pagina = 'evento_interno'
    st.rerun()

def listar_grupos(pasta):
    if os.path.exists(pasta):
        return sorted([f.replace(".xlsx", "") for f in os.listdir(pasta) if f.endswith(".xlsx")])
    return []

# ==============================================================================
# BARRA LATERAL NATIVA (DESIGN CORPORATIVO LIMPO)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🖖 ECCOMI")
    st.markdown("<p style='color: #64748B; font-size: 12px; margin-top:-10px;'>Gestão Cirúrgica de Eventos</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🏠 Página Inicial", use_container_width=True, key="nav_home"):
        navegar('home')
    if st.button("📊 Painel de Eventos", use_container_width=True, key="nav_painel"):
        navegar('painel')
    if st.button("➕ Cadastrar Evento", use_container_width=True, key="nav_cad"):
        navegar('cadastrar')
    if st.button("📦 Eventos Arquivados", use_container_width=True, key="nav_arq"):
        navegar('arquivo')


# ==============================================================================
# ROTEAMENTO E RENDERIZAÇÃO DAS PÁGINAS DO SISTEMA
# ==============================================================================

# --- TELA 1: PÁGINA INICIAL (HOME COM RESUMO EXECUTIVO DINÂMICO) ---
if st.session_state.pagina == 'home':
    st.markdown("<h1>Painel Executivo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Visão geral consolidada de todas as operações e eventos ativos no campo.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #E2E8F0; margin-bottom: 24px;'>", unsafe_allow_html=True)
    
    todos_eventos = []
    for g in listar_grupos(PASTA_VIAGENS):
        todos_eventos.append((g, PASTA_VIAGENS, "Viagem/Excursão"))
    for g in listar_grupos(PASTA_FESTAS):
        todos_eventos.append((g, PASTA_FESTAS, "Festa/Evento"))
        
    if todos_eventos:
        for g, pasta_origem, cat_nome in todos_eventos:
            caminho_planilha = os.path.join(pasta_origem, f"{g}.xlsx")
            caminho_info_json = os.path.join(PASTA_INFO, f"{g}_info.json")
            
            total_part, presentes, faltosos = 0, 0, 0
            local_ev, horario_ev, status_ev = "Não informado", "Não informado", "Em Andamento"
            
            if os.path.exists(caminho_planilha):
                try:
                    df_temp = pd.read_excel(caminho_planilha)
                    total_part = len(df_temp)
                    if 'Status Entrada' in df_temp.columns:
                        presentes = len(df_temp[df_temp['Status Entrada'] == "Presente"])
                        faltosos = len(df_temp[df_temp['Status Entrada'] == "Faltou"])
                except:
                    pass
                    
            if os.path.exists(caminho_info_json):
                try:
                    with open(caminho_info_json, "r", encoding="utf-8") as f:
                        dados_inf = json.load(f)
                        local_ev = dados_inf.get('local', 'Não informado')
                        horario_ev = dados_inf.get('horario', 'Não informado')
                        status_ev = dados_inf.get('status_evento', 'Em Andamento')
                except:
                    pass
            
            st.markdown(f"""
                <div class="card-evento">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h3 style="margin:0; font-size: 18px; color: #0F172A;">{g.replace('_', ' ')}</h3>
                        <span style="font-size:11px; font-weight: 600; background-color: #F1F5F9; color: #334155; padding: 4px 10px; border-radius: 20px;">{cat_nome}</span>
                    </div>
                    <p style="margin: 4px 0; color: #475569;"><b>Status:</b> {status_ev} | <b>Local:</b> {local_ev}</p>
                    <p style="margin: 4px 0; color: #475569;"><b>Horário:</b> {horario_ev}</p>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #F1F5F9; display: flex; gap: 20px; font-size: 13px;">
                        <span>📋 Total: <b>{total_part}</b></span>
                        <span style="color: #16A34A;">✅ Presentes: <b>{presentes}</b></span>
                        <span style="color: #DC2626;">❌ Faltosos: <b>{faltosos}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum evento registado no sistema no momento. Utilize o menu lateral para iniciar um cadastro.")
        
    st.write("")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        if st.button("📊 Aceder Painel", use_container_width=True, key="h_btn1"): 
            navegar('painel')
    with col_h2:
        if st.button("➕ Novo Evento", use_container_width=True, key="h_btn2"): 
            navegar('cadastrar')
    with col_h3:
        if st.button("📦 Arquivados", use_container_width=True, key="h_btn3"): 
            navegar('arquivo')


# --- TELA 2: PAINEL DE EVENTOS ---
elif st.session_state.pagina == 'painel':
    if st.button("← Voltar ao Início", key="voltar_home_painel"): 
        navegar('home')
    
    st.markdown("<h1>Gestão de Operações</h1>", unsafe_allow_html=True)
    categoria_evento = st.radio("Selecione o Categoria Operacional:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    
    PASTA_GRUPOS = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    cat_param = "viagens" if categoria_evento == "Viagens e Excursões" else "festas"
    grupos_disponiveis = listar_grupos(PASTA_GRUPOS)
    
    st.markdown("<hr style='border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    termo_busca = st.text_input("🔍 Pesquisar evento por nome:")
    
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
                    <h3 style="margin-top:0; font-size: 16px;">{g.replace('_', ' ')}</h3>
                    <p style="margin:2px 0; color: #475569;"><b>Local:</b> {local_g} | <b>Horário:</b> {horario_g}</p>
                    <p style="margin:2px 0; color: #475569;"><b>Check-in:</b> {presentes_p} de {total_p} confirmados</p>
                </div>
            """, unsafe_allow_html=True)
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button(f"🚀 Abrir Operação", key=f"btn_{g}", use_container_width=True): 
                    abrir_evento(g, cat_param)
            with col_b2:
                if st.button("📦 Arquivar", key=f"arq_{g}", use_container_width=True):
                    os.rename(caminho_g, os.path.join(PASTA_ARQUIVO, f"{g}.xlsx"))
                    st.rerun()
            with col_b3:
                if st.button("🗑️ Excluir", key=f"del_{g}", use_container_width=True):
                    os.remove(caminho_g)
                    if os.path.exists(caminho_inf_g): 
                        os.remove(caminho_inf_g)
                    st.rerun()
            
            with st.expander(f"📁 Atualizar Base de Dados (.xlsx) — {g.replace('_', ' ')}"):
                novo_excel = st.file_uploader("Selecionar ficheiro Excel atualizado:", type=["xlsx"], key=f"up_{g}")
                if novo_excel is not None:
                    df_novo = pd.read_excel(novo_excel)
                    df_novo.to_excel(caminho_g, index=False)
                    st.success("Base de dados atualizada com sucesso!")
            
            st.markdown("<hr style='border: 0.5px solid #F1F5F9; margin: 20px 0;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento registado nesta categoria.")


# --- TELA 3: ÁREA OPERACIONAL INTERNA DO EVENTO ---
elif st.session_state.pagina == 'evento_interno' and st.session_state.evento_ativo:
    if st.button("← Voltar ao Painel", key="voltar_painel_interno"): 
        navegar('painel')
    
    g_ativo = st.session_state.evento_ativo
    pasta_alvo = PASTA_VIAGENS if st.session_state.cat_ativa == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{g_ativo}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{g_ativo}_info.json")
    
    if os.path.exists(caminho_arquivo):
        st.markdown(f"<h1>Operação: {g_ativo.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        info_data = {}
        if os.path.exists(caminho_info):
            with open(caminho_info, "r", encoding="utf-8") as f: 
                info_data = json.load(f)

        df = pd.read_excel(caminho_arquivo)
        col_id = df.columns[0]
        col_nome = df.columns[1]
        col_ficha = df.columns[5] if len(df.columns) > 5 else df.columns[-1]
        
        if 'Status Entrada' not in df.columns: 
            df['Status Entrada'] = "Pendente"
        if 'Status Saida' not in df.columns: 
            df['Status Saida'] = "Pendente"

        aba_info, aba_chamada, aba_saida = st.tabs(["📌 Informações & Fechamento", "📥 Entrada (Embarque)", "📤 Saída (Desembarque)"])
        
        with aba_info:
            st.markdown("<h3>Detalhes Logísticos</h3>", unsafe_allow_html=True)
            link_drive = info_data.get('drive_fotos', 'Não informado')
            link_html = f'<a href="{link_drive}" target="_blank">{link_drive}</a>' if link_drive.startswith('http') else link_drive
            
            st.markdown(f"""
                <div class="card-evento">
                    <p><b>Status:</b> {info_data.get('status_evento', 'Em Andamento')}</p>
                    <p><b>Local:</b> {info_data.get('local', 'Não informado')} | <b>Tel:</b> {info_data.get('tel_local', 'Não informado')}</p>
                    <p><b>Horário/Data:</b> {info_data.get('horario', 'Não informado')}</p>
                    <p><b>Roteiro:</b> {info_data.get('roteiro', 'Não informado')}</p>
                    <p><b>Transporte:</b> {info_data.get('transporte', 'Não informado')} (Motorista: {info_data.get('motorista', 'Não informado')})</p>
                    <p><b>Equipe:</b> {info_data.get('equipe', 'Não informado')}</p>
                    <p><b>Drive/Fotos:</b> {link_html}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3>Fechamento Executivo</h3>", unsafe_allow_html=True)
            
            total_part = len(df)
            total_pres = len(df[df['Status Entrada'] == 'Presente'])
            total_falt = len(df[df['Status Entrada'] == 'Faltou'])
            total_entregue = len(df[df['Status Saida'] == 'Entregue'])

            df_resumo = pd.DataFrame([
                {"Métrica": "Nome do Evento", "Valor": g_ativo.replace('_', ' ')},
                {"Métrica": "Status", "Valor": info_data.get('status_evento', 'Em Andamento')},
                {"Métrica": "Local", "Valor": info_data.get('local', 'Não informado')},
                {"Métrica": "Data e Horário", "Valor": info_data.get('horario', 'Não informado')},
                {"Métrica": "Transporte / Motorista", "Valor": f"{info_data.get('transporte', '')} / {info_data.get('motorista', '')}"},
                {"Métrica": "Total de Participantes", "Valor": total_part},
                {"Métrica": "Total Presentes", "Valor": total_pres},
                {"Métrica": "Total Faltosos", "Valor": total_falt},
                {"Métrica": "Total Entregues", "Valor": total_entregue}
            ])

            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_resumo.to_excel(writer, sheet_name="Resumo_Executivo", index=False)
                df.to_excel(writer, sheet_name="Lista_Participantes", index=False)
            
            dados_relatorio = output_excel.getvalue()

            st.download_button(
                label="📥 Baixar Relatório Executivo Completo (.xlsx)",
                data=dados_relatorio,
                file_name=f"Relatorio_{g_ativo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_relatorio"
            )

            st.write("")
            with st.expander("⚙️ Editar Dados e Informações Operacionais"):
                with st.form("form_info_editar"):
                    status_opcoes = ["Em Andamento", "Concluído com Sucesso", "Cancelado"]
                    atual_st = info_data.get('status_evento', 'Em Andamento')
                    idx_st = status_opcoes.index(atual_st) if atual_st in status_opcoes else 0
                    
                    st_evento = st.selectbox("Status:", status_opcoes, index=idx_st)
                    loc = st.text_input("Local:", value=info_data.get('local', ''))
                    t_loc = st.text_input("Telefone:", value=info_data.get('tel_local', ''))
                    hor = st.text_input("Horário/Data:", value=info_data.get('horario', ''))
                    rot = st.text_area("Roteiro:", value=info_data.get('roteiro', ''))
                    trans = st.text_input("Transporte:", value=info_data.get('transporte', ''))
                    mot = st.text_input("Motorista:", value=info_data.get('motorista', ''))
                    eqp = st.text_area("Equipe:", value=info_data.get('equipe', ''))
                    drive = st.text_input("Link Drive:", value=info_data.get('drive_fotos', ''))
                    
                    if st.form_submit_button("💾 Guardar Alterações"):
                        novo_dict = {
                            "status_evento": st_evento,
                            "local": loc,
                            "tel_local": t_loc,
                            "horario": hor,
                            "roteiro": rot,
                            "transporte": trans,
                            "motorista": mot,
                            "equipe": eqp,
                            "drive_fotos": drive
                        }
                        with open(caminho_info, "w", encoding="utf-8") as f: 
                            json.dump(novo_dict, f, ensure_ascii=False)
                        st.success("Guardado com sucesso!")
                        st.rerun()

        with aba_chamada:
            pesquisa = st.text_input("🔍 Pesquisar participante por nome ou ID:", key="pesq_ent")
            df_filt = df[df[col_nome].astype(str).str.contains(pesquisa, case=False, na=False) | df[col_id].astype(str).str.contains(pesquisa, case=False, na=False)] if pesquisa else df
            
            st.markdown(f"<p><b>Confirmados:</b> {len(df[df['Status Entrada'] == 'Presente'])} de {len(df)}</p>", unsafe_allow_html=True)
            with st.form("form_ent"):
                novos_status = {}
                for i, row in df_filt.iterrows():
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).lower() not in ["", "nao ha.", "nenhum"] else None
                    st.markdown(f"<div><b>{row[col_id]}</b> — {row[col_nome]}</div>", unsafe_allow_html=True)
                    s_atual = str(row['Status Entrada']) if pd.notna(row['Status Entrada']) else "Pendente"
                    novos_status[i] = st.radio(
                        f"Status_{i}", 
                        ["Pendente", "Presente", "Faltou"], 
                        index=["Pendente", "Presente", "Faltou"].index(s_atual) if s_atual in ["Pendente", "Presente", "Faltou"] else 0, 
                        key=f"ent_{i}", 
                        horizontal=True, 
                        label_visibility="collapsed"
                    )
                    if ficha: 
                        st.markdown(f"<div class='alerta-medico'>⚠️ ALERTA MÉDICO: {ficha}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='border: 0.5px solid #F1F5F9;'>", unsafe_allow_html=True)
                
                if st.form_submit_button("✅ Guardar Chamada de Entrada", use_container_width=True):
                    for idx, val in novos_status.items(): 
                        df.at[idx, 'Status Entrada'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Chamada de entrada guardada com sucesso!")
                    st.rerun()

        with aba_saida:
            with st.form("form_sai"):
                novos_status_s = {}
                for i, row in df.iterrows():
                    st.markdown(f"<div><b>{row[col_id]}</b> — {row[col_nome]}</div>", unsafe_allow_html=True)
                    s_atual_s = str(row['Status Saida']) if pd.notna(row['Status Saida']) else "Pendente"
                    novos_status_s[i] = st.radio(
                        f"Saida_{i}", 
                        ["Pendente", "Entregue", "Atenção"], 
                        index=["Pendente", "Entregue", "Atenção"].index(s_atual_s) if s_atual_s in ["Pendente", "Entregue", "Atenção"] else 0, 
                        key=f"sai_{i}", 
                        horizontal=True, 
                        label_visibility="collapsed"
                    )
                    st.markdown("<hr style='border: 0.5px solid #F1F5F9;'>", unsafe_allow_html=True)
                
                if st.form_submit_button("✅ Guardar Controlo de Saída", use_container_width=True):
                    for idx, val in novos_status_s.items(): 
                        df.at[idx, 'Status Saida'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Controlo de saída guardado com sucesso!")
                    st.rerun()


# --- TELA 4: CADASTRAR NOVO EVENTO ---
elif st.session_state.pagina == 'cadastrar':
    if st.button("← Voltar ao Início", key="voltar_home_cad"): 
        navegar('home')
    st.markdown("<h1>Cadastrar Nova Operação</h1>", unsafe_allow_html=True)
    
    categoria_evento = st.radio("Categoria do Evento:", ["Viagens e Excursões", "Festas e Eventos"])
    PASTA = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    
    with st.form("form_cad"):
        nome_grupo = st.text_input("Nome do Evento:")
        if st.form_submit_button("Criar Estrutura do Evento") and nome_grupo.strip():
            caminho = os.path.join(PASTA, f"{nome_grupo.strip().replace(' ', '_')}.xlsx")
            if not os.path.exists(caminho):
                pd.DataFrame({"CPF/ID": ["000"], "Nome": ["Exemplo Participante"], "Ficha Médica": ["Nenhum"]}).to_excel(caminho, index=False)
                st.success("Evento criado com sucesso!")
                navegar('painel')
            else: 
                st.warning("Já existe um evento com este nome.")


# --- TELA 5: EVENTOS ARQUIVADOS ---
elif st.session_state.pagina == 'arquivo':
    if st.button("← Voltar ao Início", key="voltar_home_arq"): 
        navegar('home')
    st.markdown("<h1>Operações Arquivadas</h1>", unsafe_allow_html=True)
    
    arquivados = listar_grupos(PASTA_ARQUIVO)
    if arquivados:
        for arq in arquivados:
            st.markdown(f'<div class="card-evento"><b>{arq.replace("_", " ")}</b></div>', unsafe_allow_html=True)
            if st.button(f"Desarquivar {arq}", key=f"desarq_{arq}"):
                os.rename(os.path.join(PASTA_ARQUIVO, f"{arq}.xlsx"), os.path.join(PASTA_VIAGENS, f"{arq}.xlsx"))
                st.rerun()
    else:
        st.info("Nenhum evento arquivado no momento.")
