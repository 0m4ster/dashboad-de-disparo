import streamlit as st
import pandas as pd
import os
from kolmeya_api import get_investimento_kolmeya
import locale
import datetime
import requests
from streamlit_autorefresh import st_autorefresh

CSV_PATH = 'dados_dashboard.csv'

# Dados iniciais
DADOS_INICIAIS = {
    "Canal": ["HIGIENIZAÇÃO", "RCS", "KOLMEYA", "WHATSAPP", "TRAFEGO PAGO", "URA"],
    "INVESTIMENTO": [""] * 6,
    "QUANT/LEADS": [""] * 6,
    "CUSTO/ENVIO": [""] * 6,
    "PRODUÇÃO": [""] * 6,
    "PREVISÃO/FATURAMENTO": [""] * 6,
    "FATURAMENTO POR ENVIO": [""] * 6,
    "FATURA": [""] * 6,
    "ROI": [""] * 6,
}

def carregar_df():
    """Carrega ou inicializa o DataFrame principal. Salva no session_state."""
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(DADOS_INICIAIS)
        df.to_csv(CSV_PATH, index=False)
    st.session_state.df = df
    return st.session_state.df

def salvar_df():
    """Salva o DataFrame no arquivo CSV."""
    st.session_state.df.to_csv(CSV_PATH, index=False)

def atualizar_valor_df(canal, coluna, valor):
    """Atualiza um valor específico no DataFrame e salva."""
    st.session_state.df.loc[st.session_state.df["Canal"] == canal, coluna] = valor
    salvar_df()

def calcular_investimento(df, canal, mensagens):
    """Calcula o investimento para um canal específico."""
    valor_envio = df.loc[df['Canal'].str.strip().str.upper() == canal, 'CUSTO/ENVIO'].values[0]
    try:
        valor_envio = float(str(valor_envio).replace(',', '.'))
    except ValueError:
        valor_envio = 0.0
    qtd_msgs = sum(
        1 for msg in mensagens
        if str(msg.get('api', '')).strip().upper() == canal
        or str(msg.get('broker', '')).strip().upper() == canal
    )
    return qtd_msgs, valor_envio, qtd_msgs * valor_envio

def renderizar_tabela(df):
    """Renderiza a tabela HTML estilizada com os dados do DataFrame."""
    df = df.fillna("")
    html = """
    <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse: collapse; font-size: 22px;">
      <tr style="background-color: black; color: white;">
        <th style='border: 2px solid #fff;'>Canal</th>
        <th style='border: 2px solid #fff;'>INVESTIMENTO</th>
        <th style='border: 2px solid #fff;'>QUANT/LEADS</th>
        <th style='border: 2px solid #fff;'>CUSTO/ENVIO</th>
        <th style='border: 2px solid #fff;'>PRODUÇÃO</th>
        <th style='border: 2px solid #fff;'>PREVISÃO/FATURAMENTO</th>
        <th style='border: 2px solid #fff;'>FATURAMENTO POR ENVIO</th>
        <th style='border: 2px solid #fff;'>FATURA</th>
        <th style='border: 2px solid #fff;'>ROI</th>
      </tr>
    """
    for i in range(len(df)):
        html += "<tr>"
        for col in df.columns:
            html += f"<td style='background-color: #f7d5f7; color: black; font-size: 26px; border: 2px solid #fff;'>{str(df.iloc[i][col])}</td>"
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)

def formatar_moeda_brasileira(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_producao_kolmeya(data_inicio, data_fim):
    try:
        df_prod = pd.read_csv('producao_kolmeya.csv')
        df_prod['data_venda'] = pd.to_datetime(df_prod['data_venda'])
        mask = (
            (df_prod['canal'].str.upper() == 'KOLMEYA') &
            (df_prod['status_venda'].str.lower() == 'vendido') &
            (df_prod['data_venda'] >= pd.to_datetime(data_inicio)) &
            (df_prod['data_venda'] <= pd.to_datetime(data_fim))
        )
        return df_prod[mask].shape[0]
    except Exception as e:
        st.warning(f"Erro ao calcular produção Kolmeya: {e}")
        return 0

# Configuração da página e estilos
st.set_page_config(page_title="DASHBOARD SERVCRED", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #FFFAFA !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #FFFAFA !important;
    }
    .titulo-dash {
        background: black;
        color: white;
        width: 105vw;
        margin-left: -8px;
        margin-right: 0;
        padding: 40px 0;
        font-size: 2.5em;
        text-align: center;
        font-weight: bold;
    }
    div.stButton > button {
        margin-top: 1.7em;
    }
    .stTextInput > div > div > input {
        width: 80px !important;
        min-width: 100px !important;
        max-width: 105px !important;
        border: 2px solid #ff0000 !important;
        border-radius: 6px !important;
        background-color: #26262c !important;
        color: #fff !important;
    }
    label {
        color: #000000 !important;
        font-weight: bold;
        font-size: 1em;
    }
    div[data-testid="stMetric"] > div > div > span {
        color: #000000 !important;
        font-weight: bold;
    }
    .stAlert > div {
        color: #000000 !important;
        font-weight: bold;
    }
    </style>
    <div class="titulo-dash">DASHBOARD SERVCRED</div>
""", unsafe_allow_html=True)

align_left_style = """
    <style>
    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        margin: 0rem !important;
        max-width: 105vw !important;
    }
    table {
        margin-left: 0 !important;
        margin-top: 0 !important;
    }
    </style>
