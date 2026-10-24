"""Le o arquivo .env (se existir) e expoe as configuracoes do projeto."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _carregar_env():
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        # variavel ja definida no sistema tem prioridade sobre o .env
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_env()

# Oracle da FIAP (se vazio, usa o banco local SQLite de demonstracao)
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_DSN = os.getenv("ORACLE_DSN", "oracle.fiap.com.br:1521/ORCL")
SQLITE_PATH = os.getenv("SQLITE_PATH", str(RAIZ / "data" / "clyvo_demo.db"))

# IA: "anthropic", "gemini", "simulado" ou vazio (escolhe pela chave disponivel)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def usa_oracle():
    return bool(ORACLE_USER and ORACLE_PASSWORD)


def provedor_ia():
    if LLM_PROVIDER:
        return LLM_PROVIDER
    if ANTHROPIC_API_KEY:
        return "anthropic"
    if GEMINI_API_KEY:
        return "gemini"
    return "simulado"
