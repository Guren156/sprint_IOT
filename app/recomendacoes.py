"""Motor de recomendacoes proativas a partir do historico real do pet.

Regras deterministicas (sem LLM): vacinas vencendo/vencidas, check-up
atrasado, cuidado extra para pet idoso e tratamentos em andamento.
Essas recomendacoes tambem entram no contexto enviado ao LLM.
"""
from datetime import date

VALIDADE_VACINA_DIAS = 365
ORDEM = {"ALTA": 0, "MEDIA": 1, "BAIXA": 2, "INFO": 3}


def idade_anos(dt_nascimento, hoje=None):
    hoje = hoje or date.today()
    anos = hoje.year - dt_nascimento.year
    if (hoje.month, hoje.day) < (dt_nascimento.month, dt_nascimento.day):
        anos -= 1
    return anos


def eh_idoso(pet, hoje=None):
    limite = 10 if pet["especie"].lower().startswith("gato") else 7
    return idade_anos(pet["dt_nascimento"], hoje) >= limite


def _nome_vacina(detalhes):
    # "V10 - reforco anual" -> "V10" ; "Antirrabica aplicada" -> "Antirrabica"
    return (detalhes or "Vacina").split()[0].strip("-,.").capitalize()


def situacao_vacinas(historico, hoje=None):
    """Ultima dose de cada vacina e quantos dias faltam para o reforco."""
    hoje = hoje or date.today()
    ultimas = {}
    for reg in historico:
        if reg["tipo_registro"].lower() != "vacinacao":
            continue
        nome = _nome_vacina(reg["detalhes"])
        if nome not in ultimas or reg["dt_evento"] > ultimas[nome]:
            ultimas[nome] = reg["dt_evento"]
    vacinas = []
    for nome, dt in sorted(ultimas.items()):
        dias = VALIDADE_VACINA_DIAS - (hoje - dt).days
        vacinas.append({"vacina": nome, "ultima_dose": dt, "dias_para_reforco": dias})
    return vacinas


def tratamentos_ativos(historico, hoje=None):
    hoje = hoje or date.today()
    ativos = []
    for reg in historico:
        if reg["tipo_registro"].lower() != "medicacao":
            continue
        detalhes = reg["detalhes"] or ""
        if "continuo" in detalhes.lower() or (hoje - reg["dt_evento"]).days <= 30:
            ativos.append(detalhes)
    return ativos


def gerar(pet, historico, hoje=None):
    hoje = hoje or date.today()
    nome = pet["nome_pet"]
    recs = []

    vacinas = situacao_vacinas(historico, hoje)
    if not vacinas:
        recs.append({"prioridade": "MEDIA", "titulo": "Sem registro de vacinas",
                     "detalhe": f"Nao ha vacinas de {nome} no historico. Leve a carteirinha na clinica."})
    for v in vacinas:
        dias = v["dias_para_reforco"]
        if dias < 0:
            recs.append({"prioridade": "ALTA", "titulo": f"Vacina {v['vacina']} vencida",
                         "detalhe": f"O reforco de {nome} venceu ha {-dias} dias. Agende a aplicacao."})
        elif dias <= 30:
            recs.append({"prioridade": "MEDIA", "titulo": f"Vacina {v['vacina']} vence em {dias} dias",
                         "detalhe": f"Agende o reforco de {nome} antes do vencimento."})

    consultas = [r["dt_evento"] for r in historico
                 if r["tipo_registro"].lower() in ("consulta", "exame")]
    intervalo = 180 if eh_idoso(pet, hoje) else 365
    ultima = max(consultas) if consultas else None
    if ultima is None or (hoje - ultima).days > intervalo:
        tipo = "semestral (pet idoso)" if intervalo == 180 else "anual"
        quando = f"ultima em {ultima.strftime('%d/%m/%Y')}" if ultima else "nenhuma registrada"
        recs.append({"prioridade": "MEDIA", "titulo": f"Check-up {tipo} atrasado",
                     "detalhe": f"{nome}: {quando}. Recomendado agendar uma consulta de rotina."})

    for t in tratamentos_ativos(historico, hoje):
        recs.append({"prioridade": "INFO", "titulo": "Tratamento em andamento",
                     "detalhe": f"{t}. Siga a prescricao e nao interrompa sem falar com o veterinario."})

    if eh_idoso(pet, hoje):
        recs.append({"prioridade": "BAIXA", "titulo": "Pet idoso",
                     "detalhe": f"{nome} tem {idade_anos(pet['dt_nascimento'], hoje)} anos: "
                                "fique atento a mobilidade, apetite e peso."})

    return sorted(recs, key=lambda r: ORDEM[r["prioridade"]])
