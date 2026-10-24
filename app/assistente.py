"""Assistente Inteligente CLYVO: RAG com os dados do pet + LLM.

Fluxo: busca o pet no banco (retrieval) -> monta o contexto -> envia ao LLM
(Claude ou Gemini) -> devolve a resposta. Se nao houver chave de API ou o
servico falhar, um modo simulado responde usando o mesmo contexto, para a
aplicacao nunca quebrar na demonstracao.
"""
import json
import re
import urllib.request
from datetime import date

from app import config, db, recomendacoes, triagem

SISTEMA = """Voce e o Assistente Inteligente da CLYVO VET, que orienta tutores sobre a saude dos pets.
Regras:
- Responda em portugues do Brasil, de forma acolhedora, em no maximo 150 palavras.
- Use SOMENTE as informacoes do CONTEXTO DO PET. Se a informacao nao estiver la, diga que nao consta no historico e oriente falar com a clinica.
- Nunca de diagnostico definitivo nem prescreva medicamentos ou doses; voce faz orientacao e triagem, a decisao e do veterinario.
- Se houver sinal de emergencia, mande procurar a clinica imediatamente e informe o telefone dela.
- Ajuste o tom ao PERFIL DO TUTOR: iniciante = explique termos de forma didatica; recorrente = seja direto."""

SISTEMA_TRIAGEM = SISTEMA + """
Agora voce esta fazendo TRIAGEM de sintomas. Responda APENAS com um JSON, sem texto fora dele:
{"nivel": "BAIXA" | "MEDIA" | "ALTA", "justificativa": "<ate 2 frases>", "orientacao": "<o que o tutor deve fazer agora>"}"""


# ---------------------------------------------------------------- contexto (RAG)
def perfil_tutor(id_tutor):
    total = db.contar_interacoes(id_tutor)
    return ("recorrente" if total >= 3 else "iniciante"), total


def montar_contexto(pet, historico, recs, perfil):
    idade = recomendacoes.idade_anos(pet["dt_nascimento"])
    linhas = [
        "CONTEXTO DO PET",
        f"Nome: {pet['nome_pet']} | Especie: {pet['especie']} | Raca: {pet['raca']} | "
        f"Idade: {idade} anos | Peso: {pet['peso']} kg",
        f"Tutor: {pet['nome_usuario']} | Clinica: {pet['nome_clinica']} (tel. {pet['telefone_clinica']})",
        f"Data de hoje: {date.today().strftime('%d/%m/%Y')}",
        "Historico de saude (mais recente primeiro):",
    ]
    for h in historico:
        linhas.append(f"- {h['dt_evento'].strftime('%d/%m/%Y')} | {h['tipo_registro']} | {h['detalhes']}")
    if not historico:
        linhas.append("- (sem registros)")
    linhas.append("Alertas calculados pelo sistema:")
    for r in recs:
        linhas.append(f"- [{r['prioridade']}] {r['titulo']}: {r['detalhe']}")
    if not recs:
        linhas.append("- nenhum alerta")
    linhas.append(f"PERFIL DO TUTOR: {perfil}")
    return "\n".join(linhas)


# ---------------------------------------------------------------- provedores LLM
MODELOS_COM_FALLBACK = ("claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5")


def _chamar_claude(sistema, mensagem):
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=40.0, max_retries=1)
    params = dict(model=config.ANTHROPIC_MODEL, max_tokens=4000, system=sistema,
                  messages=[{"role": "user", "content": mensagem}],
                  output_config={"effort": "low"})
    if config.ANTHROPIC_MODEL in MODELOS_COM_FALLBACK:
        # se o filtro de seguranca recusar, a API tenta outro modelo automaticamente
        resposta = client.beta.messages.create(**params, betas=["server-side-fallback-2026-07-01"],
                                               fallbacks="default")
    else:
        resposta = client.messages.create(**params)
    if resposta.stop_reason == "refusal":
        raise RuntimeError("o modelo recusou a solicitacao")
    texto = "".join(b.text for b in resposta.content if b.type == "text").strip()
    if not texto:
        raise RuntimeError("resposta vazia do modelo")
    return texto


