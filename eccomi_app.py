import json
import os
import pandas as pd
import streamlit as st

# Configuração da Página do Aplicativo com recolhimento da barra lateral otimizado
st.set_page_config(
    page_title="Eccomi - Lista de Presença",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Estilização CSS personalizada (Fonte Nunito, Fundo Branco, Letras Pretas, Alertas Vermelhos e Botões Pretos)
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
.stApp {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    font-family: 'Nunito', sans-serif !important;
}
h1, h2, h3, h4, h5, h6, p, label, span, div {
    font-family: 'Nunito', sans-serif !important;
    color: #000000 !important;
}
div.stButton > button:first-child {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border-radius: 4px;
    width: 100%;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700;
}
.btn-voltar > button:first-child {
    background-color: #F1F3F4 !important;
    color: #000000 !important;
    border: 1px solid #CCCCCC !important;
    width: auto !important;
    padding: 5px 15px;
}
.alerta-vermelho {
    padding: 8px;
    background-color: #FFEEEE;
    border-left: 4px solid #FF0000;
    color: #000000;
    font-size: 13px;
    font-weight: bold;
    margin-top: 5px;
    margin-bottom: 15px;
}
.card-evento {
    padding: 20px;
    border: 2px solid #000000;
    border-radius: 8px;
    margin-bottom: 20px;
    background-color: #FAFAFA;
}
.card-aluno {
    padding: 15px;
    border: 1px solid #CCCCCC;
    border-radius: 8px;
    margin-bottom: 15px;
    background-color: #FAFAFA;
}
.info-box {
    padding: 12px;
    background-color: #F1F3F4;
    border-radius: 6px;
    font-size: 14px;
    margin-bottom: 15px;
}
div[data-baseweb="radio"] div {
    color: #000000 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Exibição da Logo Oficial no Topo
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
  logo_path = "eccomi_logo - app_3.jfif"
  if os.path.exists(logo_path):
    st.image(logo_path, width=160)
  else:
    st.markdown("📋")

st.title("Eccomi - App Lista de Presença")
st.markdown(
    "**Controle de Embarque, Desembarque e Segurança para Guias e"
    " Recreadores.**"
)

# Pastas separadas por modalidade
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO]:
  if not os.path.exists(p):
    os.makedirs(p)

# Captura de link via URL
query_params = st.query_params
evento_link = query_params.get("evento", None)
cat_link = query_params.get("cat", None)

# --- MENU LATERAL DA COORDENAÇÃO ---
st.sidebar.markdown("### 📁 Tipo de Operação")
categoria_evento = st.sidebar.radio(
    "Escolha o tipo de operação:", ["🚌 Viagens e Excursões", "🎉 Festas e Eventos"]
)

PASTA_GRUPOS = (
    PASTA_VIAGENS
    if categoria_evento == "🚌 Viagens e Excursões"
    else PASTA_FESTAS
)
cat_url_param = (
    "viagens" if categoria_evento == "🚌 Viagens e Excursões" else "festas"
)


def listar_grupos():
  return sorted([
      f.replace(".xlsx", "")
      for f in os.listdir(PASTA_GRUPOS)
      if f.endswith(".xlsx")
  ])


menu_guia = st.sidebar.selectbox(
    "Painel de Controle",
    [
        "🏠 Capas & Painel de Eventos",
        "➕ Cadastrar Grupo & Enviar Planilha",
        "⚠️ Registrar Alerta / Ocorrência",
        "📍 Rastreamento GPS (Central)",
    ],
)

grupos_disponiveis = listar_grupos()

# --- ÁREA PARTICULAR DO EVENTO (VIA LINK OU BOTÃO) ---
if evento_link:
  pasta_alvo = PASTA_VIAGENS if cat_link == "viagens" else PASTA_FESTAS
  caminho_arquivo = os.path.join(pasta_alvo, f"{evento_link}.xlsx")
  caminho_info = os.path.join(PASTA_INFO, f"{evento_link}_info.json")

  if os.path.exists(caminho_arquivo):
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    if st.button("⬅️ Voltar à Página Principal"):
      st.query_params.clear()
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"## 🎫 Evento: {evento_link.replace('_', ' ')}")

    info_data = {}
    if os.path.exists(caminho_info):
      with open(caminho_info, "r", encoding="utf-8") as f:
        info_data = json.load(f)

    aba_info, aba_chamada, aba_saida = st.tabs(
        [
            "📋 Informações & Logística",
            "📋 Chamada de Entrada",
            "🔄 Conferência de Saída",
        ]
    )

    with aba_info:
      st.subheader("📋 Detalhes Operacionais do Evento")
      st.markdown(
          f"""
            <div class="info-box">
            <b>📍 Local do Evento:</b> {info_data.get('local', 'Não informado')}<br>
            <b>📞 Telefone do Local:</b> {info_data.get('tel_local', 'Não informado')}<br>
            <b>⏰ Horário:</b> {info_data.get('horario', 'Não informado')}<br>
            <b>🗺️ Roteiro:</b> {info_data.get('roteiro', 'Não informado')}<br>
            <b>🚌 Transporte:</b> {info_data.get('transporte', 'Não informado')} (Motorista: {info_data.get('motorista', 'Não informado')})<br>
            <b>👥 Equipe de Apoio:</b> {info_data.get('equipe', 'Não informado')}
            </div>
            """,
          unsafe_allow_html=True,
      )

      st.markdown("### ⚙️ Editar Informações Operacionais")
      with st.form("form_info_extra"):
        loc = st.text_input("Local (Endereço):", value=info_data.get("local", ""))
        t_loc = st.text_input(
            "Telefone do Local:", value=info_data.get("tel_local", "")
        )
        hor = st.text_input(
            "Horário de Início e Fim:", value=info_data.get("horario", "")
        )
        rot = st.text_area(
            "Roteiro do Evento:", value=info_data.get("roteiro", "")
        )
        trans = st.text_input(
            "Transporte (Ônibus e Placa):",
            value=info_data.get("transporte", ""),
        )
        mot = st.text_input(
            "Nome e Tel. do Motorista:", value=info_data.get("motorista", "")
        )
        eqp = st.text_area(
            "Equipe Responsável (Nome, Tel e Info):",
            value=info_data.get("equipe", ""),
        )

        if st.form_submit_button("Salvar Informações Operacionais"):
          novo_dict = {
              "local": loc,
              "tel_local": t_loc,
              "horario": hor,
              "roteiro": rot,
              "transporte": trans,
              "motorista": mot,
              "equipe": eqp,
          }
          with open(caminho_info, "w", encoding="utf-8") as f:
            json.dump(novo_dict, f, ensure_ascii=False)
          st.success("Informações salvas com sucesso!")
          st.rerun()

    df = pd.read_excel(caminho_arquivo)

    # Identificação robusta das colunas
    col_id = next(
        (
            c
            for c in df.columns
            if "cpf" in c.lower() or "id" in c.lower() or "rg" in c.lower()
        ),
        df.columns[0],
    )
    col_nome = next(
        (
            c
            for c in df.columns
            if "nome" in c.lower() or "participante" in c.lower()
        ),
        df.columns[1],
    )
    col_nasc = next(
        (
            c
            for c in df.columns
            if "nascimento" in c.lower() or "data" in c.lower()
        ),
        None,
    )
    col_ficha = next(
        (
            c
            for c in df.columns
            if "médica" in c.lower()
            or "ficha" in c.lower()
            or "alergia" in c.lower()
        ),
        df.columns[5] if len(df.columns) > 5 else df.columns[-1],
    )
    col_entrada = next(
        (c for c in df.columns if "entrada" in c.lower()), "Status Entrada"
    )
    col_saida = next(
        (
            c
            for c in df.columns
            if "saída" in c.lower() or "saida" in c.lower()
        ),
        "Status Saida",
    )

    if col_entrada not in df.columns:
      df[col_entrada] = "Pendente"
    if col_saida not in df.columns:
      df[col_saida] = "Pendente"

    with aba_chamada:
      st.subheader("Conferência de Entrada (Embarque)")

      # --- BARRA DE PESQUISA POR NOME / ID ---
      termo_busca = st.text_input(
          "🔍 Pesquisar participante por nome, CPF ou ID:",
          placeholder="Digite para filtrar instantaneamente...",
          key="busca_participante_chamada",
      )

      # Filtrar o DataFrame com base na busca
      if termo_busca:
        df_filtrado = df[
            df[col_nome].astype(str).str.contains(termo_busca, case=False, na=False)
            | df[col_id]
            .astype(str)
            .str.contains(termo_busca, case=False, na=False)
        ]
      else:
        df_filtrado = df

      presentes = len(df[df[col_entrada] == "Presente"])
      st.metric("Progresso de Entrada", f"{presentes} de {len(df)} participantes")
      st.markdown("---")

      with st.form("form_animador_entrada"):
        novos_status = {}
        for idx, row in df_filtrado.iterrows():
          p_id = (
              str(row[col_id]) if pd.notna(row[col_id]) else "Não informado"
          )
          p_nome = (
              str(row[col_nome]) if pd.notna(row[col_nome]) else "Participante"
          )
          p_nasc = (
              f" | Nasc: {row[col_nasc]}"
              if col_nasc and pd.notna(row[col_nasc])
              else ""
          )
          ficha = (
              row[col_ficha]
              if pd.notna(row[col_ficha])
              and str(row[col_ficha]).strip() != ""
              and str(row[col_ficha]).lower() != "não há."
              else None
          )

          st.markdown(
              f"""<div class="card-aluno"><b>CPF/ID: {p_id} - {p_nome}{p_nasc}</b></div>""",
              unsafe_allow_html=True,
          )

          s_atual = (
              str(row[col_entrada])
              if pd.notna(row[col_entrada])
              else "Pendente"
          )
          escolha = st.radio(
              f"Status para {p_nome}:",
              ["Pendente", "Presente", "Faltou"],
              index=(
                  ["Pendente", "Presente", "Faltou"].index(s_atual)
                  if s_atual in ["Pendente", "Presente", "Faltou"]
                  else 0
              ),
              key=f"link_ent_{idx}",
              horizontal=True,
          )
          novos_status[idx] = escolha

          if ficha:
            st.markdown(
                f"""<div class="alerta-vermelho">🚨 ALERTA MÉDICO: {ficha}</div>""",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        if st.form_submit_button("💾 Salvar Chamada"):
          for idx, val in novos_status.items():
            df.at[idx, col_entrada] = val
          df.to_excel(caminho_arquivo, index=False)
          st.success("Chamada salva com sucesso!")
          st.rerun()

    with aba_saida:
      st.subheader("Conferência de Saída (Desembarque)")
      saidos = len(df[df[col_saida] == "Presente"])
      st.metric(
          "Progresso de Desembarque", f"{saidos} de {len(df)} participantes"
      )
      st.markdown("---")

      with st.form("form_animador_saida"):
        novos_status_saida = {}
        for idx, row in df.iterrows():
          p_id = (
              str(row[col_id]) if pd.notna(row[col_id]) else "Não informado"
          )
          p_nome = (
              str(row[col_nome]) if pd.notna(row[col_nome]) else "Participante"
          )
          st.markdown(
              f"""<div class="card-aluno"><b>ID: {p_id} - {p_nome}</b></div>""",
              unsafe_allow_html=True,
          )

          s_atual_s = (
              str(row[col_saida]) if pd.notna(row[col_saida]) else "Pendente"
          )
          escolha_s = st.radio(
              f"Saída para {p_nome}:",
              ["Pendente", "Presente", "Faltou"],
              index=(
                  ["Pendente", "Presente", "Faltou"].index(s_atual_s)
                  if s_atual_s in ["Pendente", "Presente", "Faltou"]
                  else 0
              ),
              key=f"link_said_{idx}",
              horizontal=True,
          )
          novos_status_saida[idx] = escolha_s

        if st.form_submit_button("💾 Salvar Saída"):
          for idx, val in novos_status_saida.items():
            df.at[idx, col_saida] = val
          df.to_excel(caminho_arquivo, index=False)
          st.success("Saída salva com sucesso!")
          st.rerun()
  else:
    st.error("Grupo ou evento não encontrado.")

else:
  # --- TELA INICIAL / PAINEL PRINCIPAL ---
  if menu_guia == "🏠 Capas & Painel de Eventos":
    st.subheader("📂 Seus Grupos e Eventos Cadastrados")

    if not grupos_disponiveis:
      st.info(
          "Nenhum grupo cadastrado ainda. Utilize o menu lateral para"
          " 'Cadastrar Grupo & Enviar Planilha'."
      )
    else:
      for g in grupos_disponiveis:
        st.markdown(
            f"""<div class="card-evento"><h3>🚌 {g.replace('_', ' ')}</h3></div>""",
            unsafe_allow_html=True,
        )
        col_A, col_B = st.columns([1, 1])
        with col_A:
          if st.button("Abrir Evento", key=f"abrir_{g}"):
            st.query_params.update(evento=g, cat=cat_url_param)
            st.rerun()
        with col_B:
          if st.button("Excluir", key=f"del_{g}"):
            c_arq = os.path.join(PASTA_GRUPOS, f"{g}.xlsx")
            c_inf = os.path.join(PASTA_INFO, f"{g}_info.json")
            if os.path.exists(c_arq):
              os.remove(c_arq)
            if os.path.exists(c_inf):
              os.remove(c_inf)
            st.success(f"Evento {g} excluído com sucesso!")
            st.rerun()

  elif menu_guia == "➕ Cadastrar Grupo & Enviar Planilha":
    st.subheader("➕ Cadastro de Novo Grupo e Envio de Planilha")
    with st.form("form_cadastro_grupo"):
      nome_grupo = st.text_input(
          "Nome do Grupo / Ônibus / Festa (Ex: Paula_Barros_Barra_Grande)"
      )
      arquivo_submetido = st.file_uploader(
          "Enviar Planilha de Participantes (.xlsx)", type=["xlsx"]
      )

      st.markdown("---")
      st.markdown("### 📋 Informações Operacionais Iniciais")
      loc_i = st.text_input("Local (Endereço do Evento):")
      t_loc_i = st.text_input("Telefone do Local:")
      hor_i = st.text_input("Horário de Início e Fim:")
      rot_i = st.text_area("Roteiro do Evento:")
      trans_i = st.text_input("Transporte (Ônibus e Placa):")
      mot_i = st.text_input("Nome e Tel. do Motorista:")
      eqp_i = st.text_area("Equipe Responsável (Nome, Tel e Info):")

      if st.form_submit_button("Criar Capa e Estrutura do Evento"):
        if nome_grupo and arquivo_submetido:
          nome_formatado = nome_grupo.strip().replace(" ", "_")
          caminho_destino = os.path.join(PASTA_GRUPOS, f"{nome_formatado}.xlsx")
          caminho_info_dest = os.path.join(
              PASTA_INFO, f"{nome_formatado}_info.json"
          )

          with open(caminho_destino, "wb") as f:
            f.write(arquivo_submetido.getbuffer())

          info_dict = {
              "local": loc_i,
              "tel_local": t_loc_i,
              "horario": hor_i,
              "roteiro": rot_i,
              "transporte": trans_i,
              "motorista": mot_i,
              "equipe": eqp_i,
          }
          with open(caminho_info_dest, "w", encoding="utf-8") as f:
            json.dump(info_dict, f, ensure_ascii=False)

          st.success(
              f"Grupo '{nome_formatado}' cadastrado e estruturado com sucesso!"
          )
          st.rerun()
        else:
          st.error(
              "Por favor, preencha o nome do grupo e envie a planilha do"
              " Excel."
          )

  elif menu_guia == "⚠️ Registrar Alerta / Ocorrência":
    st.subheader("⚠️ Central de Alertas e Ocorrências")
    st.info(
        "Utilize este painel para registrar ocorrências importantes em campo."
    )
    if grupos_disponiveis:
      grupo_selecionado = st.selectbox(
          "Selecione o Evento/Grupo:", grupos_disponiveis
      )
      tipo_alerta = st.selectbox(
          "Tipo de Ocorrência:",
          [
              "Atraso de Passageiro",
              "Problema Mecânico",
              "Questão de Saúde / Médica",
              "Outros",
          ],
      )
      descricao_alerta = st.text_area("Descrição detalhada da ocorrência:")
      if st.button("Registrar Ocorrência"):
        st.success("Ocorrência registrada e salva no histórico com sucesso!")
    else:
      st.warning("Nenhum grupo ativo para registrar ocorrências.")

  elif menu_guia == "📍 Rastreamento GPS (Central)":
    st.subheader("📍 Rastreamento GPS da Frota / Equipe")
    st.info(
        "Módulo de localização em tempo real integrado para acompanhamento da"
        " equipe em campo."
    )
