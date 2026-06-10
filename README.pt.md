<div style="text-align: right;">
  <a href="README.md">English</a> | <a href="README.pt.md">Português</a>
</div>

# CollectBot - Pipeline de Coleta e Processamento de Dados com IA

CollectBot é um sistema inteligente de coleta e processamento de dados alimentado por agentes de IA. Ele automatiza o processo de extração, qualificação e formatação de dados estruturados a partir de fontes CSV usando uma arquitetura multi-agente construída na API Google Gemini.

## Visão Geral da Arquitetura do Sistema

CollectBot emprega uma **arquitetura de pipeline distribuído multi-agente** onde agentes de IA especializados trabalham juntos em um fluxo de trabalho coordenado para transformar dados brutos em saídas refinadas, filtradas e formatadas.

```
┌─────────────────────────────────────────────────────────────────┐
│                 INTERFACE WEB STREAMLIT                          │
│  (Upload CSV → Definir Critérios → Iniciar Pipeline → Baixar)  │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   ORQUESTRADOR (Sincr)   │
                    │  Coordena 3-4 Agentes    │
                    └──────────┬───────────────┘
                               │
        ┌──────────────────────┼──────────────────────┬──────────────┐
        ▼                      ▼                      ▼              ▼
    ┌────────────┐         ┌──────────┐         ┌──────────┐   ┌──────────┐
    │ AGENTE DE  │         │ AGENTE   │         │ AGENTE   │   │CONVERSOR │
    │ COLETA     │────────►│ DE       │────────►│ DE       │──►│(JSON→CSV)│
    │(Extração)  │         │QUALIF.   │         │FORMAT.   │   │(Sistema) │
    └────────────┘         └──────────┘         └──────────┘   └──────────┘
        │                       │                    │              │
        └───────────────────────┴────────────────────┴──────────────┘
                                 │
                    ┌────────────────────────────┐
                    │   API GEMINI 2.5 FLASH     │
                    │ (Processamento LLM Remoto) │
                    └────────────────────────────┘
```

## Componentes da Arquitetura

### 1. **Camada Frontend** (`src/app.py`)
- **Framework**: Streamlit
- **Responsabilidade**: Interação do usuário e visualização
- **Principais Recursos**:
  - Upload de arquivo CSV com visualização
  - Painel de configuração com três campos:
    1. **Tarefa de Coleta**: Definir quais dados extrair
    2. **Critérios de Qualificação**: Definir regras de filtragem
    3. **Sugestões de Formatação**: Formatação de saída opcional
  - Feedback de execução do pipeline em tempo real
  - Saída CSV formatada disponível para download

### 2. **Camada de Orquestração** (`src/agents/agents.py`)
Implementa três classes de agentes especializados:

#### **Agente Coletor**
- **Função**: Extrai dados brutos relevantes do arquivo CSV de origem
- **Entrada**: Descrição da tarefa do usuário + caminho do arquivo CSV
- **Processo**:
  - Carrega CSV na API de Arquivos Gemini
  - Envia tarefa de extração ao Gemini com contexto do arquivo
  - Retorna linhas de dados brutos e não filtrados
- **Saída**: String de dados brutos

#### **Agente Qualificador**
- **Função**: Filtra e pontua dados em relação aos critérios definidos pelo usuário
- **Entrada**: Dados brutos + critérios de qualificação
- **Processo**:
  - Analisa cada registro em relação às regras de critérios
  - Atribui pontuações de relevância quando aplicável
  - Estrutura saída como array JSON (forçado via `response_mime_type`)
- **Saída**: Array JSON válido de registros qualificados

#### **Agente Formatador** (Opcional)
- **Função**: Aplica transformações estilísticas à estrutura de dados
- **Entrada**: JSON qualificado + sugestões de formatação
- **Processo**:
  - Renomeia colunas conforme solicitado pelo usuário
  - Modifica valores de campos (ex: adicionando unidades)
  - Transforma formatação de texto
- **Saída**: Array JSON reformatado
- **Status**: Ignorado se nenhuma sugestão for fornecida

#### **Classe Orquestrador**
- **Função**: Coordena a execução sequencial de todos os agentes
- **Modelo de Execução**: Padrão async/await para I/O não bloqueante
- **Fluxo do Pipeline**:
  1. Coletor extrai dados
  2. Qualificador filtra resultados
  3. Formatador refina saída (se ativado)
  4. Sistema converte JSON final para CSV
- **Saída**: String CSV final pronta para download

### 3. **Camada de Modelo IA** (`src/agents/ai_model.py`)
- **Provedor LLM**: Google Gemini 2.5 Flash
- **Método de Integração**: SDK Python `genai` do Google
- **Principais Funções**:

