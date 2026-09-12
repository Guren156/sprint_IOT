# Roteiro — Vídeo Pitch (Sprint 3, ~5 minutos)

Objetivo do vídeo: apresentar a proposta da solução, o papel da IA no sistema, os benefícios para o tutor e para a clínica, e a arquitetura de funcionamento. Gravar em modo não listado no YouTube.

Dica: cada integrante pode falar uma parte, mostrando participação de todo o grupo.

---

### 1. Abertura (0:00 – 0:30) — ~30s
- Apresentar o grupo (nomes e RMs na tela ou faladas).
- Uma frase: "Este é o vídeo pitch do componente de Inteligência Artificial do CLYVO VET, entrega da Sprint 3 da disciplina Disruptive Architectures."

### 2. O Problema (0:30 – 1:30) — ~1 min
- Explicar o contexto do CLYVO VET (app de gestão de saúde de pets: cadastro, consultas, vacinas, histórico).
- Problema: tutores não têm acompanhamento proativo da saúde do pet; clínica perde tempo com dúvidas repetitivas e não prioriza atendimentos por urgência real.
- Mostrar (tela ou protótipo) como seria a jornada do tutor sem o assistente.

### 3. A Solução de IA e Justificativa (1:30 – 3:00) — ~1min30
- Apresentar o "Assistente Inteligente CLYVO": IA Generativa (LLM) com RAG.
- Justificar por que essa abordagem foi escolhida em vez de modelo preditivo, motor de regras ou recomendação clássica (usar a tabela comparativa da documentação como apoio visual).
- Explicar rapidamente o que é RAG e por que ele evita respostas genéricas/erradas ("alucinação"): a resposta é sempre baseada nos dados reais daquele pet.

### 4. Arquitetura e Fluxo de Dados (3:00 – 4:15) — ~1min15
- Mostrar o diagrama de `arquitetura.md` na tela.
- Narrar o fluxo passo a passo: tutor pergunta → app → backend busca dados no banco → contexto é montado → LLM responde → resposta volta ao tutor → alerta de urgência alta vai para a clínica.
- Citar os dados usados (perfil, histórico clínico, vacinas, medicamentos) e de onde vêm.

### 5. Benefícios (4:15 – 4:45) — ~30s
- Para o tutor: orientação proativa, respostas imediatas, alertas de vacina/cuidado.
- Para a clínica: triagem automática por urgência, redução de perguntas repetitivas, mais tempo para casos que realmente precisam de atenção humana.

### 6. Encerramento (4:45 – 5:00) — ~15s
- Reforçar que essa é a etapa de definição/documentação (Sprint 3) e que a implementação funcional será entregue na Sprint 4.
- Agradecer.

---

## Checklist antes de gravar
- [ ] Áudio claro, sem ruído de fundo
- [ ] Diagrama de arquitetura visível na tela durante a parte 4
- [ ] Todos os integrantes aparecem ou falam em algum momento
- [ ] Vídeo publicado no YouTube em modo **não listado**
- [ ] Link do vídeo adicionado ao README.md do repositório
