# Importação das bibliotecas necessárias
import streamlit as st
import requests
import pandas as pd

# --- Configuração da Página ---
# Define o título da página e um ícone para a aba do navegador.
st.set_page_config(page_title="Albion Online | Dashboard de Preços", layout="wide")


# --- Interface do Usuário (Barra Lateral) ---
# Agrupa todos os controles de entrada do usuário na barra lateral para uma interface mais limpa.
st.sidebar.header("Configurações de Monitoramento")

# 1. Seletor de Servidor
# Permite que o usuário escolha o servidor do jogo, o que determina a URL base da API.
servidor = st.sidebar.selectbox(
    "Selecione o Servidor:",
    ("Américas", "Europa", "Ásia"),
    help="Escolha o servidor do jogo para consultar os dados."
)

# 2. Seletor de Cidades
# Permite a seleção de múltiplas cidades para análise.
cidades_default = ['Caerleon', 'Bridgewatch', 'Fort Sterling', 'Lymhurst', 'Martlock', 'Thetford', 'Brecilien']
cidades_selecionadas = st.sidebar.multiselect(
    "Selecione as Cidades:",
    options=cidades_default,
    default=cidades_default,
    help="Escolha uma ou mais cidades para monitorar."
)

# 3. Seletor de Itens
# Fornece uma lista pré-definida de itens comuns para facilitar a seleção.
itens_default = ['T4_BAG', 'T5_BAG', 'T4_FIBER_LEVEL1@1', 'T5_PLANKS', 'T6_ORE', 'T4_ROCK_LEVEL1@1']
itens_selecionados = st.sidebar.multiselect(
    "Selecione os Itens:",
    options=itens_default,
    default=itens_default,
    help="Escolha um ou mais itens da lista."
)

# 4. Área de Texto para Itens Adicionais (Bônus)
# Permite que usuários avançados colem uma lista de IDs de itens personalizados.
itens_texto = st.sidebar.text_area(
    "Adicionar Itens (separados por vírgula):",
    help="Cole uma lista de IDs de itens separados por vírgula para análise."
)

# 5. Botão de Ação
# Inicia a consulta à API e o processamento dos dados quando clicado.
botao_monitorar = st.sidebar.button("Monitorar Preços")


# --- Lógica de Back-End (Funções de Dados) ---

# Dicionário para mapear a seleção do servidor para a URL correta da API.
MAPA_SERVIDORES = {
    "Américas": "https://west.albion-online-data.com",
    "Europa": "https://europe.albion-online-data.com",
    "Ásia": "https://east.albion-online-data.com"
}

@st.cache_data
def fetch_data(base_url, itens, cidades):
    """
    Busca dados históricos da API do Albion Online Data Project.

    Utiliza o cache do Streamlit para evitar chamadas repetidas à API com os mesmos parâmetros.
    """
    # Validação para evitar chamadas vazias à API.
    if not itens or not cidades:
        return []

    # Formata os parâmetros para a URL da API.
    itens_str = ",".join(itens)
    cidades_str = ",".join(cidades)

    # Constrói a URL final para a requisição.
    url = f"{base_url}/api/v2/stats/history/{itens_str}?locations={cidades_str}&time-scale=24"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lança um erro para códigos de status HTTP 4xx ou 5xx.
        return response.json()
    except requests.exceptions.RequestException as e:
        # Exibe uma mensagem de erro amigável na interface se a chamada falhar.
        st.error(f"Erro ao buscar dados da API: {e}")
        return None

def process_variation(api_data):
    """
    Processa os dados brutos da API para calcular a variação percentual do preço.
    """
    if not api_data:
        # Retorna um DataFrame vazio se não houver dados para processar.
        return pd.DataFrame(columns=['Item', 'Cidade', 'Preço Recente (Prata)', 'Variação %'])

    variations = []
    # Itera sobre cada registro (combinação de item/cidade) retornado pela API.
    for record in api_data:
        item_id = record.get('item_id')
        cidade = record.get('location')
        data = record.get('data', [])

        # Garante que há pelo menos dois pontos de dados para calcular a variação.
        if len(data) >= 2:
            preco_recente = data[-1].get('avg_price', 0)
            preco_anterior = data[-2].get('avg_price', 0)

            # Calcula a variação percentual, com tratamento para evitar divisão por zero.
            if preco_anterior > 0:
                variacao_pct = ((preco_recente - preco_anterior) / preco_anterior) * 100
                variacao_abs = preco_recente - preco_anterior
            else:
                variacao_pct = 0
                variacao_abs = 0

            variations.append({
                'Item': item_id,
                'Cidade': cidade,
                'Preço Recente (Prata)': int(preco_recente),
                'Variação %': round(variacao_pct, 2),
                'Variação Absoluta': int(variacao_abs)  # Adicionando a variação absoluta
            })

    # Retorna os dados processados como um DataFrame do Pandas.
    return pd.DataFrame(variations)

