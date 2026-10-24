# Documentação Técnica — Componente de Inteligência Artificial

**Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA
**Projeto:** CLYVO VET
**Sprint:** 4 — Implementação funcional do componente de IA (evolução da Sprint 3)
**Grupo:** Ana Clara de Oliveira Nascimento (RM 561957), Henrique Orellana Pereira (RM 565608), Isis Macedo e Andrade (RM 561497), Rafael Carvalho Meireles (RM 563413)

---

## 1. Contexto e Problema de Negócio

O CLYVO VET é a plataforma (app + backend + banco de dados) que a equipe vem construindo ao longo do semestre para apoiar tutores e clínicas veterinárias na gestão da saúde de pets: cadastro de animais, histórico clínico, vacinas, consultas e medicamentos.

Na prática, tutores acompanham a saúde do pet de forma fragmentada: lembram de vacinas por conta própria, não sabem interpretar sintomas antes de procurar a clínica, e não recebem recomendações personalizadas com base no histórico real do animal. Do lado da clínica, a equipe gasta tempo respondendo perguntas repetitivas de tutores (cuidados básicos, dúvidas sobre pós-consulta, dúvidas sobre calendário vacinal) que poderiam ser resolvidas com contexto automatizado.

**Problema central que a IA vai resolver:** falta de acompanhamento contínuo e personalizado da jornada de saúde do pet, tanto para o tutor (que não tem orientação proativa) quanto para a clínica (que não prioriza atendimentos com base em urgência real).

## 2. Objetivo do Componente de IA

Implementar um **Assistente Inteligente CLYVO** que:

1. Responde, em linguagem natural, dúvidas do tutor sobre o pet, usando como contexto o histórico clínico real armazenado no banco de dados da aplicação (perfil, vacinas, consultas, medicamentos).
2. Gera recomendações proativas e personalizadas (ex.: "a vacina antirrábica da Luna vence em 5 dias", "com base na idade e raça do Thor, recomenda-se check-up semestral").
3. Realiza uma **triagem textual**: o tutor descreve os sintomas em texto livre e o assistente classifica a urgência (baixa/média/alta) para ajudar a clínica a priorizar o atendimento.

## 3. Abordagem de IA Escolhida e Justificativa

**Abordagem escolhida: IA Generativa (LLM) com Retrieval-Augmented Generation — RAG.**

Comparação com as demais abordagens possíveis:

| Abordagem | Por que não foi a escolhida como principal |
|---|---|
| Modelo preditivo (classificação/regressão) | Exigiria uma base histórica rotulada e volumosa (ex.: milhares de casos de diagnóstico) que o projeto não possui nesta fase; também não responde perguntas abertas do tutor. |
| Motor de regras fixas | Não escala bem para linguagem natural livre (o tutor não digita em formato estruturado) e exigiria reescrever regras a cada novo cenário. |
| Sistema de recomendação clássico (filtragem colaborativa) | Depende de grande volume de interações entre múltiplos usuários; a base de tutores/pets do CLYVO VET ainda é pequena, o que gera "cold start". |
| **IA Generativa + RAG (escolhida)** | Lida naturalmente com perguntas livres em português, se adapta a qualquer pet sem re-treinamento, e permite **fundamentar a resposta nos dados reais do pet** (RAG) em vez de "alucinar" informação genérica — que é o principal risco de um LLM puro em contexto de saúde animal. |

**Como o RAG mitiga o principal risco (alucinação em saúde):** ao invés de perguntar diretamente ao LLM "o que fazer para o pet X", o backend primeiro recupera os dados estruturados do pet (histórico, vacinas, consultas) do banco de dados e injeta esse contexto no prompt enviado ao modelo. O LLM é instruído a responder **apenas com base no contexto fornecido** e a recomendar contato com a clínica sempre que a pergunta fugir do escopo de informação disponível.

## 4. Dados Necessários

Na Sprint 4 os dados vêm das tabelas reais do banco Oracle do projeto (trabalho de Banco de Dados), e foi criada uma tabela nova para as interações com a IA.

