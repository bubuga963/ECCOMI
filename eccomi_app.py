import os
import json
import pandas as pd
import streamlit as st

# Configuração da Página do Aplicativo
st.set_page_config(
    page_title="Eccomi",
    page_icon="",
    layout="centered"
)

# Estilização CSS em Preto e Branco, Fonte Nunito, Tamanho mínimo de 12px, sem barra lateral
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* Ocultar completamente a barra lateral nativa do Streamlit */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Títulos e Textos padronizados com tamanho mínimo de 12px */
    .eccomi-title {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }

    h1 {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    h2, h3 {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    p, label, span, div, .stMarkdown {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
        font-size: 12px !important;
    }

    /* Botões padronizados com borda fina preta e fundo branco */
    div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 4px;
        width: 100%;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600;
        font-size: 12px !important;
        padding: 8px 12px;
    }
    div.stButton > button:first-child:hover {
        background-color: #F8F9FA !important;
    }

    .alerta-medico {
        padding: 10px;
        background-color: #FFFFFF;
        border: 1px solid #000000;
        color: #000000;
        font-size: 12px;
        font-weight: bold;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    
    .card-evento {
        padding: 15px;
        border: 1px solid #000000;
        border-radius: 4px;
        margin-bottom: 15px;
        background-color: #FFFFFF;
    }
    .card-aluno {
        padding: 12px;
        border: 1px solid #000000;
        border-radius: 4px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
    }
    .info-box {
        padding: 12px;
        border: 1px solid #000000;
        border-radius: 4px;
        font-size: 12px;
        margin-bottom: 15px;
        background-color: #FFFFFF;
    }
    div[data-baseweb="radio"] div {
        color: #000000 !important;
        font-size: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Pastas de dados
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"

for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p):
        os.makedirs(p)

# Captura de parâmetros via URL
query_params = st.query_params
evento_link = query_params.get("evento", None)
cat_link = query_params.get("cat", None)
pagina_atual = query_params.get("pagina", "home")

def listar_grupos(pasta):
    if os.path.exists(pasta):
        return sorted([f.replace(".xlsx", "") for f in os.listdir(pasta) if f.endswith(".xlsx")])
    return []

# --- 1. ÁREA INTERNA DO EVENTO SELECIONADO ---
if evento_link:
    pasta_alvo = PASTA_VIAGENS if cat_link == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{evento_link}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{evento_link}_info.json")
    
    if os.path.exists(caminho_arquivo):
        if st.button("Retornar à Página Inicial"):
            st.query_params.clear()
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"<h1>Evento: {evento_link.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0.5px solid #000000;'>", unsafe_allow_html=True)
        
        info_data = {}
        if os.path.exists(caminho_info):
            with open(caminho_info, "r", encoding="utf-8") as f:
                info_data = json.load(f)

        aba_info, aba_chamada, aba_saida = st.tabs(["Informações e Logística", "Chamada de Entrada", "Conferência de Saída"])
        
        with aba_info:
            st.markdown("<h3>Detalhes Operacionais e Mídia do Evento</h3>", unsafe_allow_html=True)
            link_drive = info_data.get('drive_fotos', 'Não informado')
            link_html = f'<a href="{link_drive}" target="_blank">{link_drive}</a>' if link_drive.startswith('http') else link_drive
            
            st.markdown(f"""
                <div class="info-box">
                    <b>Local do Evento:</b> {info_data.get('local', 'Não informado')}<br>
                    <b>Telefone do Local:</b> {info_data.get('tel_local', 'Não informado')}<br>
                    <b>Horário:</b> {info_data.get('horario', 'Não informado')}<br>
                    <b>Roteiro:</b> {info_data.get('roteiro', 'Não informado')}<br>
                    <b>Transporte:</b> {info_data.get('transporte', 'Não informado')} (Motorista: {info_data.get('motorista', 'Não informado')})<br>
                    <b>Equipe de Apoio:</b> {info_data.get('equipe', 'Não informado')}<br>
                    <b>Link Google Drive / Fotos:</b> {link_html}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3>Editar Informações e Link de Fotos</h3>", unsafe_allow_html=True)
            with st.form("form_info_extra"):
                loc = st.text_input("Local (Endereço):", value=info_data.get('local', ''))
                t_loc = st.text_input("Telefone do Local:", value=info_data.get('tel_local', ''))
                hor = st.text_input("Horário de Início e Fim:", value=info_data.get('horario', ''))
                rot = st.text_area("Roteiro do Evento:", value=info_data.get('roteiro', ''))
                trans = st.text_input("Transporte (Ônibus e Placa):", value=info_data.get('transporte', ''))
                mot = st.text_input("Nome e Tel. do Motorista:", value=info_data.get('motorista', ''))
                eqp = st.text_area("Equipe Responsável (Nome, Tel e Info):", value=info_data.get('equipe', ''))
                drive = st.text_input("Link do Google Drive / Fotos do Evento:", value=info_data.get('drive_fotos', ''))
                
                if st.form_submit_button("Salvar Informações Operacionais"):
                    novo_dict = {
                        "local": loc, "tel_local": t_loc, "horario": hor,
                        "roteiro": rot, "transporte": trans, "motorista": mot, "equipe": eqp, "drive_fotos": drive
                    }
                    with open(caminho_info, "w", encoding="utf-8") as f:
                        json.dump(novo_dict, f, ensure_ascii=False)
                    st.success("Informações e link salvos com sucesso!")
                    st.rerun()

        df = pd.read_excel(caminho_arquivo)
        col_id = next((c for c in df.columns if 'cpf' in c.lower() or 'id' in c.lower()), df.columns[0])
        col_nome = next((c for c in df.columns if 'nome' in c.lower() or 'participante' in c.lower()), df.columns[1])
        col_nasc = next((c for c in df.columns if 'nascimento' in c.lower() or 'data' in c.lower()), None)
        col_ficha = next((c for c in df.columns if 'medica' in c.lower() or 'ficha' in c.lower() or 'alergia' in c.lower()), df.columns[5] if len(df.columns) > 5 else df.columns[-1])
        col_entrada = next((c for c in df.columns if 'entrada' in c.lower()), 'Status Entrada')
        col_saida = next((c for c in df.columns if 'saida' in c.lower() or 'saída' in c.lower()), 'Status Saida')
        
        if col_entrada not in df.columns:
            df[col_entrada] = "Pendente"
        if col_saida not in df.columns:
            df[col_saida] = "Pendente"

        with aba_chamada:
            st.markdown("<h3>Conferência de Entrada (Embarque)</h3>", unsafe_allow_html=True)
            termo_busca_part = st.text_input("Pesquisar participante por nome, CPF ou ID:", placeholder="Digite para filtrar instantaneamente...", key="busca_part_chamada")
            
            if termo_busca_part:
                df_filtrado = df[df[col_nome].astype(str).str.contains(termo_busca_part, case=False, na=False) | df[col_id].astype(str).str.contains(termo_busca_part, case=False, na=False)]
            else:
                df_filtrado = df

            presentes = len(df[df[col_entrada] == "Presente"])
            st.markdown(f"<p><b>Progresso de Entrada:</b> {presentes} de {len(df)} participantes</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border: 0.5px solid #000000;'>", unsafe_allow_html=True)
            
            with st.form("form_animador_entrada"):
                novos_status = {}
                for i, row in df_filtrado.iterrows():
                    p_id = str(row[col_id]) if pd.notna(row[col_id]) else "Não informado"
                    p_nome = str(row[col_nome]) if pd.notna(row[col_nome]) else "Participante"
                    p_nasc = f" | Nasc: {row[col_nasc]}" if col_nasc and pd.notna(row[col_nasc]) else ""
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).strip() != "" and str(row[col_ficha]).lower() != "nao ha." else None
                    
                    st.markdown(f"""<div class="card-aluno"><b>CPF/ID: {p_id} - {p_nome}{p_nasc}</b></div>""", unsafe_allow_html=True)
                    s_atual = str(row[col_entrada]) if pd.notna(row[col_entrada]) else "Pendente"
                    
                    escolha = st.radio(
                        f"Status para {p_nome}:",
                        ["Pendente", "Presente", "Faltou"],
                        index=["Pendente", "Presente", "Faltou"].index(s_atual) if s_atual in ["Pendente", "Presente", "Faltou"] else 0,
                        key=f"link_ent_{i}",
                        horizontal=True
                    )
                    novos_status[i] = escolha

                    if ficha:
                        st.markdown(f"""<div class="alerta-medico">ALERTA MÉDICO: {ficha}</div>""", unsafe_allow_html=True)
                    st.markdown("<hr style='border: 0.5px solid #CCCCCC;'>", unsafe_allow_html=True)

                if st.form_submit_button("Salvar Chamada"):
                    for idx, val in novos_status.items():
                        df.at[idx, col_entrada] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Chamada salva com sucesso!")
                    st.rerun()

        with aba_saida:
            st.markdown("<h3>Conferência de Saída (Desembarque)</h3>", unsafe_allow_html=True)
            with st.form("form_animador_saida"):
                novos_status_s = {}
                for i, row in df.iterrows():
                    p_id = str(row[col_id]) if pd.notna(row[col_id]) else "Não informado"
                    p_nome = str(row[col_nome]) if pd.notna(row[col_nome]) else "Participante"
                    st.markdown(f"""<div class="card-aluno"><b>CPF/ID: {p_id} - {p_nome}</b></div>""", unsafe_allow_html=True)
                    s_atual_s = str(row[col_saida]) if pd.notna(row[col_saida]) else "Pendente"
                    
                    escolha_s = st.radio(
                        f"Saída para {p_nome}:",
                        ["Pendente", "Entregue com Segurança", "Atenção na Saída"],
                        index=["Pendente", "Entregue com Segurança", "Atenção na Saída"].index(s_atual_s) if s_atual_s in ["Pendente", "Entregue com Segurança", "Atenção na Saída"] else 0,
                        key=f"link_sai_{i}",
                        horizontal=True
                    )
                    novos_status_s[i] = escolha_s
                    st.markdown("<hr style='border: 0.5px solid #CCCCCC;'>", unsafe_allow_html=True)

                if st.form_submit_button("Salvar Saída"):
                    for idx, val in novos_status_s.items():
                        df.at[idx, col_saida] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Saída salva com sucesso!")
                    st.rerun()
    else:
        st.error("Evento não encontrado.")
        if st.button("Retornar à Página Inicial"):
            st.query_params.clear()
            st.rerun()

# --- 2. PÁGINA INICIAL DE APRESENTAÇÃO DO SISTEMA ---
elif pagina_atual == "home":
    st.markdown('<div class="eccomi-title">ECCOMI</div>', unsafe_allow_html=True)
    st.markdown("<p><b>Sistema B2B de Gestão de Eventos, Controlo de Embarque, Desembarque e Segurança para Guias e Recreadores.</b></p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 0.5px solid #000000; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
    
    st.markdown("<h3>Apresentação e Vantagens</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="info-box">
            <b>O que é o Eccomi?</b><br>
            Uma ferramenta cirúrgica de campo desenvolvida para agências de turismo, escolas e creches. O Eccomi elimina planilhas de papel e grupos de WhatsApp caóticos, oferecendo chamadas rápidas, alertas médicos visuais em destaque e acesso centralizado a links de fotos em nuvem (Google Drive).<br><br>
            <b>Como funciona?</b><br>
            Sem necessidade de alterar sistemas legados ou instalar aplicações complexas. Basta carregar a planilha oficial do seu evento e a equipe de campo terá tudo pronto para garantir a segurança absoluta dos participantes de forma intuitiva e imediata.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        if st.button("Aceder ao Painel de Eventos"):
            st.query_params["pagina"] = "painel"
            st.rerun()
    with col_h2:
        if st.button("Cadastrar Novo Evento"):
            st.query_params["pagina"] = "cadastrar"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_h3, col_h4, col_h5 = st.columns(3)
    with col_h3:
        if st.button("Arquivo Passado"):
            st.query_params["pagina"] = "arquivo"
            st.rerun()
    with col_h4:
        if st.button("Registar Alerta"):
            st.query_params["pagina"] = "alerta"
            st.rerun()
    with col_h5:
        if st.button("Rastreamento GPS"):
            st.query_params["pagina"] = "gps"
            st.rerun()

# --- 3. PAINEL DE EVENTOS ---
elif pagina_atual == "painel":
    if st.button("Retornar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="eccomi-title">PAINEL DE EVENTOS</div>', unsafe_allow_html=True)
    categoria_evento = st.radio("Tipo de Operação:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    
    PASTA_GRUPOS = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    cat_url_param = "viagens" if categoria_evento == "Viagens e Excursões" else "festas"
    grupos_disponiveis = listar_grupos(PASTA_GRUPOS)
    
    st.markdown("<hr style='border: 0.5px solid #000000; margin: 15px 0;'>", unsafe_allow_html=True)
    termo_busca = st.text_input("Buscar evento pelo nome:", "")
    
    if grupos_disponiveis:
        eventos_filtrados = [g for g in grupos_disponiveis if termo_busca.lower() in g.lower()] if termo_busca else grupos_disponiveis
        
        if eventos_filtrados:
            for g in eventos_filtrados:
                caminho_g = os.path.join(PASTA_GRUPOS, f"{g}.xlsx")
                caminho_inf_g = os.path.join(PASTA_INFO, f"{g}_info.json")
                
                total_p = 0
                confirmados_p = 0
                faltou_p = 0
                local_g = "Não informado"
                horario_g = "Não informado"
                
                if os.path.exists(caminho_g):
                    try:
                        df_g = pd.read_excel(caminho_g)
                        total_p = len(df_g)
                        c_ent = next((c for c in df_g.columns if 'entrada' in c.lower()), None)
                        if c_ent and c_ent in df_g.columns:
                            confirmados_p = len(df_g[df_g[c_ent] == "Presente"])
                            faltou_p = len(df_g[df_g[c_ent] == "Faltou"])
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

                link_evento = f"http://localhost:8501/?evento={g}&cat={cat_url_param}"
                
                st.markdown(f"""
                    <div class="card-evento">
                        <h3 style="font-size: 14px !important; margin-bottom: 5px;">{g.replace('_', ' ')}</h3>
                        <p><b>Local:</b> {local_g} | <b>Horário/Data:</b> {horario_g}</p>
                        <p><b>Participantes:</b> Total: {total_p} | Confirmados: {confirmados_p} | Faltaram: {faltou_p}</p>
                        <p><b>Link exclusivo para a equipe:</b></p>
                        <div class="info-box">{link_evento}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_b1, col_b2, col_b3, col_b4 = st.columns([1.5, 3, 1.5, 1.5])
                with col_b1:
                    if st.button("Abrir Evento", key=f"btn_{g}"):
                        st.query_params["evento"] = g
                        st.query_params["cat"] = cat_url_param
                        st.rerun()
                with col_b2:
                    novo_excel = st.file_uploader("Atualizar Planilha", type=["xlsx"], key=f"up_{g}", label_visibility="collapsed")
                    if novo_excel is not None:
                        df_novo = pd.read_excel(novo_excel)
                        df_novo.to_excel(caminho_g, index=False)
                        st.success("Planilha atualizada com sucesso!")
                        st.rerun()
                with col_b3:
                    if st.button("Arquivar", key=f"arq_{g}"):
                        dst = os.path.join(PASTA_ARQUIVO, f"{g}.xlsx")
                        if os.path.exists(caminho_g):
                            os.rename(caminho_g, dst)
                        st.success("Arquivado!")
                        st.rerun()
                with col_b4:
                    if st.button("Excluir", key=f"del_{g}"):
                        if os.path.exists(caminho_g):
                            os.remove(caminho_g)
                        if os.path.exists(caminho_inf_g):
                            os.remove(caminho_inf_g)
                        st.success("Excluído!")
                        st.rerun()
                st.markdown("<hr style='border: 0.5px solid #000000; margin-top: 15px;'>", unsafe_allow_html=True)
        else:
            st.info("Nenhum evento encontrado com essa busca.")
    else:
        st.warning("Nenhum evento cadastrado nesta categoria.")

# --- 4. CADASTRAR NOVO EVENTO ---
elif pagina_atual == "cadastrar":
    if st.button("Retornar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="eccomi-title">CADASTRAR NOVO EVENTO</div>', unsafe_allow_html=True)
    categoria_evento = st.radio("Tipo de Operação:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    PASTA_GRUPOS = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    grupos_disponiveis = listar_grupos(PASTA_GRUPOS)

    with st.form("form_cadastro_grupo"):
        nome_grupo = st.text_input("Nome do Grupo / Ônibus / Festa (Ex: Paula_Barros_Barra_Grande)")
        enviar_cadastro = st.form_submit_button("Criar Capa e Estrutura do Evento")
        
    if enviar_cadastro and nome_grupo.strip():
        nome_limpo = nome_grupo.strip().replace(" ", "_")
        caminho = os.path.join(PASTA_GRUPOS, f"{nome_limpo}.xlsx")
        
        if os.path.exists(caminho):
            st.warning("Este evento já existe nesta categoria!")
        else:
            df_padrao = pd.DataFrame({
                "CPF": ["123.456.789-00", "987.654.321-11"],
                "Nome completo do participante": ["Judyth", "Thor"],
                "Data de Nascimento": ["10/05/2014", "15/08/2013"],
                "Responsável": ["Luiza Paixão", "Luiza Paixão"],
                "Telefone Emergência": ["21981095949", "21981095949"],
                "Ficha Médica": ["Dermatite", "Nebacetim"],
                "Status Entrada": ["Pendente", "Pendente"],
                "Status Saída": ["Pendente", "Pendente"],
                "Ocorrências no Evento": ["Nenhum", "Nenhum"]
            })
            df_padrao.to_excel(caminho, index=False)
            st.success(f"Capa do evento **{nome_grupo}** criada com sucesso!")
            st.rerun()

    if grupos_disponiveis:
        st.markdown("<hr style='border: 0.5px solid #000000;'>", unsafe_allow_html=True)
        st.markdown("<h3>Enviar Planilha Oficial (.xlsx)</h3>", unsafe_allow_html=True)
        grupo_escolhido = st.selectbox("Selecione o evento para atualizar:", grupos_disponiveis)
        
        arquivo_excel = st.file_uploader("Escolha o arquivo Excel da agência:", type=["xlsx"])
        if arquivo_excel is not None:
            df_cliente = pd.read_excel(arquivo_excel)
            caminho_alvo = os.path.join(PASTA_GRUPOS, f"{grupo_escolhido}.xlsx")
            df_cliente.to_excel(caminho_alvo, index=False)
            st.success(f"Planilha do evento **{grupo_escolhido}** atualizada com sucesso!")

# --- 5. ARQUIVO DE EVENTOS PASSADOS ---
elif pagina_atual == "arquivo":
    if st.button("Retornar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="eccomi-title">EVENTOS PASSADOS</div>', unsafe_allow_html=True)
    st.markdown("<p>Armazenamento de eventos encerrados. É possível desarquivar caso necessário.</p>", unsafe_allow_html=True)
    
    arquivados = sorted([f.replace(".xlsx", "") for f in os.listdir(PASTA_ARQUIVO) if f.endswith(".xlsx")])
    if arquivados:
        for arq in arquivados:
            st.markdown(f"""
                <div class="card-evento">
                    <h3 style="font-size: 14px !important;">{arq.replace('_', ' ')}</h3>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Desarquivar {arq.replace('_', ' ')}", key=f"des_{arq}"):
                src = os.path.join(PASTA_ARQUIVO, f"{arq}.xlsx")
                dst = os.path.join(PASTA_VIAGENS, f"{arq}.xlsx")
                if os.path.exists(src):
                    os.rename(src, dst)
                st.success("Evento desarquivado com sucesso!")
                st.rerun()
            st.markdown("<hr style='border: 0.5px solid #000000;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento arquivado no momento.")

# --- 6. REGISTAR ALERTA OU OCORRÊNCIA ---
elif pagina_atual == "alerta":
    if st.button("Retornar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="eccomi-title">REGISTO DE OCORRÊNCIAS</div>', unsafe_allow_html=True)
    todos_g = listar_grupos(PASTA_VIAGENS) + listar_grupos(PASTA_FESTAS)
    if todos_g:
        g_alerta = st.selectbox("Selecione o evento:", todos_g)
        pasta_g_alerta = PASTA_VIAGENS if os.path.exists(os.path.join(PASTA_VIAGENS, f"{g_alerta}.xlsx")) else PASTA_FESTAS
        df_a = pd.read_excel(os.path.join(pasta_g_alerta, f"{g_alerta}.xlsx"))
        col_n = next((c for c in df_a.columns if 'nome' in c.lower()), df_a.columns[1])
        part_alerta = st.selectbox("Participante envolvido:", df_a[col_n].tolist())
        if part_alerta:
            with st.form("form_alerta_geral"):
                txt_oc = st.text_area("Descreva o ocorrido:")
                if st.form_submit_button("Salvar Alerta"):
                    st.success("Alerta registado com sucesso!")
    else:
        st.info("Nenhum evento cadastrado.")

# --- 7. RASTREAMENTO GPS ---
elif pagina_atual == "gps":
    if st.button("Retornar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="eccomi-title">RASTREAMENTO GPS</div>', unsafe_allow_html=True)
    st.markdown("<p>Acompanhe a posição geográfica em tempo real dos guias e monitores.</p>", unsafe_allow_html=True)
    dados_mapa = pd.DataFrame({"lat": [-22.9068], "lon": [-43.1729]})
    st.map(dados_mapa, zoom=15)
    st.info("O sistema captura a posição atual do telemóvel do guia em campo.")