def create_comparison_table(df):
    """
    Cria uma tabela comparativa de preços entre cidades.
    """
    if df.empty:
        return pd.DataFrame()

    # Usa pivot_table para remodelar os dados
    comparison_df = df.pivot_table(
        index='Item',
        columns='Cidade',
        values='Preço Recente (Prata)',
        aggfunc='first' # Usa 'first' para evitar problemas com duplicatas se houver
    )
    return comparison_df

# --- Layout Principal do Dashboard ---
st.title("Dashboard de Variação de Preços - Albion Online")

# A lógica principal só é executada quando o botão "Monitorar Preços" é pressionado.
if botao_monitorar:
    # Combina e limpa a lista de itens da seleção múltipla e da área de texto.
    itens_adicionais = [item.strip() for item in itens_texto.split(',') if item.strip()]
    todos_os_itens = sorted(list(set(itens_selecionados + itens_adicionais)))

    # Validação das entradas do usuário.
    if not todos_os_itens:
        st.warning("Por favor, selecione ou adicione pelo menos um item.")
    elif not cidades_selecionadas:
        st.warning("Por favor, selecione pelo menos uma cidade.")
    else:
        # Exibe um spinner enquanto os dados estão sendo buscados e processados.
        with st.spinner("Buscando dados da API e processando..."):
            base_url = MAPA_SERVIDORES[servidor]
            dados_api = fetch_data(base_url, todos_os_itens, cidades_selecionadas)
            df_variacao = process_variation(dados_api)

            # Se o processamento retornar um DataFrame com dados, exibe os resultados.
            if not df_variacao.empty:
                st.success("Dados processados com sucesso!")

                # 1. Métricas de Destaque
                st.subheader("Métricas de Destaque")
                col1, col2, col3 = st.columns(3)

                maior_alta = df_variacao.loc[df_variacao['Variação %'].idxmax()]
                maior_queda = df_variacao.loc[df_variacao['Variação %'].idxmin()]

                col1.metric(
                    label=f"📈 Maior Alta: {maior_alta['Item']} ({maior_alta['Cidade']})",
                    value=f"{maior_alta['Variação %']:.2f}%",
                    delta=f"{maior_alta['Variação Absoluta']} Prata"
                )
                col2.metric(
                    label=f"📉 Maior Queda: {maior_queda['Item']} ({maior_queda['Cidade']})",
                    value=f"{maior_queda['Variação %']:.2f}%",
                    delta=f"{maior_queda['Variação Absoluta']} Prata"
                )
                col3.metric(
                    label="🔍 Itens Monitorados",
                    value=len(df_variacao),
                    help="Contagem total de combinações item/cidade analisadas."
                )

                # 2. Tabela de Dados Detalhada
                st.subheader("Variação Detalhada por Item")

                # Formatação condicional para colorir a coluna de variação.
                def colorir_variacao(val):
                    color = 'green' if val > 0 else 'red' if val < 0 else 'white'
                    return f'color: {color}'

                # Exibe o dataframe sem a coluna de variação absoluta
                st.dataframe(
                    df_variacao[['Item', 'Cidade', 'Preço Recente (Prata)', 'Variação %']]
                    .style.applymap(colorir_variacao, subset=['Variação %'])
                )

                # Tabela Comparativa de Preços
                st.subheader("Comparativo de Preços por Cidade")
                df_comparativo = create_comparison_table(df_variacao)

                if not df_comparativo.empty:
                    # Aplica um mapa de calor para destacar os preços mais baixos (verde) e mais altos (vermelho) por linha (item)
                    st.dataframe(
                        df_comparativo.style.background_gradient(cmap='RdYlGn_r', axis=1)
                        .format("{:,.0f}", na_rep="-")
                    )
                else:
                    st.warning("Não há dados suficientes para gerar a tabela comparativa.")


                # 3. Gráfico de Tendência Histórica
                st.subheader("Histórico de Preço")

                # Permite ao usuário selecionar um item/cidade da tabela para visualizar em um gráfico.
                opcoes_grafico = [f"{row['Item']} - {row['Cidade']}" for index, row in df_variacao.iterrows()]
                item_selecionado_grafico = st.selectbox("Selecione um Item/Cidade para ver o histórico:", options=opcoes_grafico)

                if item_selecionado_grafico:
                    item_id_selecionado, cidade_selecionada = item_selecionado_grafico.split(" - ")

                    # Filtra os dados da API para encontrar o histórico do item selecionado.
                    dados_historicos = next((item for item in dados_api if item['item_id'] == item_id_selecionado and item['location'] == cidade_selecionada), None)

                    if dados_historicos and dados_historicos['data']:
                        # Cria e exibe um gráfico de linha com o histórico de preços.
                        df_historico = pd.DataFrame(dados_historicos['data'])
                        df_historico['timestamp'] = pd.to_datetime(df_historico['timestamp'])
                        df_historico.set_index('timestamp', inplace=True)

                        st.line_chart(df_historico['avg_price'])
                    else:
                        st.warning("Não foi possível encontrar dados históricos para o item selecionado.")
            else:
                # Mensagem de erro se nenhum dado for retornado ou processado.
                st.error("Não foram encontrados dados suficientes para calcular a variação. Verifique os IDs dos itens ou tente outras cidades.")
