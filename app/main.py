"""API REST do Assistente Inteligente CLYVO VET (FastAPI)."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app import assistente, config, db

app = FastAPI(title="CLYVO VET - Assistente Inteligente",
              description="Sprint 4 - Disruptive Architectures: IoT, IoB & Generative IA",
              version="4.0")

PAGINA = config.RAIZ / "app" / "static" / "index.html"


class Pergunta(BaseModel):
    id_pet: int
    pergunta: str = Field(min_length=3, max_length=500)


class Sintomas(BaseModel):
    id_pet: int
    sintomas: str = Field(min_length=3, max_length=500)


@app.exception_handler(Exception)
async def erro_inesperado(request: Request, exc: Exception):
    # erro de banco/conexao vira uma mensagem clara em vez de "500 Internal Server Error"
    return JSONResponse(status_code=503, content={
        "detail": f"Falha ao acessar o banco ({db.tipo_banco()}): {type(exc).__name__}: {exc}"})


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(PAGINA)


@app.get("/api/status")
def status():
    return {"banco": db.tipo_banco(), "ia": config.provedor_ia(),
            "modelo": config.ANTHROPIC_MODEL if config.provedor_ia() == "anthropic"
            else config.GEMINI_MODEL if config.provedor_ia() == "gemini" else "regras locais"}


@app.get("/api/tutores")
def tutores():
    return db.listar_tutores()


@app.get("/api/tutores/{id_tutor}/pets")
def pets_do_tutor(id_tutor: int):
    return db.listar_pets(id_tutor)


@app.get("/api/pets/{id_pet}")
def painel_pet(id_pet: int):
    dados = assistente.painel_pet(id_pet)
    if dados is None:
        raise HTTPException(404, "Pet nao encontrado")
    return dados


@app.get("/api/pets/{id_pet}/interacoes")
def interacoes(id_pet: int):
    return db.listar_interacoes(id_pet)


@app.post("/api/chat")
def chat(dados: Pergunta):
    resultado = assistente.conversar(dados.id_pet, dados.pergunta.strip())
    if resultado is None:
        raise HTTPException(404, "Pet nao encontrado")
    return resultado


@app.post("/api/triagem")
def triagem(dados: Sintomas):
    resultado = assistente.triar(dados.id_pet, dados.sintomas.strip())
    if resultado is None:
        raise HTTPException(404, "Pet nao encontrado")
    return resultado


@app.get("/api/clinica/alertas")
def alertas():
    return assistente.alertas_clinica()
