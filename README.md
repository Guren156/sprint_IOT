# CLYVO VET — Assistente Inteligente (Sprint 3)

Documentação do componente de Inteligência Artificial do projeto **CLYVO VET**, entregue na disciplina **Disruptive Architectures: IoT, IoB & Generative IA**.

## Integrantes

| Nome | RM |
|---|---|
| Ana Clara de Oliveira Nascimento | 561957 |
| Isis Macedo | 561497 |
| Henrique Pereira | 565608 |
| Pedro Mariutti | 75999 |
| Rafael Carvalho Meireles | 563413 |

## Sobre esta entrega (Sprint 3)

Nesta sprint, o objetivo foi **definir e documentar** o componente de Inteligência Artificial que será integrado ao CLYVO VET — sem ainda implementá-lo. A implementação funcional está prevista para a Sprint 4.

Propomos um **Assistente Inteligente** baseado em IA Generativa (LLM) com Retrieval-Augmented Generation (RAG), capaz de:
- Responder dúvidas do tutor sobre o pet com base no histórico clínico real;
- Gerar recomendações proativas e personalizadas (ex.: alertas de vacina);
- Realizar triagem de sintomas relatados em texto livre, classificando a urgência do atendimento.

## Estrutura do repositório

```
├── README.md                      <- este arquivo
├── docs/
│   ├── documentacao-tecnica.md    <- problema, dados, abordagem de IA, justificativa, personalização
│   ├── arquitetura.md             <- diagrama de arquitetura (Mermaid) + fluxo de dados
│   └── roteiro-video.md           <- roteiro usado para gravar o vídeo pitch
```

## Links da entrega

- **Vídeo pitch (YouTube, não listado):** _adicionar link aqui após gravar_
- **Documentação técnica completa:** [`docs/documentacao-tecnica.md`](./docs/documentacao-tecnica.md)
- **Diagrama de arquitetura:** [`docs/arquitetura.md`](./docs/arquitetura.md)

## Tecnologias previstas

| Componente | Tecnologia |
|---|---|
| Aplicação (frontend) | Mobile / Web CLYVO VET (construída nas disciplinas de Mobile / Java / .NET) |
| Backend | API REST (.NET ou Java, conforme entrega das outras disciplinas) |
| Banco de dados | Banco relacional do CLYVO VET (perfil, histórico clínico, vacinas, medicamentos) |
| IA | LLM Generativo com RAG (contexto injetado a partir dos dados do pet) |

## Resultados parciais (Sprint 3)

| Item | Status |
|---|---|
| Definição do problema de negócio | Concluído |
| Escolha e justificativa da abordagem de IA | Concluído |
| Identificação dos dados necessários | Concluído |
| Estratégia de personalização | Concluído |
| Diagrama de arquitetura | Concluído |
| Implementação funcional do assistente | Planejado para Sprint 4 |
