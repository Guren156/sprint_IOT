# CLYVO VET — Assistente Inteligente (Sprint 4)

Componente de Inteligência Artificial do **CLYVO VET**, da disciplina **Disruptive Architectures: IoT, IoB & Generative IA**.

Na Sprint 3 definimos e documentamos a proposta. Nesta Sprint 4 o assistente está **implementado e funcionando**: uma API REST em Python (FastAPI) lê os dados reais do pet no **banco Oracle da FIAP**, monta o contexto (RAG) e consulta um **LLM** (Claude ou Gemini). Tem também uma tela web para o tutor e outra para a clínica.

## Integrantes

| Nome | RM |
|---|---|
| Ana Clara de Oliveira Nascimento | 561957 |
| Henrique Orellana Pereira | 565608 |
| Isis Macedo e Andrade | 561497 |
| Rafael Carvalho Meireles | 563413 |

## Links da entrega

- **Vídeo (YouTube, não listado):** _adicionar link aqui_
- **Vídeo da Sprint 3:** https://youtu.be/ZoQhvzi6FDc
- **Documentação técnica:** [`docs/documentacao-tecnica.md`](./docs/documentacao-tecnica.md)
- **Arquitetura:** [`docs/arquitetura.md`](./docs/arquitetura.md)
- **Testes e resultados:** [`docs/testes.md`](./docs/testes.md)

## Funcionalidades

| # | Funcionalidade | Como a IA atua |
|---|---|---|
| 1 | **Painel de saúde do pet** | Lê perfil e histórico no Oracle e calcula a situação das vacinas e dos check-ups |
| 2 | **Recomendações proativas** | Motor de regras gera alertas priorizados (vacina vencida ou vencendo, check-up atrasado, pet idoso, tratamento em andamento) |
| 3 | **Chat com o assistente** | LLM com RAG: responde dúvidas do tutor usando **só** os dados daquele pet |
| 4 | **Triagem de sintomas** | O LLM classifica a urgência (BAIXA/MÉDIA/ALTA) e as regras de segurança garantem que sinais graves nunca fiquem como baixa |
| 5 | **Personalização por comportamento** | Tutor com menos de 3 interações recebe explicações didáticas; o recorrente recebe respostas diretas |
| 6 | **Painel da clínica** | Triagens ordenadas por urgência e lista de pets com vacina vencida, para a clínica entrar em contato |
| 7 | **Auditoria** | Toda pergunta e resposta é gravada na tabela `T_CLY_INTERACAO_IA` |

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend / API REST | Python 3.10+ e FastAPI (documentação automática em `/docs`) |
| Banco de dados | Oracle FIAP (`oracledb`, modo thin, sem instalar o Oracle Client). Sem credenciais, usa SQLite local com os mesmos dados |
| IA generativa | Claude (Anthropic API) ou Gemini (Google AI Studio). Sem chave, roda em **modo simulado** |
| Frontend | HTML + CSS + JavaScript puro, servido pela própria API |
| Testes | pytest + TestClient do FastAPI (12 testes ponta a ponta) |

## Estrutura do repositório

```
├── app/
│   ├── main.py            <- rotas da API REST
│   ├── assistente.py      <- RAG: monta o contexto, chama o LLM, modo simulado, triagem
│   ├── recomendacoes.py   <- regras de vacinas, check-up, pet idoso e tratamentos
│   ├── triagem.py         <- palavras-chave de urgência (rede de segurança)
│   ├── db.py              <- acesso ao Oracle e ao SQLite
│   ├── config.py          <- lê o .env
│   └── static/index.html  <- telas do tutor e da clínica
├── sql/
│   ├── 01_oracle_ia.sql   <- cria T_CLY_INTERACAO_IA e o histórico recente no Oracle
│   └── 02_sqlite_demo.sql <- banco local de demonstração (mesmos dados)
├── tests/test_api.py      <- testes automatizados
├── docs/                  <- documentação técnica, arquitetura, testes e roteiro do vídeo
├── requirements.txt
└── .env.example           <- modelo de configuração (copie para .env)
```

## Como executar

**1. Instalar as dependências** (Python 3.10 ou superior):

```bash
pip install -r requirements.txt
```

**2. Configurar (opcional).** Copie `.env.example` para `.env` e preencha:
- `ORACLE_USER` / `ORACLE_PASSWORD`: usuário do Oracle da FIAP. Antes, rode no SQL Developer o script de Banco de Dados da Sprint 4 e depois [`sql/01_oracle_ia.sql`](./sql/01_oracle_ia.sql).
- `ANTHROPIC_API_KEY` **ou** `GEMINI_API_KEY`: chave do LLM. O Gemini tem cota gratuita em https://aistudio.google.com/apikey.

Sem o `.env`, o projeto roda do mesmo jeito, com o banco SQLite local e a IA em modo simulado.

**3. Subir a aplicação:**

```bash
python -m uvicorn app.main:app --port 8000
```

Abra **http://localhost:8000** para usar as telas ou **http://localhost:8000/docs** para testar a API (Swagger).

**4. Rodar os testes:**

```bash
python -m pytest -v
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/status` | Banco e provedor de IA em uso |
| GET | `/api/tutores` | Lista de tutores |
| GET | `/api/tutores/{id}/pets` | Pets do tutor |
| GET | `/api/pets/{id}` | Perfil, histórico, vacinas e recomendações |
| POST | `/api/chat` | `{"id_pet": 101, "pergunta": "..."}`: resposta do assistente |
| POST | `/api/triagem` | `{"id_pet": 101, "sintomas": "..."}`: nível de urgência e orientação |
| GET | `/api/pets/{id}/interacoes` | Últimas interações do pet com a IA |
| GET | `/api/clinica/alertas` | Painel da clínica |

## Resultados

| Item | Sprint 3 | Sprint 4 |
|---|---|---|
| Problema, abordagem de IA e dados | Documentado | Mantido |
| Arquitetura | Diagrama proposto | **Implementada** (API, Oracle, LLM e telas) |
| Assistente (chat com RAG) | Planejado | **Funcionando** |
| Triagem de urgência | Planejado | **Funcionando** (LLM + regras de segurança) |
| Recomendações proativas | Planejado | **Funcionando** |
| Painel da clínica | Planejado | **Funcionando** |
| Testes automatizados | — | **12 testes passando** |
