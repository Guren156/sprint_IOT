# Roteiro — Vídeo da Sprint 4 (~5 minutos)

Objetivo: apresentar a solução e **demonstrar o assistente funcionando de verdade**. O feedback da Sprint 3 pediu prototipação, então o vídeo deve ser principalmente demonstração. Publicar no YouTube como **não listado**.

Antes de gravar: suba a aplicação (`python -m uvicorn app.main:app --port 8000`), abra http://localhost:8000 e deixe o SQL Developer aberto. Se possível, configure uma chave de LLM no `.env` para o status mostrar "IA: claude" ou "IA: gemini".

---

### 1. Abertura (0:00 – 0:20)
- Grupo (nomes e RMs na tela).
- "Na Sprint 3 apresentamos a proposta. Agora vamos mostrar o Assistente Inteligente da CLYVO VET funcionando."

### 2. Problema e solução (0:20 – 1:00)
- Tutor sem acompanhamento proativo; clínica sem priorização por urgência.
- Solução: IA generativa com RAG sobre o histórico real do pet, mais regras de segurança (abordagem híbrida).

### 3. Arquitetura (1:00 – 1:40)
- Mostrar o diagrama de `docs/arquitetura.md`.
- Tela → API FastAPI → Oracle (busca o pet) → contexto → LLM → resposta → log em `T_CLY_INTERACAO_IA` → painel da clínica.

### 4. Demonstração (1:40 – 4:15) — a parte principal
Seguir os cenários de `docs/testes.md`:
1. Thor: mostrar as recomendações (V10 vencendo, check-up atrasado) e explicar que vêm do banco.
2. Chat: "As vacinas estão em dia?" A resposta usa as datas reais.
3. Mel: "Ela está tomando algum remédio?" O assistente cita a Amoxicilina.
4. Triagem MÉDIA: "está vomitando desde ontem e não quer comer".
5. Triagem ALTA (Nina): "comeu chocolate e está tremendo". Mostrar o telefone da clínica e o aviso legal.
6. Painel da Clínica: a triagem ALTA no topo e as vacinas vencidas.
7. SQL Developer: `SELECT * FROM T_CLY_INTERACAO_IA ORDER BY id_interacao DESC;` mostra o registro no Oracle.
8. (Rápido) Rodar `python -m pytest -v` e mostrar os 12 testes passando.

### 5. Benefícios e personalização (4:15 – 4:45)
- Tutor: respostas imediatas baseadas no pet e alertas proativos; o tom muda de iniciante para recorrente.
- Clínica: triagem priorizada, contato proativo de vacinas e auditoria das interações.

### 6. Encerramento (4:45 – 5:00)
- Repositório no GitHub com README e instruções. Agradecer.

---

## Checklist
- [ ] Todos os integrantes falam em algum momento
- [ ] A demonstração mostra as funcionalidades sem erro
- [ ] O registro no Oracle aparece no SQL Developer
- [ ] Vídeo publicado como **não listado** e link adicionado ao README.md
