# Arquitetura de Integração — Assistente Inteligente CLYVO (Sprint 4)

Arquitetura **implementada**: o que estava proposto na Sprint 3 agora roda de verdade. Cada caixa do diagrama corresponde a um arquivo do repositório.

```mermaid
flowchart TB
    subgraph Personas
        T[Tutor do Pet]
        C[Equipe da Clínica]
    end

    subgraph Front["Frontend web - app/static/index.html"]
        UI[App do Tutor\nchat + triagem + recomendações]
        DASH[Painel da Clínica]
    end

    subgraph API["API REST FastAPI - app/main.py"]
        ROT[Rotas /api/...]
        RAG[Montador de contexto RAG\napp/assistente.py]
        REC[Motor de recomendações\napp/recomendacoes.py]
        TRI[Regras de segurança da triagem\napp/triagem.py]
        SIM[Modo simulado\nfallback sem LLM]
    end

    subgraph Dados["Banco Oracle FIAP - app/db.py"]
        DB[(T_CLY_PETS, T_CLY_RESPONSAVEL,\nT_CLY_CLINICA, T_CLY_HISTORICO_SAUDE)]
        LOGDB[(T_CLY_INTERACAO_IA)]
    end

    subgraph IA["Serviço de IA generativa"]
        LLM[[Claude - Anthropic API\nou Gemini - Google AI]]
    end

    T -->|1 pergunta / sintomas| UI
    UI -->|2 HTTP JSON| ROT
    ROT -->|3 SELECT do pet e histórico| DB
    DB -->|4 dados reais| REC
    REC -->|5 alertas priorizados| RAG
    RAG -->|6 prompt com contexto do pet| LLM
    LLM -->|7 resposta / nível de urgência| RAG
    RAG -. falha ou sem chave .-> SIM
    RAG -->|8 nível do LLM| TRI
    TRI -->|9 nível final = o mais alto| ROT
    ROT -->|10 INSERT da interação| LOGDB
    ROT -->|11 resposta| UI
    UI --> T
    LOGDB -->|12 triagens por urgência| DASH
    DB -->|vacinas vencidas| DASH
    DASH --> C
```

## Fluxo passo a passo

| Nº | Etapa | Onde no código |
|---|---|---|
| 1-2 | O tutor escolhe o pet e envia uma pergunta ou os sintomas. A tela faz `POST /api/chat` ou `POST /api/triagem` | `index.html`, `main.py` |
| 3-4 | **Retrieval:** a API busca no Oracle o perfil do pet, o tutor, a clínica e todo o histórico de saúde | `db.obter_pet`, `db.historico` |
| 5 | O motor de regras calcula a situação das vacinas, os check-ups atrasados, se o pet é idoso e os tratamentos em andamento | `recomendacoes.gerar` |
| 6 | **Augmented:** o contexto (dados + alertas + perfil do tutor) entra no prompt, com instruções para responder só com base nele | `assistente.montar_contexto` |
| 7 | **Generation:** o LLM gera a resposta em linguagem natural. Na triagem, devolve um JSON com nível, justificativa e orientação | `assistente.chamar_llm` |
| — | Se não houver chave ou a API falhar, o modo simulado responde com o mesmo contexto, e a aplicação não quebra | `assistente._resposta_simulada` |
| 8-9 | Na triagem, as palavras-chave de emergência funcionam como rede de segurança: vale o nível mais alto entre a regra e o LLM | `triagem.py` |
| 10 | A interação é gravada para auditoria e personalização | `db.salvar_interacao` |
| 11 | A resposta volta para a tela | `index.html` |
| 12 | O painel da clínica lista as triagens (ALTA primeiro) e os pets com vacina vencida | `assistente.alertas_clinica` |

## Modelo de dados usado pela IA

Reaproveita as tabelas do trabalho de Banco de Dados e acrescenta uma tabela nova:

```mermaid
erDiagram
    T_CLY_RESPONSAVEL ||--o{ T_CLY_PETS : possui
    T_CLY_CLINICA ||--o{ T_CLY_PETS : atende
    T_CLY_PETS ||--o{ T_CLY_HISTORICO_SAUDE : tem
    T_CLY_PETS ||--o{ T_CLY_INTERACAO_IA : gera
    T_CLY_RESPONSAVEL ||--o{ T_CLY_INTERACAO_IA : faz
    T_CLY_INTERACAO_IA {
        NUMBER id_interacao PK
        NUMBER T_CLY_PETS_id_pet FK
        NUMBER T_CLY_RESPONSAVEL_id_usuario FK
        VARCHAR2 tipo "CHAT ou TRIAGEM"
        VARCHAR2 pergunta
        VARCHAR2 resposta
        VARCHAR2 nivel_urgencia
        VARCHAR2 modo_ia "claude, gemini ou simulado"
        DATE dt_interacao
    }
```
