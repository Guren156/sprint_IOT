"""Triagem de sintomas: regras de seguranca + classificacao do LLM.

As palavras-chave garantem que sinais graves NUNCA sejam classificados
como baixa urgencia, mesmo que o LLM erre. O nivel final e o MAIS ALTO
entre a regra e o LLM.
"""
import unicodedata

NIVEIS = ["BAIXA", "MEDIA", "ALTA"]

SINAIS_ALTA = [
    "nao consegue respirar", "falta de ar", "respirando com dificuldade", "convuls",
    "desmai", "inconsciente", "sangrando", "sangramento", "envenen", "veneno",
    "atropel", "gengiva roxa", "gengiva branca", "barriga inchada", "abdomen inchado",
    "nao consegue urinar", "nao urina", "engoliu", "nao levanta", "vomitando sangue",
    "sangue nas fezes", "chocolate",
]
SINAIS_MEDIA = [
    "vomit", "diarreia", "febre", "mancando", "manca", "nao come", "nao quer comer",
    "sem apetite", "tosse", "tossindo", "ferida", "olho vermelho", "coceira",
    "apatico", "triste", "bebendo muita agua", "espirr", "caroco", "com dor", "sentindo dor", "chorando",
]

ORIENTACAO = {
    "ALTA": "Procure a clinica ou um pronto-atendimento veterinario IMEDIATAMENTE.",
    "MEDIA": "Agende uma consulta nos proximos dias e observe a evolucao dos sintomas.",
    "BAIXA": "Observe o pet nas proximas 24-48h. Se piorar ou surgirem novos sintomas, procure a clinica.",
}


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def classificar_por_regras(sintomas):
    texto = normalizar(sintomas)
    encontrados = [s for s in SINAIS_ALTA if s in texto]
    if encontrados:
        return "ALTA", encontrados
    encontrados = [s for s in SINAIS_MEDIA if s in texto]
    if encontrados:
        return "MEDIA", encontrados
    return "BAIXA", []


def nivel_mais_alto(a, b):
    return a if NIVEIS.index(a) >= NIVEIS.index(b) else b