| Função | Propósito | Entrada | Saída |
|--------|-----------|---------|-------|
| `upload_csv()` | Carrega CSV na API de Arquivos Gemini | Caminho do arquivo | Objeto de arquivo |
| `collector_fetch_from_file()` | Extrai dados usando arquivo carregado | Tarefa, objeto de arquivo | String de dados brutos |
| `qualifier_analyze()` | Filtra dados com imposição de esquema JSON | Dados brutos, critérios | Array JSON |
| `formatter_interpret()` | Aplica formatação ao JSON | JSON, sugestões | JSON refinado |
| `json_to_csv_dynamic()` | Converte JSON para formato CSV | String JSON | String CSV |
| `call_gemini()` | Wrapper genérico de API | Prompt, instrução de sistema | Texto de resposta |

### 4. **Pipeline de Dados**
- **Formato de Entrada**: Arquivos CSV (carregados via Streamlit)
- **Fluxo de Processamento**:
  ```
  Arquivo CSV → [Carregar no Gemini] → Extração de Dados Brutos
  → Filtragem por Critérios (JSON) → Formatação Opcional
  → Conversão para CSV → Download
  ```
- **Formato de Saída**: Arquivo CSV com registros qualificados e formatados

## Pilha de Tecnologia

| Componente | Tecnologia | Versão |
|-----------|-----------|---------|
| **Interface Web** | Streamlit | Mais recente |
| **Backend LLM** | Google Gemini 2.5 Flash | API |
| **Runtime Python** | Python | 3.8+ |
| **Cliente API** | google-genai | Mais recente |
| **Processamento de Dados** | Pandas | Mais recente |
| **Configuração de Ambiente** | python-dotenv | Mais recente |
| **Runtime Async** | asyncio | Built-in |

## Diagrama de Fluxo de Execução

```
Ação do Usuário           Resposta do Sistema
──────────────────────────────────────────────
    │
    ├─► Carregar CSV ───────────────► Streamlit salva arquivo temporário
    │
    ├─► Definir Tarefa & Critérios ► Configuração armazenada no estado UI
    │
    ├─► Clicar "Executar Pipeline" ► Orchestrator.run_pipeline() inicia
    │                                  ├─► Coletor carrega CSV no Gemini
    │                                  ├─► Coletor extrai linhas relevantes
    │                                  ├─► Qualificador filtra com critérios
    │                                  ├─► Qualificador retorna array JSON
    │                                  ├─► Formatador (se ativado) refina JSON
    │                                  └─► Sistema converte JSON para CSV
    │
    └─► Baixar Resultados ──────────► Usuário recebe arquivo CSV estruturado
```

## Padrões de Design Chave

1. **Processamento Assincronizado**: Utiliza `asyncio` para evitar bloqueios durante chamadas de API Gemini com I/O intensivo
2. **Abstração de Agentes**: Cada agente encapsula uma única responsabilidade (SRP)
3. **Imposição de Esquema JSON**: API Gemini `response_mime_type` garante saída JSON estruturada
4. **Integração com API de Arquivos**: Aproveita a API de Arquivos Gemini para manipulação eficiente de CSV
5. **Interface com Estado**: Estado de sessão Streamlit persiste orquestrador entre reexecuções
6. **Degradação Graciosa**: Formatador pula silenciosamente se nenhuma sugestão for fornecida

## Exemplo de Transformação de Dados

```
CSV de Entrada:
país,energia_renovável_%,status
Noruega,98.5,ativa
Alemanha,46.2,ativa
Índia,12.1,em desenvolvimento

(Tarefa do Usuário: "Encontrar países mudando para opções com baixas emissões de carbono")
(Critérios do Usuário: "Energia renovável > 20% OU aumentos notáveis")

↓ [Coletor extrai] ↓ [Qualificador filtra] ↓

JSON de Saída:
[
  {"país": "Noruega", "energia_renovável_%": 98.5, "status": "ativa", "relevância": "alta"},
  {"país": "Alemanha", "energia_renovável_%": 46.2, "status": "ativa", "relevância": "alta"}
]

↓ [Converter para CSV] ↓

CSV de Saída:
país,energia_renovável_%,status,relevância
Noruega,98.5,ativa,alta
Alemanha,46.2,ativa,alta
```

## Configuração de Ambiente

O sistema requer uma chave API do Gemini armazenada em `.env`:
```
GEMINI_API_KEY=sua_chave_api_aqui
```

## Melhorias Futuras

- Processamento em lote de múltiplos arquivos
- Registro customizável de tipo de agente
- Algoritmos avançados de pontuação
- Camada de cache para critérios repetidos
- Opções de formato de exportação (JSON, Excel, Parquet)
- Análise de desempenho de agentes
