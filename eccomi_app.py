import os
import json
import io
import uuid
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO GLOBAL DA PÁGINA E DESIGN CORPORATIVO
# ==============================================================================
st.set_page_config(
    page_title="Eccomi | Gestão de Eventos",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS limpa e moderna para o painel
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .card-evento {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kanban-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .alerta-medico {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        color: #991B1B;
        padding: 10px;
        border-radius: 0 6px 6px 0;
        margin: 5px 0 10px 0;
        font-size: 13px;
        font-weight: 600;
    }

    /* Correção dos ícones internos do Streamlit (Material Symbols) */
    [data-testid="stIconMaterial"],
    [data-testid="stExpanderIcon"],
    .material-icons,
    .material-symbols-rounded,
    .material-symbols-outlined {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: "liga" !important;
        font-feature-settings: "liga" !important;
        -webkit-font-smoothing: antialiased;
    }
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapsedControl"] span,
    [data-testid="stExpandSidebarButton"] span {
        display: inline-block;
        max-width: 24px;
        max-height: 24px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# ESTRUTURA DE PASTAS LOCAIS
# ==============================================================================
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

STATUS_EVENTO_OPCOES = ["Em Andamento", "Finalizado", "Cancelado", "Adiado"]

# ==============================================================================
# GERENCIAMENTO DE ESTADO (SESSION STATE)
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

def carregar_info(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados if isinstance(dados, dict) else {}
        except Exception:
            return {}
    return {}

def salvar_info(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ==============================================================================
# BARRA LATERAL (MENU DE NAVEGAÇÃO)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🖖 ECCOMI")
    st.markdown("<p style='color: #64748B; font-size: 12px;'>Gestão de Eventos e Operações</p>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🏠 Página Inicial", use_container_width=True):
        navegar('home')
    if st.button("📊 Painel de Eventos", use_container_width=True):
        navegar('painel')
    if st.button("➕ Cadastrar Evento", use_container_width=True):
        navegar('cadastrar')
    if st.button("📦 Eventos Arquivados", use_container_width=True):
        navegar('arquivo')

# ==============================================================================
# ROTEAMENTO DE PÁGINAS
# ==============================================================================

# --- TELA 1: HOME (PAINEL EXECUTIVO) ---
if st.session_state.pagina == 'home':
    st.title("Painel Executivo")
    st.write("Visão geral consolidada de todas as operações ativas.")
    st.markdown("---")

    # Controlo de visualização (Lista vs. Kanban)
    tipo_view = st.radio("Modo de Visualização:", ["📋 Lista Executiva", "🗂️ Kanban por Status"], horizontal=True, key="view_home")

    todos_eventos = []
    for g in listar_grupos(PASTA_VIAGENS):
        todos_eventos.append((g, PASTA_VIAGENS, "Viagem/Excursão"))
    for g in listar_grupos(PASTA_FESTAS):
        todos_eventos.append((g, PASTA_FESTAS, "Festa/Evento"))

    if todos_eventos:
        # Carrega dados consolidados de cada evento
        dados_consolidados = []
        for g, pasta_origem, cat_nome in todos_eventos:
            caminho_planilha = os.path.join(pasta_origem, f"{g}.xlsx")
            caminho_info_json = os.path.join(PASTA_INFO, f"{g}_info.json")

            total_part, presentes, faltosos = 0, 0, 0
            if os.path.exists(caminho_planilha):
                try:
                    df_temp = pd.read_excel(caminho_planilha)
                    total_part = len(df_temp)
                    if 'Status Entrada' in df_temp.columns:
                        presentes = len(df_temp[df_temp['Status Entrada'] == "Presente"])
                        faltosos = len(df_temp[df_temp['Status Entrada'] == "Faltou"])
                except:
                    pass

            dados_inf = carregar_info(caminho_info_json)
            
            # Garante ID padrão se não existir
            if not dados_inf.get('id_evento'):
                dados_inf['id_evento'] = f"EVT-{str(uuid.uuid4())[:6].upper()}"
                salvar_info(caminho_info_json, dados_inf)

            dados_consolidados.append({
                "nome": g,
                "pasta": pasta_origem,
                "categoria": cat_nome,
                "id_evento": dados_inf.get('id_evento'),
                "status": dados_inf.get('status_evento', 'Em Andamento'),
                "local": dados_inf.get('local', 'Não informado'),
                "data_inicio": dados_inf.get('data_inicio', '—'),
                "data_fim": dados_inf.get('data_fim', '—'),
                "total": total_part,
                "presentes": presentes,
                "faltosos": faltosos
            })

        if tipo_view == "📋 Lista Executiva":
            for ev in dados_consolidados:
                st.markdown(f"""
                    <div class="card-evento">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0 0 8px 0; font-size: 18px;">{ev['nome'].replace('_', ' ')} <span style="font-size:12px; font-weight:normal; color:#64748B;">({ev['categoria']})</span></h3>
                            <span style="background-color:#E2E8F0; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold;">ID: {ev['id_evento']}</span>
                        </div>
                        <p style="margin:4px 0;"><b>Status:</b> {ev['status']} | <b>Local:</b> {ev['local']} | <b>Período:</b> {ev['data_inicio']} até {ev['data_fim']}</p>
                        <p style="margin:4px 0; color: #475569;">Total: <b>{ev['total']}</b> | ✅ Presentes: <b>{ev['presentes']}</b> | ❌ Faltosos: <b>{ev['faltosos']}</b></p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            # Visão Kanban
            col_k1, col_k2, col_k3, col_k4 = st.columns(4)
            status_list = ["Em Andamento", "Adiado", "Finalizado", "Cancelado"]
            colunas_map = {"Em Andamento": col_k1, "Adiado": col_k2, "Finalizado": col_k3, "Cancelado": col_k4}

            for idx_s, st_val in enumerate(status_list):
                with list(colunas_map.values())[idx_s]:
                    st.markdown(f"#### 📌 {st_val}")
                    evs_status = [e for e in dados_consolidados if e['status'] == st_val]
                    if evs_status:
                        for ev in evs_status:
                            st.markdown(f"""
                                <div class="kanban-card">
                                    <b style="font-size:15px;">{ev['nome'].replace('_', ' ')}</b><br>
                                    <span style="font-size:11px; color:#64748B;">ID: {ev['id_evento']}</span><br>
                                    <p style="font-size:12px; margin:4px 0;">📍 {ev['local']}<br>📅 {ev['data_inicio']} a {ev['data_fim']}</p>
                                    <hr style="margin:6px 0;">
                                    <span style="font-size:12px; color:#0F172A;">👥 {ev['total']} pax | ✅ {ev['presentes']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='font-size:12px; color:#94A3B8;'>Nenhum evento</p>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento registado. Utilize o menu lateral para iniciar um cadastro.")

# --- TELA 2: PAINEL DE EVENTOS ---
elif st.session_state.pagina == 'painel':
    if st.button("← Voltar ao Início"):
        navegar('home')

    st.title("Gestão de Operações")
    categoria_evento = st.radio("Categoria:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)

    pasta_grupos = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    cat_param = "viagens" if categoria_evento == "Viagens e Excursões" else "festas"
    grupos_disponiveis = listar_grupos(pasta_grupos)

    st.markdown("---")
    
    # Filtros de busca integrados (por nome e por data)
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        termo_busca = st.text_input("🔍 Pesquisar evento por nome:")
    with col_b2:
        filtro_data = st.text_input("📅 Filtrar por data (ex: 2027):")

    if grupos_disponiveis:
        eventos_filtrados = []
        for g in grupos_disponiveis:
            caminho_inf_g = os.path.join(PASTA_INFO, f"{g}_info.json")
            info_g = carregar_info(caminho_inf_g)
            
            # Condições de filtro
            match_nome = termo_busca.lower() in g.lower() if termo_busca else True
            data_str = f"{info_g.get('data_inicio', '')} {info_g.get('data_fim', '')}"
            match_data = filtro_data in data_str if filtro_data else True
            
            if match_nome and match_data:
                eventos_filtrados.append(g)

        if eventos_filtrados:
            for g in eventos_filtrados:
                caminho_g = os.path.join(pasta_grupos, f"{g}.xlsx")
                caminho_inf_g = os.path.join(PASTA_INFO, f"{g}_info.json")

                total_p, presentes_p = 0, 0
                if os.path.exists(caminho_g):
                    try:
                        df_g = pd.read_excel(caminho_g)
                        total_p = len(df_g)
                        if 'Status Entrada' in df_g.columns:
                            presentes_p = len(df_g[df_g['Status Entrada'] == "Presente"])
                    except:
                        pass

                info_g = carregar_info(caminho_inf_g)
                id_ev = info_g.get('id_evento', 'SEM-ID')
                d_ini = info_g.get('data_inicio', '—')
                d_fim = info_g.get('data_fim', '—')
                local_ev = info_g.get('local', 'Não informado')

                st.markdown(f"""
                    <div class="card-evento">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0;">{g.replace('_', ' ')}</h4>
                            <span style="background-color:#E2E8F0; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold;">ID: {id_ev}</span>
                        </div>
                        <p style="margin:4px 0; color: #475569;"><b>Local:</b> {local_ev} | <b>Período:</b> {d_ini} até {d_fim}</p>
                        <p style="margin:4px 0; color: #475569;">Check-in: {presentes_p} de {total_p} confirmados</p>
                    </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🚀 Abrir", key=f"abrir_{g}", use_container_width=True):
                        abrir_evento(g, cat_param)
                with col2:
                    if st.button(f"📦 Arquivar", key=f"arq_{g}", use_container_width=True):
                        info_g["categoria_origem"] = cat_param
                        salvar_info(caminho_inf_g, info_g)
                        os.rename(caminho_g, os.path.join(PASTA_ARQUIVO, f"{g}.xlsx"))
                        st.rerun()
                with col3:
                    if st.button(f"🗑️ Excluir", key=f"del_{g}", use_container_width=True):
                        os.remove(caminho_g)
                        if os.path.exists(caminho_inf_g):
                            os.remove(caminho_inf_g)
                        st.rerun()

                mostrar_upload = st.toggle(
                    f"📁 Atualizar Base de Dados (.xlsx) — {g.replace('_', ' ')}",
                    key=f"tog_up_{g}"
                )
                if mostrar_upload:
                    novo_excel = st.file_uploader(
                        "Selecionar ficheiro Excel atualizado:",
                        type=["xlsx"],
                        key=f"up_{g}"
                    )
                    if novo_excel is not None:
                        df_novo = pd.read_excel(novo_excel)
                        df_novo.to_excel(caminho_g, index=False)
                        st.success("Base de dados atualizada com sucesso!")

                st.markdown("---")
        else:
            st.info("Nenhum evento corresponde aos filtros aplicados.")
    else:
        st.info("Nenhum evento encontrado nesta categoria.")

# --- TELA 3: ÁREA INTERNA DO EVENTO ---
elif st.session_state.pagina == 'evento_interno' and st.session_state.evento_ativo:
    if st.button("← Voltar ao Painel"):
        navegar('painel')

    g_ativo = st.session_state.evento_ativo
    pasta_alvo = PASTA_VIAGENS if st.session_state.cat_ativa == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{g_ativo}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{g_ativo}_info.json")

    if os.path.exists(caminho_arquivo):
        st.title(f"Operação: {g_ativo.replace('_', ' ')}")
        st.markdown("---")

        info_data = carregar_info(caminho_info)
        
        # Garante ID
        if not info_data.get('id_evento'):
            info_data['id_evento'] = f"EVT-{str(uuid.uuid4())[:6].upper()}"
            salvar_info(caminho_info, info_data)

        df = pd.read_excel(caminho_arquivo)
        col_id = df.columns[0]
        col_nome = df.columns[1]
        col_ficha = df.columns[5] if len(df.columns) > 5 else df.columns[-1]

        if 'Status Entrada' not in df.columns:
            df['Status Entrada'] = "Pendente"
        if 'Status Saida' not in df.columns:
            df['Status Saida'] = "Pendente"

        aba_info, aba_chamada, aba_saida = st.tabs(["📌 Informações & Relatório", "📥 Entrada", "📤 Saída"])

        # ----------------------------------------------------------------------
        # ABA: INFORMAÇÕES (COM EDIÇÃO DE NOME, ID E DATAS)
        # ----------------------------------------------------------------------
        with aba_info:
            st.subheader("Detalhes e Fechamento")

            status_atual = info_data.get("status_evento", "Em Andamento")
            opcoes_status = list(STATUS_EVENTO_OPCOES)
            if status_atual not in opcoes_status:
                opcoes_status.append(status_atual)

            with st.form(f"form_info_{g_ativo}"):
                st.markdown(f"**Identificação Oficial (ID: {info_data.get('id_evento')})**")
                
                novo_nome_evento = st.text_input("Nome do Evento", value=g_ativo.replace('_', ' '))

                c_st1, c_st2 = st.columns(2)
                with c_st1:
                    novo_status = st.selectbox(
                        "Status do evento",
                        opcoes_status,
                        index=opcoes_status.index(status_atual)
                    )
                with c_st2:
                    st.text_input("ID do Evento (Fixo)", value=info_data.get('id_evento'), disabled=True)

                st.markdown("**Período da Operação**")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    nova_data_inicio = st.text_input("Data de Início", value=info_data.get("data_inicio", ""))
                with c_d2:
                    nova_data_fim = st.text_input("Data de Término", value=info_data.get("data_fim", ""))

                st.markdown("**Local e Contatos**")
                c1, c2 = st.columns(2)
                with c1:
                    novo_local = st.text_input("Local", value=info_data.get("local", ""))
                    novo_horario = st.text_input("Horário", value=info_data.get("horario", ""))
                with c2:
                    novo_tel_local = st.text_input("Telefone do local", value=info_data.get("tel_local", ""))
                    novo_drive = st.text_input("Link do Drive de fotos", value=info_data.get("drive_fotos", ""))

                st.markdown("**Logística**")
                c3, c4 = st.columns(2)
                with c3:
                    novo_transporte = st.text_input("Transporte", value=info_data.get("transporte", ""))
                with c4:
                    novo_motorista = st.text_input("Motorista", value=info_data.get("motorista", ""))

                nova_equipe = st.text_area("Equipe", value=info_data.get("equipe", ""), height=100)
                novo_roteiro = st.text_area("Roteiro", value=info_data.get("roteiro", ""), height=150)

                salvar = st.form_submit_button("💾 Salvar Informações", use_container_width=True)

            if salvar:
                novo_slug = novo_nome_evento.strip().replace(' ', '_')
                
                # Atualiza dicionário de info
                info_data.update({
                    "status_evento": novo_status,
                    "data_inicio": nova_data_inicio.strip(),
                    "data_fim": nova_data_fim.strip(),
                    "local": novo_local.strip(),
                    "tel_local": novo_tel_local.strip(),
                    "horario": novo_horario.strip(),
                    "roteiro": novo_roteiro.strip(),
                    "transporte": novo_transporte.strip(),
                    "motorista": novo_motorista.strip(),
                    "equipe": nova_equipe.strip(),
                    "drive_fotos": novo_drive.strip(),
                })

                # Se o nome mudou, renomeia os ficheiros físicos no disco
                if novo_slug != g_ativo:
                    novo_caminho_arq = os.path.join(pasta_alvo, f"{novo_slug}.xlsx")
                    novo_caminho_inf = os.path.join(PASTA_INFO, f"{novo_slug}_info.json")
                    
                    if os.path.exists(novo_caminho_arq):
                        st.error("Já existe um evento ativo com este novo nome.")
                    else:
                        os.rename(caminho_arquivo, novo_caminho_arq)
                        if os.path.exists(caminho_info):
                            os.rename(caminho_info, novo_caminho_inf)
                        salvar_info(novo_caminho_inf, info_data)
                        st.session_state.evento_ativo = novo_slug
                        st.success("Nome do evento e ficheiros atualizados com sucesso!")
                        st.rerun()
                else:
                    salvar_info(caminho_info, info_data)
                    st.success("Informações do evento atualizadas com sucesso!")
                    st.rerun()

            if info_data.get("drive_fotos"):
                st.link_button("📷 Abrir Drive de Fotos", info_data["drive_fotos"], use_container_width=True)

            st.markdown("---")

            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Participantes", index=False)

            st.download_button(
                label="📥 Baixar Planilha Atualizada (.xlsx)",
                data=output_excel.getvalue(),
                file_name=f"Relatorio_{g_ativo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with aba_chamada:
            pesquisa = st.text_input("🔍 Pesquisar participante:", key="pesq_part")
            df_filt = df[df[col_nome].astype(str).str.contains(pesquisa, case=False, na=False)] if pesquisa else df

            with st.form("form_chamada"):
                novos_status = {}
                for i, row in df_filt.iterrows():
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).lower() not in ["", "nao ha.", "nenhum"] else None
                    st.write(f"**{row[col_id]}** — {row[col_nome]}")
                    s_atual = str(row['Status Entrada']) if pd.notna(row['Status Entrada']) else "Pendente"

                    novos_status[i] = st.radio(
                        f"Status_{i}", ["Pendente", "Presente", "Faltou"],
                        index=["Pendente", "Presente", "Faltou"].index(s_atual) if s_atual in ["Pendente", "Presente", "Faltou"] else 0,
                        key=f"ent_{i}", horizontal=True, label_visibility="collapsed"
                    )
                    if ficha:
                        st.markdown(f"<div class='alerta-medico'>⚠️ ALERTA MÉDICO: {ficha}</div>", unsafe_allow_html=True)
                    st.markdown("---")

                if st.form_submit_button("✅ Guardar Chamada", use_container_width=True):
                    for idx, val in novos_status.items():
                        df.at[idx, 'Status Entrada'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Alterações guardadas com sucesso!")
                    st.rerun()

        with aba_saida:
            with st.form("form_saida_controlo"):
                novos_status_s = {}
                for i, row in df.iterrows():
                    st.write(f"**{row[col_id]}** — {row[col_nome]}")
                    s_atual_s = str(row['Status Saida']) if pd.notna(row['Status Saida']) else "Pendente"
                    novos_status_s[i] = st.radio(
                        f"Saida_{i}", ["Pendente", "Entregue", "Atenção"],
                        index=["Pendente", "Entregue", "Atenção"].index(s_atual_s) if s_atual_s in ["Pendente", "Entregue", "Atenção"] else 0,
                        key=f"sai_{i}", horizontal=True, label_visibility="collapsed"
                    )
                    st.markdown("---")

                if st.form_submit_button("✅ Guardar Saída", use_container_width=True):
                    for idx, val in novos_status_s.items():
                        df.at[idx, 'Status Saida'] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Controlo de saída guardado!")
                    st.rerun()

# --- TELA 4: CADASTRAR NOVO EVENTO ---
elif st.session_state.pagina == 'cadastrar':
    if st.button("← Voltar"):
        navegar('home')
    st.title("Cadastrar Nova Operação")

    categoria_evento = st.radio("Categoria:", ["Viagens e Excursões", "Festas e Eventos"])
    pasta_destino = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS

    with st.form("form_novo_evento"):
        nome_grupo = st.text_input("Nome do Evento:")
        c_cad1, c_cad2 = st.columns(2)
        with c_cad1:
            data_ini_novo = st.text_input("Data de Início (ex: 01/11/2027)")
        with c_cad2:
            data_fim_novo = st.text_input("Data de Término (ex: 01/11/2027)")

        if st.form_submit_button("Criar Estrutura") and nome_grupo.strip():
            nome_arquivo = nome_grupo.strip().replace(' ', '_')
            caminho = os.path.join(pasta_destino, f"{nome_arquivo}.xlsx")
            if not os.path.exists(caminho):
                # Cria planilha padrão com ID e nome de exemplo
                pd.DataFrame({
                    "ID": ["ID-001"], 
                    "Nome": ["Participante Exemplo"], 
                    "Ficha Médica": ["Nenhum"]
                }).to_excel(caminho, index=False)
                
                # Gera ID único para o evento
                novo_id_evt = f"EVT-{str(uuid.uuid4())[:6].upper()}"
                
                salvar_info(os.path.join(PASTA_INFO, f"{nome_arquivo}_info.json"), {
                    "id_evento": novo_id_evt,
                    "status_evento": "Em Andamento",
                    "data_inicio": data_ini_novo.strip(),
                    "data_fim": data_fim_novo.strip(),
                    "local": "",
                    "tel_local": "",
                    "horario": "",
                    "roteiro": "",
                    "transporte": "",
                    "motorista": "",
                    "equipe": "",
                    "drive_fotos": "",
                })
                st.success("Operação criada com sucesso!")
                navegar('painel')
            else:
                st.warning("Já existe um evento com este nome.")

# --- TELA 5: ARQUIVADOS ---
elif st.session_state.pagina == 'arquivo':
    if st.button("← Voltar"):
        navegar('home')
    st.title("Operações Arquivadas")

    arquivados = listar_grupos(PASTA_ARQUIVO)
    if arquivados:
        nomes_cat = {"viagens": "Viagens e Excursões", "festas": "Festas e Eventos"}
        pastas_cat = {"viagens": PASTA_VIAGENS, "festas": PASTA_FESTAS}

        for arq in arquivados:
            info_arq = carregar_info(os.path.join(PASTA_INFO, f"{arq}_info.json"))
            cat_origem = info_arq.get("categoria_origem")
            id_arq = info_arq.get("id_evento", "SEM-ID")

            etiqueta = (
                f" <span style='font-size:12px; color:#64748B;'>({nomes_cat[cat_origem]}) — ID: {id_arq}</span>"
                if cat_origem in nomes_cat else f" — ID: {id_arq}"
            )
            st.markdown(
                f"<div class='card-evento'><b>{arq.replace('_', ' ')}</b>{etiqueta}</div>",
                unsafe_allow_html=True
            )

            if cat_origem in nomes_cat:
                cat_destino = cat_origem
            else:
                escolha = st.radio(
                    "Restaurar para:",
                    list(nomes_cat.values()),
                    key=f"cat_des_{arq}",
                    horizontal=True
                )
                cat_destino = "viagens" if escolha == nomes_cat["viagens"] else "festas"

            if st.button(f"Desarquivar {arq.replace('_', ' ')}", key=f"des_{arq}"):
                origem = os.path.join(PASTA_ARQUIVO, f"{arq}.xlsx")
                destino = os.path.join(pastas_cat[cat_destino], f"{arq}.xlsx")
                if os.path.exists(destino):
                    st.warning("Já existe um evento ativo com este nome nessa categoria.")
                else:
                    os.rename(origem, destino)
                    st.rerun()
    else:
        st.info("Nenhum evento arquivado.")
