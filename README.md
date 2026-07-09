# ⚖️ Painel Estatístico da Justiça do Trabalho (JT)

Este repositório contém um dashboard interativo desenvolvido em **Streamlit** para visualização e análise de dados históricos da Justiça do Trabalho do Brasil. O projeto utiliza **uv** como gerenciador de pacotes e o formato **Parquet** como base de dados otimizada para garantir alta performance e carregamento instantâneo das informações.

---

## 📌 Visão Geral do Projeto

O objetivo deste projeto é fornecer uma ferramenta visual, moderna e intuitiva para explorar os principais indicadores do judiciário trabalhista, focando estritamente na **quantidade de processos judiciais**. A coluna `Quantidade` representa o volume absoluto de processos associados a cada categoria da coluna `Variavel` (não contendo valores financeiros ou monetários).

Os indicadores principais contemplam:
*   `Casos Novos` e `CN por Assunto` (fluxo de novos processos).
*   `Julgados` (processos que receberam decisão judicial).
*   `Iniciadas` (processos cujo trâmite foi iniciado).
*   `Encerradas` (processos arquivados ou finalizados).
*   Outras variáveis do fluxo processual como `Recebidos`, `Resíduo` e `Extintas`.

O dashboard adota um **visual premium com tons pastéis**, suportando **alternância dinâmica entre tema claro e tema escuro**, cards de métricas (KPIs) estilizados via HTML/CSS com micro-animações, e gráficos interativos gerados com **Plotly**.

---

## 📂 Estrutura do Repositório

*   [main.py](file:///home/eduardo/Projetos/Painel-JT-Gemini/main.py): Código fonte do dashboard interativo em Streamlit.
*   [limpeza_dados.ipynb](file:///home/eduardo/Projetos/Painel-JT-Gemini/limpeza_dados.ipynb): Jupyter Notebook detalhando as etapas de análise exploratória, limpeza e conversão do CSV original de 72MB para o arquivo Parquet de 2.5MB.
*   `data/`: Diretório contendo os conjuntos de dados:
    *   `Base de Dados JT Historico - CSV.csv`: Base bruta original (delimitada por `;`, codificação `latin1`).
    *   [Base_de_Dados_JT_Historico_Limpa.parquet](file:///home/eduardo/Projetos/Painel-JT-Gemini/data/Base_de_Dados_JT_Historico_Limpa.parquet): Base limpa e otimizada utilizada pelo dashboard.
*   [pyproject.toml](file:///home/eduardo/Projetos/Painel-JT-Gemini/pyproject.toml) & [uv.lock](file:///home/eduardo/Projetos/Painel-JT-Gemini/uv.lock): Arquivos de configuração de dependências do gerenciador `uv`.

---

## 🧹 Processo de Limpeza e Organização dos Dados

As etapas de ETL (Extração, Transformação e Carga) estão implementadas no notebook [limpeza_dados.ipynb](file:///home/eduardo/Projetos/Painel-JT-Gemini/limpeza_dados.ipynb) e compreendem:
1.  **Filtragem de Colunas**: Seleção estrita das colunas de interesse (`Variavel`, `Ano`, `Instancia`, `Regiao Judiciaria` e `Quantidade`).
2.  **Tratamento de Nulos**: 
    *   A instância **TST** (Tribunal Superior do Trabalho) não possui divisão regional física de TRT. Os valores nulos em `Regiao Judiciaria` para o TST foram devidamente preenchidos como `"TST (Nacional)"`.
    *   Linhas irrelevantes com valores nulos nos campos essenciais foram descartadas (19 linhas de 1 milhão).
3.  **Padronização de Strings**: Correção de erros ortográficos causados por codificação incorreta (ex: `Arrecada  o` → `Arrecadação`, `Res duo` → `Resíduo` e `Tempo M dio` → `Tempo Médio`).
4.  **Limpeza Numérica (Quantidade e Ano)**:
    *   Os valores de `Quantidade` vinham formatados com padrão de texto em português (pontos de milhar e vírgulas decimais). O pipeline removeu os pontos, trocou as vírgulas por pontos, tratou erros e converteu a coluna para tipo numérico inteiro, arredondando frações para manter a coerência das quantidades absolutas de processos.
    *   A coluna `Ano` foi convertida para tipo inteiro.
5.  **Otimização de Armazenamento**: Exportação para o formato binário colunar **Parquet**, que reduziu o tamanho do dataset de **71.9 MB (CSV)** para **2.49 MB (Parquet)**, representando uma **redução de 96.5% no tamanho do arquivo** e acelerando drasticamente o dashboard.

---

## 🛠️ Como Executar e Replicar o Projeto

Este projeto utiliza o **uv**, o gerenciador de pacotes e ambientes Python mais veloz do ecossistema moderno.

### Pré-requisitos
Certifique-se de possuir o Python instalado (versão `>= 3.13`) e o `uv`. Caso não tenha o `uv` instalado, execute:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Passo 1: Instalar as Dependências
Com o `uv` instalado, navegue até a pasta do projeto e crie o ambiente virtual sincronizando as dependências configuradas no `pyproject.toml`:
```bash
uv sync
```
Isso instalará automaticamente o Pandas, PyArrow, Streamlit, Plotly e Jupyter no ambiente `.venv`.

### Passo 2: Executar o Notebook de Limpeza (Opcional)
A base limpa em Parquet já está pré-gerada no diretório `data/`. Se desejar reprocessá-la a partir do CSV original, você pode abrir e rodar o Jupyter Notebook ou executá-lo diretamente via linha de comando com `nbconvert`:
```bash
uv run jupyter nbconvert --to notebook --execute --inplace limpeza_dados.ipynb
```

### Passo 3: Iniciar o Dashboard em Streamlit
Para inicializar o dashboard interativo localmente, execute o seguinte comando:
```bash
uv run streamlit run main.py
```
O Streamlit abrirá automaticamente o painel no seu navegador padrão (geralmente no endereço `http://localhost:8501`).

---

## 📊 Funcionalidades do Dashboard

*   **Métricas do Fluxo Processual (KPIs)**: Exibição dinâmica de 4 cards consolidados (`Casos Novos`, `Julgados`, `Iniciadas` e `Encerradas`) com cálculo automático de variação percentual (%) comparado ao período imediatamente anterior de mesma duração.
*   **Abas Interativas**:
    *   **Panorama Geral**: Gráficos de linhas e barras mostrando o fluxo processual anual e comparativo entre processos iniciados vs. encerrados e casos novos vs. julgados.
    *   **Análise Regional (TRTs)**: Ranking dinâmico e gráfico de barras horizontal ordenado para identificar quais regiões possuem o maior volume do indicador selecionado, com mapeamento dos estados (ex: `02ª Região (SP Capital)`).
    *   **Análise por Instância**: Visualização em formato de rosca e barras empilhadas para entender a distribuição da quantidade de processos entre Varas de 1ª Instância, Tribunais de 2ª Instância e TST.
    *   **Consulta de Dados**: Tabela interativa para pesquisas avançadas e exportação em formato CSV dos dados filtrados.
*   **Filtros Avançados (Barra Lateral)**:
    *   Seleção de período via slider (intervalo de anos).
    *   Filtros dinâmicos de instâncias e regiões judiciárias.
    *   Seleção do indicador principal.
    *   **Alternador de Tema**: Rápido alternador entre Tema Claro (Soft Pastel Cream) e Tema Escuro (Slate Premium Dark) com transição de layouts e cores de gráficos adaptadas.