def _chamar_gemini(sistema, mensagem, json_saida=False):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent"
    corpo = {
        "system_instruction": {"parts": [{"text": sistema}]},
        "contents": [{"role": "user", "parts": [{"text": mensagem}]}],
    }
    if json_saida:
        corpo["generationConfig"] = {"responseMimeType": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(corpo).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json",
                                          "x-goog-api-key": config.GEMINI_API_KEY})
    with urllib.request.urlopen(req, timeout=40) as r:
        dados = json.loads(r.read().decode("utf-8"))
    return dados["candidates"][0]["content"]["parts"][0]["text"].strip()


def chamar_llm(sistema, mensagem, json_saida=False):
    """Devolve (texto, modo). Lanca excecao se o provedor falhar."""
    provedor = config.provedor_ia()
    if provedor == "anthropic" and config.ANTHROPIC_API_KEY:
        return _chamar_claude(sistema, mensagem), "claude"
    if provedor == "gemini" and config.GEMINI_API_KEY:
        return _chamar_gemini(sistema, mensagem, json_saida), "gemini"
    raise RuntimeError("nenhum LLM configurado")


# ---------------------------------------------------------------- modo simulado
def _resposta_simulada(pet, historico, recs, perfil, pergunta):
    nome = pet["nome_pet"]
    p = triagem.normalizar(pergunta)
    partes = []
    if perfil == "iniciante":
        partes.append(f"Ola, {pet['nome_usuario']}! Vou te ajudar com base no historico de {nome}.")

    if "vacin" in p:
        vacinas = recomendacoes.situacao_vacinas(historico)
        if not vacinas:
            partes.append(f"Nao ha vacinas de {nome} registradas no historico.")
        for v in vacinas:
            dias = v["dias_para_reforco"]
            situacao = f"vencida ha {-dias} dias" if dias < 0 else f"reforco em {dias} dias"
            partes.append(f"- {v['vacina']}: ultima dose em {v['ultima_dose'].strftime('%d/%m/%Y')} ({situacao}).")
        if perfil == "iniciante":
            partes.append("O reforco anual mantem a protecao do pet contra doencas graves.")
    elif any(t in p for t in ("remedio", "medica", "tratamento", "antibiotico")):
        ativos = recomendacoes.tratamentos_ativos(historico)
        if ativos:
            partes.append(f"Tratamento em andamento de {nome}: " + "; ".join(ativos) + ".")
            partes.append("Siga exatamente a prescricao e nao suspenda sem falar com o veterinario.")
        else:
            partes.append(f"Nao ha tratamento ativo de {nome} no historico. Nao medique sem orientacao.")
    elif any(t in p for t in ("peso", "comida", "racao", "aliment", "gordo", "magro")):
        partes.append(f"{nome} pesa {pet['peso']} kg (ultimo registro). A quantidade ideal de racao "
                      "depende de idade, raca e atividade; o veterinario pode montar um plano.")
    elif any(t in p for t in ("consulta", "check", "exame", "veterinario")):
        consultas = [h for h in historico if h["tipo_registro"].lower() in ("consulta", "exame")]
        if consultas:
            c = consultas[0]
            partes.append(f"Ultimo atendimento: {c['dt_evento'].strftime('%d/%m/%Y')} - {c['detalhes']}.")
        else:
            partes.append(f"Nao ha consultas de {nome} registradas.")
    else:
        partes.append(f"{nome} e um(a) {pet['especie'].lower()} {pet['raca']} de "
                      f"{recomendacoes.idade_anos(pet['dt_nascimento'])} anos.")

    importantes = [r for r in recs if r["prioridade"] in ("ALTA", "MEDIA")]
    if importantes:
        partes.append("Atencao: " + "; ".join(r["titulo"] for r in importantes) + ".")
    partes.append(f"Em caso de duvida, fale com a {pet['nome_clinica']} pelo {pet['telefone_clinica']}.")
    return "\n".join(partes)


# ---------------------------------------------------------------- casos de uso
def _carregar(id_pet):
    pet = db.obter_pet(id_pet)
    if pet is None:
        return None
    historico = db.historico(id_pet)
    recs = recomendacoes.gerar(pet, historico)
    return pet, historico, recs


def painel_pet(id_pet):
    dados = _carregar(id_pet)
    if dados is None:
        return None
    pet, historico, recs = dados
    return {"pet": pet, "idade": recomendacoes.idade_anos(pet["dt_nascimento"]),
            "historico": historico, "recomendacoes": recs,
            "vacinas": recomendacoes.situacao_vacinas(historico)}