"""
st.markdown(align_left_style, unsafe_allow_html=True)

# Carrega o DataFrame
df = carregar_df()

# Layout dos inputs
col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
with col1:
    canal_selecionado = st.selectbox('Escolha o canal', df['Canal'])
    user_input1 = st.text_input('valor por envio', key='comissao1')
with col2:
    btn1 = st.button('Enviar 1')
with col3:
    user_input2 = st.text_input('valor comissão', key='comissao2')
with col4:
    btn2 = st.button('Enviar 2')

# Período de consulta
hoje = datetime.date.today()
data_inicio = st.date_input("Data início", value=hoje, key="data_inicio")
data_fim = st.date_input("Data fim", value=hoje + datetime.timedelta(days=7), key="data_fim")

# Ajuste para evitar erro de data futura na API
agora = datetime.datetime.now()
if data_fim == hoje:
    hora_final = agora.strftime("%H:%M")
    data_fim_str = f"{data_fim} {hora_final}"
else:
    data_fim_str = f"{data_fim} 23:59"

# Consulta API
valor = None
erro_api = None
import logging
logging.basicConfig(filename='dashboard_servcred.log', level=logging.ERROR)

# Busca token da API de variável de ambiente
KOLMEYA_TOKEN = os.environ.get('KOLMEYA_TOKEN', '4YyZFPMQHW0LZeKiGAqe705cLPweuJKIWFtKAyuj')
try:
    valor = get_investimento_kolmeya(
        KOLMEYA_TOKEN,
        f"{data_inicio} 00:00",
        data_fim_str
    )
    if isinstance(valor, dict) and "valor" in valor:
        valor = valor["valor"]
except Exception as e:
    erro_api = str(e)
    logging.error(f"Erro ao consultar API Kolmeya: {erro_api}")

# Atualiza valor de CUSTO/ENVIO ao clicar no botão
if btn1 and user_input1:
    atualizar_valor_df(canal_selecionado, "CUSTO/ENVIO", user_input1)
    df = st.session_state.df
    st.success(f"Valor por envio atualizado para {canal_selecionado}!")

# Cálculo e atualização do investimento KOLMEYA
if isinstance(valor, list):
    qtd_msgs, valor_envio, valor_investido = calcular_investimento(df, "KOLMEYA", valor)
    atualizar_valor_df("KOLMEYA", "INVESTIMENTO", formatar_moeda_brasileira(valor_investido))
    st.write(f"Valor por envio KOLMEYA: {valor_envio}")
    st.metric(label="Total investido KOLMEYA", value=f"R$ {valor_investido:,.2f}")

# Buscar total de cliques Kolmeya via API
def obter_total_cliques_kolmeya():
    try:
        resp = requests.get('https://dashboad-de-disparo.onrender.com/cliques_kolmeya')
        if resp.status_code == 200:
            data = resp.json()
            total_unicos = data.get('total_cliques_unicos_ip_user', 0)
            total_geral = data.get('total_cliques', 0)
            return total_unicos, total_geral
    except Exception as e:
        st.warning(f"Erro ao buscar cliques Kolmeya: {e}")
    return 0, 0

# Atualiza QUANT/LEADS da KOLMEYA antes de renderizar a tabela
if st.button("Atualizar cliques Kolmeya"):
    cliques_unicos, cliques_geral = obter_total_cliques_kolmeya()
    atualizar_valor_df("KOLMEYA", "QUANT/LEADS", cliques_geral)
    df = carregar_df()
    st.success("Quantidade de cliques atualizada!")
else:
    cliques_unicos, cliques_geral = obter_total_cliques_kolmeya()
    atualizar_valor_df("KOLMEYA", "QUANT/LEADS", cliques_geral)
    df = carregar_df()

# Preenche QUANT/LEADS da linha KOLMEYA com o total de cliques geral
idx_kolmeya = df[df['Canal'].str.upper() == 'KOLMEYA'].index
if len(idx_kolmeya) > 0:
    df.at[idx_kolmeya[0], 'QUANT/LEADS'] = cliques_geral

# Calcula produção Kolmeya
producao_kolmeya = calcular_producao_kolmeya(data_inicio, data_fim)
if len(idx_kolmeya) > 0:
    df.at[idx_kolmeya[0], 'PRODUÇÃO'] = producao_kolmeya

# Renderiza a tabela
renderizar_tabela(df)

# Exibe ambos os valores de cliques
st.metric("Cliques únicos Kolmeya", cliques_unicos)
st.metric("Total de cliques Kolmeya", cliques_geral)

# Esconde menus do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Locale para moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    st.warning("Não foi possível definir o locale para pt_BR.UTF-8. Formatação de moeda pode não funcionar corretamente.")
    locale.setlocale(locale.LC_ALL, '')

st.subheader("Consulta de Investimento Kolmeya")

if erro_api:
    st.error(f"Erro ao consultar o financeiro: {erro_api}")
elif isinstance(valor, dict) and "erro" in valor:
    st.error(f"Erro ao consultar a API Kolmeya: {valor['erro']}")
elif isinstance(valor, dict) and "messages" in valor:
    qtd_msgs, valor_envio, valor_investido = calcular_investimento(df, "KOLMEYA", valor["messages"])
    atualizar_valor_df("KOLMEYA", "INVESTIMENTO", formatar_moeda_brasileira(valor_investido))
    df = carregar_df()  # Recarrega o DataFrame atualizado
    if "show_kolmeya_table" not in st.session_state:
        st.session_state["show_kolmeya_table"] = False
    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("\U0001F50D", key="blue_square_btn", help="Visualizar mensagens detalhadas"):
                st.session_state["show_kolmeya_table"] = not st.session_state["show_kolmeya_table"]
    if st.session_state["show_kolmeya_table"]:
        st.dataframe(pd.DataFrame(valor["messages"]))
else:
    st.info("Nenhum valor retornado para o período selecionado ou valor inesperado.")

# Adiciona auto-refresh a cada 30 segundos
st_autorefresh(interval=30 * 1000, key="datarefresh")