| Dado | Tabela (Oracle) | Estrutura | Uso pela IA |
|---|---|---|---|
| Perfil do pet | `T_CLY_PETS` | espécie, raça, data de nascimento (idade), peso | Personalização: cuidados por idade, espécie e raça; pet idoso tem check-up semestral |
| Tutor | `T_CLY_RESPONSAVEL` | nome, telefone | Tom da resposta, contato no painel da clínica |
| Clínica | `T_CLY_CLINICA` | nome, telefone | Orientação de contato em caso de urgência |
| Histórico clínico | `T_CLY_HISTORICO_SAUDE` (tipo `Consulta`, `Exame`, `Cirurgia`) | data, tipo, detalhes | Contexto das respostas e cálculo do check-up atrasado |
| Vacinas | `T_CLY_HISTORICO_SAUDE` (tipo `Vacinacao`) | vacina, data da dose | Alerta de reforço anual (vencida ou vencendo em até 30 dias) |
| Medicamentos | `T_CLY_HISTORICO_SAUDE` (tipo `Medicacao`) | medicamento, posologia, data | Tratamento em andamento: o assistente não sugere nada que conflite e orienta seguir a prescrição |
| Mensagem do tutor | entrada em tempo real (API) | texto livre, até 500 caracteres | Pergunta do chat ou relato de sintomas da triagem |
| Interações com a IA | `T_CLY_INTERACAO_IA` (**nova**) | tipo, pergunta, resposta, nível de urgência, modo da IA, data | Auditoria, painel da clínica e personalização por comportamento |

## 5. Estratégia de Personalização

A personalização ocorre em duas camadas:

1. **Personalização por dados estruturados:** cada resposta é gerada com o contexto específico daquele pet (idade, raça, histórico) — nunca uma resposta genérica igual para todos os animais.
2. **Personalização por comportamento:** o histórico de interações (`interacao_ia`) permite ajustar o tom e o nível de detalhe das respostas com base em quão frequentemente aquele tutor já interagiu com o assistente (tutor iniciante recebe explicações mais didáticas; tutor recorrente recebe respostas mais diretas). Implementado: com menos de 3 interações registradas o tutor é "iniciante"; a partir de 3, "recorrente". O perfil entra no prompt do LLM.

## 6. Fluxo de Dados (Ponta a Ponta)

1. Tutor abre o app CLYVO VET e escreve uma pergunta ou descreve um sintoma no chat do Assistente Inteligente.
2. O app envia a mensagem para o **Backend CLYVO VET** (API REST em Python/FastAPI, `app/main.py`).
3. O backend identifica o pet associado à conversa e consulta o **Banco de Dados** para recuperar perfil, histórico clínico, vacinas e medicamentos daquele pet.
4. O backend monta o **prompt contextualizado** (dados do pet + pergunta do tutor + instruções de sistema) e envia para o **Serviço de IA (LLM)**.
5. O LLM gera a resposta em linguagem natural (ou, no caso de triagem, um nível de urgência + justificativa).
6. O backend registra a interação na tabela `interacao_ia` (auditoria) e devolve a resposta para o app.
7. O app exibe a resposta ao tutor; se a urgência for classificada como alta, o app sugere contato imediato com a clínica.

Ver diagrama completo em [`arquitetura.md`](./arquitetura.md).

## 7. Priorização de Ações / Apoio à Tomada de Decisão

Quando o tutor relata sintomas, o assistente classifica a urgência em três níveis e sugere a ação correspondente:

| Nível | Exemplo de gatilho | Ação sugerida pelo assistente |
|---|---|---|
| Baixa | "meu gato está dormindo mais que o normal" | Orientação geral + observação continuada |
| Média | "o cachorro está com vômito desde ontem" | Recomendar agendar consulta nos próximos dias |
| Alta | "meu pet não consegue respirar direito" | Recomendar contato imediato com a clínica / emergência |

Essa classificação **não substitui o diagnóstico veterinário** — o próprio texto gerado pela IA deixa isso explícito, funcionando como apoio à priorização e não como diagnóstico automatizado.