def conversar(id_pet, pergunta):
    dados = _carregar(id_pet)
    if dados is None:
        return None
    pet, historico, recs = dados
    perfil, total = perfil_tutor(pet["id_usuario"])
    contexto = montar_contexto(pet, historico, recs, perfil)
    aviso = None
    try:
        resposta, modo = chamar_llm(SISTEMA, f"{contexto}\n\nPERGUNTA DO TUTOR: {pergunta}")
    except Exception as erro:
        resposta, modo = _resposta_simulada(pet, historico, recs, perfil, pergunta), "simulado"
        if config.provedor_ia() != "simulado":
            aviso = f"LLM indisponivel ({type(erro).__name__}); resposta gerada no modo simulado."
    db.salvar_interacao(id_pet, pet["id_usuario"], "CHAT", pergunta, resposta, None, modo)
    return {"resposta": resposta, "modo": modo, "perfil_tutor": perfil,
            "interacoes_anteriores": total, "aviso": aviso}


def _ler_json(texto):
    achado = re.search(r"\{.*\}", texto, re.DOTALL)
    dados = json.loads(achado.group(0) if achado else texto)
    nivel = str(dados.get("nivel", "")).upper().replace("É", "E")
    if nivel not in triagem.NIVEIS:
        raise ValueError("nivel invalido")
    return nivel, str(dados.get("justificativa", "")), str(dados.get("orientacao", ""))


def triar(id_pet, sintomas):
    dados = _carregar(id_pet)
    if dados is None:
        return None
    pet, historico, recs = dados
    perfil, _ = perfil_tutor(pet["id_usuario"])
    nivel_regra, sinais = triagem.classificar_por_regras(sintomas)
    contexto = montar_contexto(pet, historico, recs, perfil)
    aviso = None
    try:
        texto, modo = chamar_llm(SISTEMA_TRIAGEM, f"{contexto}\n\nSINTOMAS RELATADOS: {sintomas}",
                                 json_saida=True)
        nivel_llm, justificativa, orientacao = _ler_json(texto)
    except Exception as erro:
        modo, nivel_llm = "simulado", None
        justificativa = ("Sinais identificados: " + ", ".join(sinais) + ".") if sinais \
            else "Nenhum sinal de alerta identificado no relato."
        orientacao = triagem.ORIENTACAO[nivel_regra]
        if config.provedor_ia() != "simulado":
            aviso = f"LLM indisponivel ({type(erro).__name__}); triagem feita pelas regras."

    nivel = triagem.nivel_mais_alto(nivel_llm or nivel_regra, nivel_regra)
    if nivel_llm and nivel != nivel_llm:
        orientacao = triagem.ORIENTACAO[nivel]
    if nivel == "ALTA":
        orientacao += f" Telefone da {pet['nome_clinica']}: {pet['telefone_clinica']}."

    resposta = f"{justificativa} {orientacao}".strip()
    db.salvar_interacao(id_pet, pet["id_usuario"], "TRIAGEM", sintomas, resposta, nivel, modo)
    return {"nivel": nivel, "nivel_regras": nivel_regra, "nivel_llm": nivel_llm,
            "sinais_detectados": sinais, "justificativa": justificativa,
            "orientacao": orientacao, "modo": modo, "aviso": aviso,
            "aviso_legal": "Triagem de apoio. Nao substitui o diagnostico do veterinario."}


def alertas_clinica():
    """Painel da clinica: triagens recentes + pets com vacina vencida."""
    vacinas_vencidas = []
    for pet in db.listar_todos_pets():
        for v in recomendacoes.situacao_vacinas(db.historico(pet["id_pet"])):
            if v["dias_para_reforco"] < 0:
                vacinas_vencidas.append({"id_pet": pet["id_pet"], "nome_pet": pet["nome_pet"],
                                         "tutor": pet["nome_usuario"], "telefone": pet["telefone_tutor"],
                                         "vacina": v["vacina"], "dias_vencida": -v["dias_para_reforco"]})
    triagens = db.listar_triagens()
    ordem = {"ALTA": 0, "MEDIA": 1, "BAIXA": 2}
    triagens.sort(key=lambda t: (ordem.get(t["nivel_urgencia"], 3), -t["id_interacao"]))
    return {"triagens": triagens, "vacinas_vencidas": vacinas_vencidas}
