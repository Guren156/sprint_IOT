# Documentação Técnica — Componente de Inteligência Artificial

**Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA
**Projeto:** CLYVO VET
**Sprint:** 3 — Definição e documentação do componente de IA
**Grupo:** Ana Clara de Oliveira Nascimento (RM 561957), Isis Macedo (RM 561497), Henrique Pereira (RM 565608), Pedro Mariutti (RM 75999), Rafael Carvalho Meireles (RM 563413)

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

| Dado | Origem | Estrutura | Uso pela IA |
|---|---|---|---|
| Perfil do pet | Banco relacional CLYVO VET (tabela `pet`) | espécie, raça, idade, peso, sexo | Base para personalização de recomendações (ex.: cuidados por raça/idade) |
| Histórico clínico | Banco relacional (tabela `consulta` / `diagnostico`) | data, diagnóstico, observações do veterinário | Contexto para responder dúvidas do tutor e para a triagem |
| Vacinas | Banco relacional (tabela `vacina`) | tipo, data de aplicação, data de reforço | Geração de alertas proativos de vencimento |
| Medicamentos | Banco relacional (tabela `medicamento`) | nome, dosagem, período de uso | Evitar recomendações que conflitem com tratamento em curso |
| Mensagem do tutor (sintomas relatados) | Input em tempo real via app (texto livre) | texto não estruturado | Entrada para classificação de urgência (triagem) |
| Histórico de interações com o assistente | Log da própria IA (nova tabela `interacao_ia`) | pergunta, resposta, timestamp, pet_id | Auditoria, melhoria contínua do prompt e análise de uso |

## 5. Estratégia de Personalização

A personalização ocorre em duas camadas:

1. **Personalização por dados estruturados:** cada resposta é gerada com o contexto específico daquele pet (idade, raça, histórico) — nunca uma resposta genérica igual para todos os animais.
2. **Personalização por comportamento:** o histórico de interações (`interacao_ia`) permite ajustar o tom e o nível de detalhe das respostas com base em quão frequentemente aquele tutor já interagiu com o assistente (tutor iniciante recebe explicações mais didáticas; tutor recorrente recebe respostas mais diretas).

## 6. Fluxo de Dados (Ponta a Ponta)

1. Tutor abre o app CLYVO VET e escreve uma pergunta ou descreve um sintoma no chat do Assistente Inteligente.
2. O app envia a mensagem para o **Backend CLYVO VET** (API REST em .NET/Java, conforme construída nas outras disciplinas).
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

## 9. Escopo desta Sprint vs. Próxima Sprint

- **Sprint 3 (esta entrega):** definição do problema, da abordagem de IA, dos dados, da arquitetura de integração e da estratégia de personalização — entregue como documentação + vídeo pitch.
- **Sprint 4 (próxima entrega):** implementação funcional do assistente (integração real ou simulada com LLM), testes com cenários reais de uso e demonstração em vídeo do funcionamento ponta a ponta.
