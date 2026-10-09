import os
import json
import io
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
    """Lê o JSON de informações do evento (devolve {} se não existir ou estiver inválido)."""
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados if isinstance(dados, dict) else {}
        except Exception:
            return {}
    return {}

def salvar_info(caminho, dados):
    """Grava o JSON de informações do evento."""
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
            local_ev = dados_inf.get('local') or "Não informado"
            status_ev = dados_inf.get('status_evento') or "Em Andamento"

            st.markdown(f"""
                <div class="card-evento">
                    <h3 style="margin:0 0 8px 0; font-size: 18px;">{g.replace('_', ' ')} <span style="font-size:12px; font-weight:normal; color:#64748B;">({cat_nome})</span></h3>
                    <p style="margin:4px 0;"><b>Status:</b> {status_ev} | <b>Local:</b> {local_ev}</p>
                    <p style="margin:4px 0; color: #475569;">Total: <b>{total_part}</b> | ✅ Presentes: <b>{presentes}</b> | ❌ Faltosos: <b>{faltosos}</b></p>
                </div>
            """, unsafe_allow_html=True)
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
    termo_busca = st.text_input("🔍 Pesquisar evento:")

    if grupos_disponiveis:
        eventos_filtrados = [g for g in grupos_disponiveis if termo_busca.lower() in g.lower()] if termo_busca else grupos_disponiveis

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
            linha_local = ""
            if info_g.get("local") or info_g.get("horario"):
                linha_local = (
                    f"<p style='margin:4px 0;'><b>Local:</b> {info_g.get('local', '—')} | "
                    f"<b>Horário:</b> {info_g.get('horario', '—')}</p>"
                )

            st.markdown(f"""
                <div class="card-evento">
                    <h4 style="margin:0;">{g.replace('_', ' ')}</h4>
                    {linha_local}
                    <p style="margin:4px 0; color: #475569;">Check-in: {presentes_p} de {total_p} confirmados</p>
                </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🚀 Abrir", key=f"abrir_{g}", use_container_width=True):
                    abrir_evento(g, cat_param)
            with col2:
                if st.button(f"📦 Arquivar", key=f"arq_{g}", use_container_width=True):
                    # Guarda a categoria de origem para o "Desarquivar" devolver o evento ao sítio certo
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
        # ABA: INFORMAÇÕES (AGORA EDITÁVEL)
        # ----------------------------------------------------------------------
        with aba_info:
            st.subheader("Detalhes e Fechamento")

            # Garante que o status atual aparece na lista, mesmo que seja personalizado
            status_atual = info_data.get("status_evento", "Em Andamento")
            opcoes_status = list(STATUS_EVENTO_OPCOES)
            if status_atual not in opcoes_status:
                opcoes_status.append(status_atual)

            with st.form(f"form_info_{g_ativo}"):
                st.markdown("**Status e local**")
                novo_status = st.selectbox(
                    "Status do evento",
                    opcoes_status,
                    index=opcoes_status.index(status_atual)
                )

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
                # Atualiza só os campos editáveis e preserva qualquer chave extra já existente no JSON
                info_data.update({
                    "status_evento": novo_status,
                    "local": novo_local.strip(),
                    "tel_local": novo_tel_local.strip(),
                    "horario": novo_horario.strip(),
                    "roteiro": novo_roteiro.strip(),
                    "transporte": novo_transporte.strip(),
                    "motorista": novo_motorista.strip(),
                    "equipe": nova_equipe.strip(),
                    "drive_fotos": novo_drive.strip(),
                })
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
        if st.form_submit_button("Criar Estrutura") and nome_grupo.strip():
            nome_arquivo = nome_grupo.strip().replace(' ', '_')
            caminho = os.path.join(pasta_destino, f"{nome_arquivo}.xlsx")
            if not os.path.exists(caminho):
                pd.DataFrame({"ID": ["001"], "Nome": ["Participante Exemplo"], "Ficha Médica": ["Nenhum"]}).to_excel(caminho, index=False)
                # Cria também o JSON de informações, pronto para ser editado na aba do evento
                salvar_info(os.path.join(PASTA_INFO, f"{nome_arquivo}_info.json"), {
                    "status_evento": "Em Andamento",
                    "local": "",
                    "tel_local": "",
                    "horario": "",
                    "roteiro": "",
                    "transporte": "",
                    "motorista": "",
                    "equipe": "",
                    "drive_fotos": "",
                })
                st.success("Criado com sucesso!")
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

            etiqueta = (
                f" <span style='font-size:12px; color:#64748B;'>({nomes_cat[cat_origem]})</span>"
                if cat_origem in nomes_cat else ""
            )
            st.markdown(
                f"<div class='card-evento'><b>{arq.replace('_', ' ')}</b>{etiqueta}</div>",
                unsafe_allow_html=True
            )

            if cat_origem in nomes_cat:
                cat_destino = cat_origem
            else:
                # Eventos arquivados antes desta correção não têm categoria guardada: pergunta ao utilizador
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
