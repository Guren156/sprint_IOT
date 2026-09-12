# Arquitetura de Integração — Assistente Inteligente CLYVO

Diagrama mostrando a comunicação entre tutor, aplicação, banco de dados, backend e o componente de IA.

```mermaid
flowchart TB
    subgraph Personas
        T[Tutor do Pet]
        C[Equipe da Clínica]
    end

    subgraph App["CLYVO VET - App (Mobile / Web)"]
        UI[Chat do Assistente Inteligente]
        DASH[Painel da Clínica]
    end

    subgraph Backend["Backend CLYVO VET (API .NET / Java)"]
        API[API REST]
        CTX[Montador de Contexto]
        LOG[Registro de Interações]
    end

    subgraph Dados["Banco de Dados CLYVO VET"]
        DB[(Perfil, Histórico Clínico,\nVacinas, Medicamentos)]
        LOGDB[(interacao_ia)]
    end

    subgraph IA["Serviço de IA"]
        LLM[[LLM Generativo\ncom RAG]]
    end

    T -->|"1 - pergunta / sintomas"| UI
    UI -->|"2 - request HTTP"| API
    API -->|"3 - busca dados do pet"| DB
    DB -->|"4 - histórico + perfil"| CTX
    CTX -->|"5 - prompt contextualizado"| LLM
    LLM -->|"6 - resposta / nível de urgência"| API
    API -->|"7 - grava"| LOGDB
    API -->|"8 - resposta"| UI
    UI -->|"9 - exibe resposta / alerta"| T
    API -.->|"10 - alerta de urgência alta"| DASH
    DASH --> C
```

## Legenda do fluxo

| Nº | Etapa |
|---|---|
| 1 | Tutor envia pergunta ou descreve sintomas no chat do app |
| 2 | App chama a API do backend |
| 3-4 | Backend consulta o banco de dados relacional para obter perfil, histórico clínico, vacinas e medicamentos do pet |
| 5 | Backend monta o prompt com o contexto do pet + pergunta do tutor e envia ao serviço de IA |
| 6 | LLM retorna resposta em linguagem natural (ou classificação de urgência, no caso de triagem) |
| 7 | Interação é registrada para auditoria e melhoria contínua |
| 8-9 | Resposta é devolvida e exibida ao tutor no app |
| 10 | Em caso de urgência alta, um alerta é encaminhado ao painel da clínica |
