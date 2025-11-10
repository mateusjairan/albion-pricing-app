# Dashboard de Variação de Preços do Albion Online

Uma aplicação web interativa construída com Streamlit para monitorar a variação diária de preços de itens no jogo Albion Online.

## Funcionalidades

- **Seleção de Servidor**: Escolha entre os servidores de Américas, Europa e Ásia.
- **Seleção de Cidades**: Monitore preços nas principais cidades do jogo, incluindo cidades do portal e Caerleon.
- **Seleção de Itens**: Acompanhe itens de uma lista pré-definida ou adicione seus próprios itens através de uma lista de IDs.
- **Métricas de Destaque**: Visualize rapidamente o item com a maior alta e a maior queda de preço.
- **Tabela Detalhada**: Analise uma tabela completa com os preços recentes e a variação percentual de cada item/cidade.
- **Gráfico Histórico**: Selecione um item específico para visualizar a tendência de seu preço ao longo do tempo.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Streamlit**: Framework para a construção da interface web.
- **Pandas**: Para manipulação e análise dos dados.
- **Requests**: Para realizar as chamadas à API do Albion Online Data Project.

## Instalação e Execução

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_DIRETORIO>
    ```

2.  **Instale as dependências:**
    Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```
    Instale as bibliotecas necessárias:
    ```bash
    pip install streamlit requests pandas
    ```

3.  **Execute a aplicação:**
    ```bash
    streamlit run app.py
    ```

4.  Abra seu navegador e acesse a URL fornecida pelo Streamlit (geralmente `http://localhost:8501`).

---

Desenvolvido para auxiliar jogadores a tomar decisões informadas sobre o mercado do Albion Online.