## 8. Considerações Éticas e de Dados

- Dados clínicos do pet e dados pessoais do tutor são sensíveis: o serviço de IA recebe apenas o contexto necessário à pergunta (não o histórico completo de todos os pets do tutor).
- O assistente é instruído (via prompt de sistema) a nunca fornecer diagnóstico definitivo, apenas orientação e triagem, reforçando que o atendimento veterinário humano é sempre a fonte de decisão final.
- Interações ficam registradas para fins de auditoria e melhoria, respeitando os princípios de minimização de dados da LGPD.

## 9. Implementação (Sprint 4)

Atendendo ao feedback da Sprint 3 ("era esperado uma prototipação"), nesta sprint o assistente foi **implementado de ponta a ponta e funciona sem erros**.

| Componente | Implementação | Arquivo |
|---|---|---|
| API REST | FastAPI com validação de entrada (Pydantic) e erros tratados (404, 422, 503) | `app/main.py` |
| Acesso a dados | Oracle FIAP via `oracledb` (modo thin). Sem credenciais, usa um SQLite com os mesmos dados, para a demonstração nunca parar | `app/db.py` |
| Retrieval + contexto (RAG) | Busca o pet, o tutor, a clínica e o histórico e monta um contexto estruturado com os alertas calculados | `app/assistente.py` |
| LLM | Claude (Anthropic API, modelo configurável) ou Gemini (Google AI Studio), escolhido pela chave no `.env` | `app/assistente.py` |
| Fallback | Sem chave ou com falha de rede/API, o **modo simulado** responde com o mesmo contexto, e a tela informa o modo usado | `app/assistente.py` |
| Recomendações | Motor de regras: reforço anual de vacina, check-up anual (semestral para cão a partir de 7 anos e gato a partir de 10), tratamentos ativos | `app/recomendacoes.py` |
| Triagem | O LLM devolve um JSON (nível, justificativa, orientação). As palavras-chave de emergência (ex.: "não consegue respirar", "convulsão", "chocolate") garantem nível mínimo. **Nível final = o mais alto** | `app/triagem.py` |
| Telas | App do tutor (painel, chat, triagem) e painel da clínica | `app/static/index.html` |
| Testes | 12 testes automatizados ponta a ponta | `tests/test_api.py` |

### 9.1 Por que uma abordagem híbrida (LLM + regras)

- **Cálculos determinísticos ficam nas regras:** datas de vacina, dias de atraso e idade. LLMs erram contas de data, e esses alertas precisam ser exatos.
- **Linguagem natural fica no LLM:** entender perguntas livres, explicar de forma acolhedora e adaptar o tom ao tutor.
- **Segurança na triagem:** se o LLM subestimar um caso grave, a regra eleva o nível. Em saúde, um falso alarme custa menos do que deixar passar uma emergência.

### 9.2 Prompt de sistema (resumo)

O assistente responde em português, em até 150 palavras, **somente** com base no contexto do pet. Ele não dá diagnóstico definitivo nem prescreve medicamentos ou doses, encaminha emergências para a clínica com o telefone dela e ajusta o tom ao perfil do tutor. Texto completo em `app/assistente.py` (`SISTEMA` e `SISTEMA_TRIAGEM`).

## 10. Testes e Resultados

Os cenários e os resultados estão em [`testes.md`](./testes.md). Resumo: 12 de 12 testes automatizados passam, cobrindo recomendações, chat com dados reais, personalização, triagem nos três níveis, painel da clínica e tratamento de erros.

## 11. Limitações e Próximos Passos

- A triagem é apoio à decisão, não diagnóstico: o aviso legal aparece em toda resposta.
- As regras de vacina usam reforço anual para todas as vacinas; o ideal é ter o protocolo de cada vacina cadastrado pela clínica.
- Próximos passos: integrar o endpoint ao app mobile e ao backend Java (ClyvoPet), notificar o tutor quando um reforço estiver perto de vencer e avaliar as respostas do LLM com um conjunto de perguntas de referência.
