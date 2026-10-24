# Testes e Resultados — Sprint 4

## Testes automatizados

Rodar na raiz do projeto:

```bash
python -m pytest -v
```

Os testes usam um banco SQLite temporário (os mesmos dados do Oracle) e a IA em modo simulado, então rodam em qualquer máquina sem credenciais.

| Teste | O que verifica | Resultado |
|---|---|---|
| `test_status` | A API sobe e informa o banco e a IA em uso | ✅ |
| `test_pagina_web` | A tela web é servida em `/` | ✅ |
| `test_tutores_e_pets` | Leitura de tutores e pets do banco | ✅ |
| `test_recomendacoes_usam_historico_real` | Thor: V10 vencendo e check-up atrasado. Mel: vacina vencida em 1º lugar e tratamento ativo. Rex (idoso): check-up semestral | ✅ |
| `test_chat_responde_com_dados_do_pet_e_registra` | A pergunta sobre remédio da Mel cita a Amoxicilina do histórico, e a interação é gravada | ✅ |
| `test_personalizacao_tutor_iniciante_vira_recorrente` | O perfil muda de iniciante para recorrente após 3 interações | ✅ |
| `test_triagem` (4 casos) | "não consegue respirar" e "comeu chocolate" dão ALTA; "vomitando e não quer comer" dá MÉDIA; "dormindo mais que o normal" dá BAIXA | ✅ |
| `test_triagem_alta_aparece_no_painel_da_clinica` | Triagem ALTA aparece no topo do painel; vacinas vencidas são listadas | ✅ |
| `test_erros_tratados` | Pet inexistente devolve 404; pergunta vazia ou campo faltando devolve 422 | ✅ |

**Resultado: 12 de 12 testes passando.**

## Cenários para a demonstração no vídeo

| # | Tutor / Pet | Ação | Resultado esperado |
|---|---|---|---|
| 1 | Henrique / Thor | Abrir o painel | Alertas "V10 vence em 10 dias" e "Check-up anual atrasado" |
| 2 | Henrique / Thor | Chat: "As vacinas estão em dia?" | Lista V10 e antirrábica com as datas reais e avisa do reforço |
| 3 | Henrique / Mel | Chat: "Ela está tomando algum remédio?" | Cita a Amoxicilina 250 mg e orienta não interromper |
| 4 | Henrique / Mel | Triagem: "está vomitando desde ontem e não quer comer" | Urgência MÉDIA: agendar consulta |
| 5 | Ana Clara / Nina | Triagem: "comeu chocolate e está tremendo" | Urgência ALTA com o telefone da clínica |
| 6 | — | Abrir o Painel da Clínica | Triagem ALTA no topo e a Mel na lista de vacinas vencidas |
| 7 | — | No SQL Developer: `SELECT * FROM T_CLY_INTERACAO_IA` | Todas as interações gravadas no Oracle |

## Tratamento de falhas (sem erro de execução)

| Situação | Comportamento |
|---|---|
| Sem chave de LLM | Modo simulado responde com os dados do pet; o status mostra "IA: simulado" |
| Chave inválida, sem internet ou API fora do ar | A resposta sai pelo modo simulado e a tela mostra o aviso "LLM indisponível" |
| LLM devolve JSON inválido na triagem | O nível sai pelas regras |
| Oracle sem credenciais | Usa o SQLite local com os mesmos dados |
| Oracle fora do ar | A API responde 503 com uma mensagem clara, sem quebrar a tela |
| Entrada inválida | 422 com a validação do Pydantic |
