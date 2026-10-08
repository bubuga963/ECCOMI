import os
import json
import pandas as pd
import streamlit as st

# 1. CORREÇÃO DA BARRA LATERAL: 
# Usamos 'collapsed' nativo do Streamlit. Isso mantém o ícone de expandir/encolher de forma correta, 
# sem bugar a tela ou deixar textos fantasmas.
st.set_page_config(
    page_title="Eccomi",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# Estilização CSS: Preto e Branco, Nunito, tamanho mínimo 12px
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* Padronização de Títulos e Textos */
    .eccomi-title {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }
    h1 { font-size: 26px !important; font-weight: 700 !important; color: #000000 !important; }
    h2, h3 { font-size: 16px !important; font-weight: 700 !important; color: #000000 !important; }
    p, label, span, div, .stMarkdown {
        font-family: 'Nunito', sans-serif !important;
        color: #000000 !important;
        font-size: 12px !important;
    }

    /* Padronização Absoluta de Botões (Todos iguais, borda fina) */
    div.stButton > button:first-child, div[data-testid="stPopover"] > button:first-child {
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
    div.stButton > button:first-child:hover, div[data-testid="stPopover"] > button:first-child:hover {
        background-color: #F8F9FA !important;
    }

    /* Estilo dos Cards e Alertas */
    .alerta-medico {
        padding: 10px; background-color: #FFFFFF; border: 1px solid #000000;
        color: #000000; font-size: 12px; font-weight: bold; margin-top: 5px; margin-bottom: 15px;
    }
    .card-evento {
        padding: 15px; border: 1px solid #000000; border-radius: 4px;
        margin-bottom: 15px; background-color: #FFFFFF;
    }
    .card-aluno {
        padding: 12px; border: 1px solid #000000; border-radius: 4px;
        margin-bottom: 10px; background-color: #FFFFFF;
    }
    .info-box {
        padding: 12px; border: 1px solid #000000; border-radius: 4px;
        font-size: 12px; margin-bottom: 15px; background-color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# Pastas de dados
PASTA_VIAGENS = "bases_viagens"
PASTA_FESTAS = "bases_festas"
PASTA_INFO = "bases_info_eventos"
PASTA_ARQUIVO = "bases_arquivados"
for p in [PASTA_VIAGENS, PASTA_FESTAS, PASTA_INFO, PASTA_ARQUIVO]:
    if not os.path.exists(p): os.makedirs(p)

# Navegação e Estado da URL
query_params = st.query_params
evento_link = query_params.get("evento", None)
cat_link = query_params.get("cat", None)
pagina_atual = query_params.get("pagina", "home")

def listar_grupos(pasta):
    if os.path.exists(pasta):
        return sorted([f.replace(".xlsx", "") for f in os.listdir(pasta) if f.endswith(".xlsx")])
    return []

# --- MENU LATERAL NATIVO (Oculto por padrão, mas acessível pelo ícone) ---
with st.sidebar:
    st.markdown("### Navegação Rápida")
    if st.button("Página Inicial"):
        st.query_params["pagina"] = "home"
        if "evento" in st.query_params: del st.query_params["evento"]
        st.rerun()
    if st.button("Painel de Eventos"):
        st.query_params["pagina"] = "painel"
        if "evento" in st.query_params: del st.query_params["evento"]
        st.rerun()
    if st.button("Cadastrar Evento"):
        st.query_params["pagina"] = "cadastrar"
        if "evento" in st.query_params: del st.query_params["evento"]
        st.rerun()

# --- 1. ÁREA INTERNA DO EVENTO SELECIONADO ---
if evento_link:
    pasta_alvo = PASTA_VIAGENS if cat_link == "viagens" else PASTA_FESTAS
    caminho_arquivo = os.path.join(pasta_alvo, f"{evento_link}.xlsx")
    caminho_info = os.path.join(PASTA_INFO, f"{evento_link}_info.json")
    
    if os.path.exists(caminho_arquivo):
        # Botão de retorno padronizado
        if st.button("Voltar ao Painel Geral"):
            del st.query_params["evento"]
            st.query_params["pagina"] = "painel"
            st.rerun()

        st.markdown(f"<h1>Evento: {evento_link.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0.5px solid #000000;'>", unsafe_allow_html=True)
        
        info_data = {}
        if os.path.exists(caminho_info):
            with open(caminho_info, "r", encoding="utf-8") as f:
                info_data = json.load(f)

        aba_info, aba_chamada, aba_saida = st.tabs(["Logística", "Entrada", "Saída"])
        
        with aba_info:
            st.markdown("<h3>Detalhes do Evento</h3>", unsafe_allow_html=True)
            link_drive = info_data.get('drive_fotos', 'Não informado')
            link_html = f'<a href="{link_drive}" target="_blank">{link_drive}</a>' if link_drive.startswith('http') else link_drive
            
            st.markdown(f"""
                <div class="info-box">
                    <b>Local:</b> {info_data.get('local', 'Não informado')}<br>
                    <b>Telefone:</b> {info_data.get('tel_local', 'Não informado')}<br>
                    <b>Horário:</b> {info_data.get('horario', 'Não informado')}<br>
                    <b>Roteiro:</b> {info_data.get('roteiro', 'Não informado')}<br>
                    <b>Transporte:</b> {info_data.get('transporte', 'Não informado')} (Mot: {info_data.get('motorista', 'Não informado')})<br>
                    <b>Equipe:</b> {info_data.get('equipe', 'Não informado')}<br>
                    <b>Fotos/Drive:</b> {link_html}
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_info"):
                loc = st.text_input("Local:", value=info_data.get('local', ''))
                t_loc = st.text_input("Telefone do Local:", value=info_data.get('tel_local', ''))
                hor = st.text_input("Horário:", value=info_data.get('horario', ''))
                rot = st.text_area("Roteiro:", value=info_data.get('roteiro', ''))
                trans = st.text_input("Transporte:", value=info_data.get('transporte', ''))
                mot = st.text_input("Motorista:", value=info_data.get('motorista', ''))
                eqp = st.text_area("Equipe:", value=info_data.get('equipe', ''))
                drive = st.text_input("Link Fotos:", value=info_data.get('drive_fotos', ''))
                
                if st.form_submit_button("Salvar Informações"):
                    novo_dict = {"local": loc, "tel_local": t_loc, "horario": hor, "roteiro": rot, "transporte": trans, "motorista": mot, "equipe": eqp, "drive_fotos": drive}
                    with open(caminho_info, "w", encoding="utf-8") as f:
                        json.dump(novo_dict, f, ensure_ascii=False)
                    st.success("Salvo com sucesso!")
                    st.rerun()

        df = pd.read_excel(caminho_arquivo)
        col_id = df.columns[0]
        col_nome = df.columns[1]
        col_nasc = next((c for c in df.columns if 'nascimento' in c.lower() or 'data' in c.lower()), None)
        col_ficha = df.columns[5] if len(df.columns) > 5 else df.columns[-1]
        col_entrada = next((c for c in df.columns if 'entrada' in c.lower()), 'Status Entrada')
        col_saida = next((c for c in df.columns if 'saida' in c.lower() or 'saída' in c.lower()), 'Status Saida')
        
        if col_entrada not in df.columns: df[col_entrada] = "Pendente"
        if col_saida not in df.columns: df[col_saida] = "Pendente"

        with aba_chamada:
            termo = st.text_input("Pesquisar participante:", placeholder="Nome, CPF ou ID...", key="busca_ent")
            df_filtrado = df[df[col_nome].astype(str).str.contains(termo, case=False, na=False) | df[col_id].astype(str).str.contains(termo, case=False, na=False)] if termo else df
            
            st.markdown(f"<p><b>Entrada:</b> {len(df[df[col_entrada] == 'Presente'])} de {len(df)} presentes</p>", unsafe_allow_html=True)
            
            with st.form("form_ent"):
                novos_status = {}
                for i, row in df_filtrado.iterrows():
                    ficha = row[col_ficha] if pd.notna(row[col_ficha]) and str(row[col_ficha]).lower() not in ["", "nao ha.", "nenhum"] else None
                    st.markdown(f"""<div class="card-aluno"><b>{row[col_id]} - {row[col_nome]}</b></div>""", unsafe_allow_html=True)
                    s_atual = str(row[col_entrada]) if pd.notna(row[col_entrada]) else "Pendente"
                    novos_status[i] = st.radio(f"Status {row[col_nome]}:", ["Pendente", "Presente", "Faltou"], index=["Pendente", "Presente", "Faltou"].index(s_atual) if s_atual in ["Pendente", "Presente", "Faltou"] else 0, key=f"ent_{i}", horizontal=True)
                    if ficha: st.markdown(f"""<div class="alerta-medico">ALERTA MÉDICO: {ficha}</div>""", unsafe_allow_html=True)
                    st.markdown("<hr style='border: 0.5px solid #CCCCCC;'>", unsafe_allow_html=True)

                if st.form_submit_button("Salvar Chamada"):
                    for idx, val in novos_status.items(): df.at[idx, col_entrada] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Salvo!")
                    st.rerun()

        with aba_saida:
            with st.form("form_sai"):
                novos_status_s = {}
                for i, row in df.iterrows():
                    st.markdown(f"""<div class="card-aluno"><b>{row[col_id]} - {row[col_nome]}</b></div>""", unsafe_allow_html=True)
                    s_atual_s = str(row[col_saida]) if pd.notna(row[col_saida]) else "Pendente"
                    novos_status_s[i] = st.radio(f"Saída {row[col_nome]}:", ["Pendente", "Entregue", "Atenção"], index=["Pendente", "Entregue", "Atenção"].index(s_atual_s) if s_atual_s in ["Pendente", "Entregue", "Atenção"] else 0, key=f"sai_{i}", horizontal=True)
                    st.markdown("<hr style='border: 0.5px solid #CCCCCC;'>", unsafe_allow_html=True)

                if st.form_submit_button("Salvar Saída"):
                    for idx, val in novos_status_s.items(): df.at[idx, col_saida] = val
                    df.to_excel(caminho_arquivo, index=False)
                    st.success("Salvo!")
                    st.rerun()

# --- 2. PÁGINA INICIAL REAL (Separada do Painel) ---
elif pagina_atual == "home":
    st.markdown('<div class="eccomi-title">ECCOMI</div>', unsafe_allow_html=True)
    st.markdown("<p><b>Sistema B2B de Gestão e Segurança para Eventos, Excursões e Escolas.</b></p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 0.5px solid #000000; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <b>Bem-vindo ao Eccomi</b><br>
            Plataforma cirúrgica desenhada para eliminar planilhas de papel em campo. Proporciona chamadas rápidas, controlo de embarque/desembarque e exibe alertas médicos de segurança (como alergias e medicações) de forma instantânea para os monitores.<br><br>
            <i>Utilize o menu abaixo ou o ícone no topo esquerdo para navegar.</i>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ir para Painel de Eventos"):
            st.query_params["pagina"] = "painel"
            st.rerun()
        if st.button("Arquivo de Passados"):
            st.query_params["pagina"] = "arquivo"
            st.rerun()
    with col2:
        if st.button("Cadastrar Novo Evento"):
            st.query_params["pagina"] = "cadastrar"
            st.rerun()
        if st.button("Ocorrências e GPS"):
            st.query_params["pagina"] = "outros"
            st.rerun()

# --- 3. PAINEL GERAL DE EVENTOS ---
elif pagina_atual == "painel":
    if st.button("Voltar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
        
    st.markdown('<div class="eccomi-title">PAINEL DE EVENTOS</div>', unsafe_allow_html=True)
    categoria_evento = st.radio("Categoria:", ["Viagens e Excursões", "Festas e Eventos"], horizontal=True)
    
    PASTA_GRUPOS = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
    cat_url_param = "viagens" if categoria_evento == "Viagens e Excursões" else "festas"
    grupos_disponiveis = listar_grupos(PASTA_GRUPOS)
    
    termo_busca = st.text_input("Buscar evento por nome:", "")
    
    if grupos_disponiveis:
        eventos_filtrados = [g for g in grupos_disponiveis if termo_busca.lower() in g.lower()] if termo_busca else grupos_disponiveis
        
        for g in eventos_filtrados:
            caminho_g = os.path.join(PASTA_GRUPOS, f"{g}.xlsx")
            caminho_inf_g = os.path.join(PASTA_INFO, f"{g}_info.json")
            
            total_p, confirmados_p, faltou_p = 0, 0, 0
            local_g, horario_g = "Não informado", "Não informado"
            
            if os.path.exists(caminho_g):
                try:
                    df_g = pd.read_excel(caminho_g)
                    total_p = len(df_g)
                    c_ent = next((c for c in df_g.columns if 'entrada' in c.lower()), None)
                    if c_ent and c_ent in df_g.columns:
                        confirmados_p = len(df_g[df_g[c_ent] == "Presente"])
                        faltou_p = len(df_g[df_g[c_ent] == "Faltou"])
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
                    <p><b>Local:</b> {local_g} | <b>Horário:</b> {horario_g}</p>
                    <p><b>Total:</b> {total_p} | <b>Presentes:</b> {confirmados_p} | <b>Faltas:</b> {faltou_p}</p>
                    <div class="info-box">http://localhost:8501/?evento={g}&cat={cat_url_param}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # CORREÇÃO DEFINITIVA DOS 4 BOTÕES ALINHADOS
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                if st.button("Abrir Evento", key=f"btn_{g}"):
                    st.query_params["evento"] = g
                    st.query_params["cat"] = cat_url_param
                    st.rerun()
            with col_b2:
                # SOLUÇÃO DO UPLOAD: Usa um Popover. Ele renderiza como um botão comum idêntico aos outros.
                with st.popover("Atualizar Planilha"):
                    novo_excel = st.file_uploader("Suba a planilha .xlsx atualizada:", type=["xlsx"], key=f"up_{g}")
                    if novo_excel is not None:
                        df_novo = pd.read_excel(novo_excel)
                        df_novo.to_excel(caminho_g, index=False)
                        st.success("Planilha atualizada!")
            with col_b3:
                if st.button("Arquivar", key=f"arq_{g}"):
                    os.rename(caminho_g, os.path.join(PASTA_ARQUIVO, f"{g}.xlsx"))
                    st.rerun()
            with col_b4:
                if st.button("Excluir", key=f"del_{g}"):
                    os.remove(caminho_g)
                    if os.path.exists(caminho_inf_g): os.remove(caminho_inf_g)
                    st.rerun()
            st.markdown("<hr style='border: 0.5px solid #000000; margin-top: 15px;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum evento.")

# --- OUTRAS PÁGINAS (Cadastrar, Arquivo, Ocorrências) ---
elif pagina_atual in ["cadastrar", "arquivo", "outros"]:
    if st.button("Voltar à Página Inicial"):
        st.query_params["pagina"] = "home"
        st.rerun()
        
    if pagina_atual == "cadastrar":
        st.markdown('<h3>CADASTRAR NOVO EVENTO</h3>', unsafe_allow_html=True)
        categoria_evento = st.radio("Categoria:", ["Viagens e Excursões", "Festas e Eventos"])
        PASTA = PASTA_VIAGENS if categoria_evento == "Viagens e Excursões" else PASTA_FESTAS
        
        with st.form("form_cad"):
            nome_grupo = st.text_input("Nome do Evento:")
            if st.form_submit_button("Criar Estrutura Vazia") and nome_grupo.strip():
                caminho = os.path.join(PASTA, f"{nome_grupo.strip().replace(' ', '_')}.xlsx")
                pd.DataFrame({"CPF": ["000"], "Nome": ["Exemplo"], "Ficha Médica": ["Nenhum"]}).to_excel(caminho, index=False)
                st.success("Criado!")
                st.rerun()
                
        grupos = listar_grupos(PASTA)
        if grupos:
            st.markdown("<h3>Ou envie uma Planilha Base</h3>", unsafe_allow_html=True)
            g_escolhido = st.selectbox("Selecione o evento para anexar planilha:", grupos)
            arq = st.file_uploader("Upload Excel", type=["xlsx"])
            if arq:
                pd.read_excel(arq).to_excel(os.path.join(PASTA, f"{g_escolhido}.xlsx"), index=False)
                st.success("Atualizado!")
                
    elif pagina_atual == "arquivo":
        st.markdown('<h3>ARQUIVO</h3>', unsafe_allow_html=True)
        arquivados = listar_grupos(PASTA_ARQUIVO)
        for arq in arquivados:
            st.markdown(f'<div class="card-evento">{arq.replace("_", " ")}</div>', unsafe_allow_html=True)
            if st.button(f"Desarquivar {arq}"):
                os.rename(os.path.join(PASTA_ARQUIVO, f"{arq}.xlsx"), os.path.join(PASTA_VIAGENS, f"{arq}.xlsx"))
                st.rerun()
