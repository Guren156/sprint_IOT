"""Testes ponta a ponta da API (banco SQLite temporario + IA em modo simulado).

Rodar:  python -m pytest -v
"""
import os
import tempfile

import pytest

os.environ["ORACLE_USER"] = ""
os.environ["LLM_PROVIDER"] = "simulado"
os.environ["SQLITE_PATH"] = os.path.join(tempfile.mkdtemp(), "teste.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

cliente = TestClient(app)


def test_status():
    r = cliente.get("/api/status")
    assert r.status_code == 200
    assert r.json()["banco"] == "sqlite"
    assert r.json()["ia"] == "simulado"


def test_pagina_web():
    r = cliente.get("/")
    assert r.status_code == 200
    assert "Assistente Inteligente" in r.text


def test_tutores_e_pets():
    assert len(cliente.get("/api/tutores").json()) == 5
    pets = cliente.get("/api/tutores/1/pets").json()
    assert [p["nome_pet"] for p in pets] == ["Thor", "Mel", "Tom"]


def test_recomendacoes_usam_historico_real():
    thor = cliente.get("/api/pets/101").json()
    titulos = [r["titulo"] for r in thor["recomendacoes"]]
    assert any("V10 vence em" in t for t in titulos)          # reforco proximo
    assert any("Check-up anual atrasado" in t for t in titulos)

    mel = cliente.get("/api/pets/102").json()
    assert mel["recomendacoes"][0]["prioridade"] == "ALTA"     # vacina vencida vem primeiro
    assert any(r["titulo"] == "Tratamento em andamento" for r in mel["recomendacoes"])

    rex = cliente.get("/api/pets/106").json()
    assert any("semestral" in r["titulo"] for r in rex["recomendacoes"])  # pet idoso


def test_chat_responde_com_dados_do_pet_e_registra():
    r = cliente.post("/api/chat", json={"id_pet": 102, "pergunta": "Ela esta tomando algum remedio?"})
    assert r.status_code == 200
    corpo = r.json()
    assert "Amoxicilina" in corpo["resposta"]
    assert corpo["modo"] == "simulado"
    assert cliente.get("/api/pets/102/interacoes").json()[0]["tipo"] == "CHAT"


def test_personalizacao_tutor_iniciante_vira_recorrente():
    perfis = [cliente.post("/api/chat", json={"id_pet": 104, "pergunta": "As vacinas estao em dia?"})
              .json()["perfil_tutor"] for _ in range(4)]
    assert perfis[0] == "iniciante"
    assert perfis[-1] == "recorrente"


@pytest.mark.parametrize("sintomas,nivel", [
    ("Meu cachorro nao consegue respirar direito", "ALTA"),
    ("Ele comeu chocolate agora pouco", "ALTA"),
    ("Está vomitando desde ontem e não quer comer", "MEDIA"),
    ("Meu gato esta dormindo mais que o normal", "BAIXA"),
])
def test_triagem(sintomas, nivel):
    r = cliente.post("/api/triagem", json={"id_pet": 101, "sintomas": sintomas})
    assert r.status_code == 200
    assert r.json()["nivel"] == nivel


def test_triagem_alta_aparece_no_painel_da_clinica():
    cliente.post("/api/triagem", json={"id_pet": 105, "sintomas": "Teve uma convulsao agora"})
    painel = cliente.get("/api/clinica/alertas").json()
    assert painel["triagens"][0]["nivel_urgencia"] == "ALTA"
    assert any(v["nome_pet"] == "Mel" for v in painel["vacinas_vencidas"])


def test_erros_tratados():
    assert cliente.get("/api/pets/999").status_code == 404
    assert cliente.post("/api/chat", json={"id_pet": 999, "pergunta": "oi tudo bem"}).status_code == 404
    assert cliente.post("/api/chat", json={"id_pet": 101, "pergunta": ""}).status_code == 422
    assert cliente.post("/api/triagem", json={"id_pet": 101}).status_code == 422
