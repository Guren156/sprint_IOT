"""Acesso ao banco: Oracle da FIAP ou, sem credenciais, SQLite local.

As consultas sao as mesmas nos dois bancos (parametros :nome funcionam
no oracledb e no sqlite3). So a gravacao do log muda (sequence x autoincrement).
"""
import sqlite3
from datetime import date, datetime
from pathlib import Path

from app import config

SQL_PET = """
SELECT p.id_pet, p.nome_pet, p.especie, p.raca, p.dt_nascimento, p.peso,
       r.id_usuario, r.nome_usuario, r.telefone AS telefone_tutor,
       c.id_clinica, c.nome_clinica, c.telefone AS telefone_clinica
  FROM T_CLY_PETS p
  JOIN T_CLY_RESPONSAVEL r ON r.id_usuario = p.T_CLY_RESPONSAVEL_id_usuario
  JOIN T_CLY_CLINICA c ON c.id_clinica = p.T_CLY_CLINICA_id_clinica
"""


def tipo_banco():
    return "oracle" if config.usa_oracle() else "sqlite"


def _conectar():
    if config.usa_oracle():
        import oracledb  # modo thin: nao precisa instalar o Oracle Client
        return oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD,
                                dsn=config.ORACLE_DSN)
    caminho = Path(config.SQLITE_PATH)
    novo = not caminho.exists()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho)
    if novo:
        script = (config.RAIZ / "sql" / "02_sqlite_demo.sql").read_text(encoding="utf-8")
        con.executescript(script)
        con.commit()
    return con


def _para_data(valor):
    # Oracle devolve datetime; SQLite devolve texto 'AAAA-MM-DD'
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        return date.fromisoformat(valor[:10])
    return valor


def _consultar(sql, params=None):
    con = _conectar()
    try:
        cur = con.cursor()
        cur.execute(sql, params or {})
        colunas = [c[0].lower() for c in cur.description]
        linhas = []
        for linha in cur.fetchall():
            item = dict(zip(colunas, linha))
            for chave in item:
                if chave == "dt_interacao":
                    item[chave] = str(item[chave])[:16]
                elif chave.startswith("dt_"):
                    item[chave] = _para_data(item[chave])
            linhas.append(item)
        return linhas
    finally:
        con.close()


def listar_tutores():
    return _consultar("SELECT id_usuario, nome_usuario FROM T_CLY_RESPONSAVEL ORDER BY id_usuario")


def listar_pets(id_tutor):
    return _consultar(SQL_PET + " WHERE r.id_usuario = :id_tutor ORDER BY p.id_pet",
                      {"id_tutor": id_tutor})


def listar_todos_pets():
    return _consultar(SQL_PET + " ORDER BY p.id_pet")


def obter_pet(id_pet):
    linhas = _consultar(SQL_PET + " WHERE p.id_pet = :id_pet", {"id_pet": id_pet})
    return linhas[0] if linhas else None


def historico(id_pet):
    return _consultar("""
        SELECT tipo_registro, detalhes, dt_evento
          FROM T_CLY_HISTORICO_SAUDE
         WHERE T_CLY_PETS_id_pet = :id_pet
         ORDER BY dt_evento DESC""", {"id_pet": id_pet})


def contar_interacoes(id_tutor):
    linhas = _consultar("""
        SELECT COUNT(*) AS total FROM T_CLY_INTERACAO_IA
         WHERE T_CLY_RESPONSAVEL_id_usuario = :id_tutor""", {"id_tutor": id_tutor})
    return int(linhas[0]["total"])


def salvar_interacao(id_pet, id_tutor, tipo, pergunta, resposta, nivel, modo):
    params = {
        "id_pet": id_pet, "id_tutor": id_tutor, "tipo": tipo,
        "pergunta": pergunta[:1000], "resposta": resposta[:2000],
        "nivel": nivel, "modo": modo,
    }
    con = _conectar()
    try:
        cur = con.cursor()
        if config.usa_oracle():
            cur.execute("""
                INSERT INTO T_CLY_INTERACAO_IA
                VALUES (SEQ_CLY_INTERACAO_IA.NEXTVAL, :id_pet, :id_tutor, :tipo,
                        :pergunta, :resposta, :nivel, :modo, SYSDATE)""", params)
        else:
            params["agora"] = datetime.now().isoformat(sep=" ", timespec="seconds")
            cur.execute("""
                INSERT INTO T_CLY_INTERACAO_IA
                    (T_CLY_PETS_id_pet, T_CLY_RESPONSAVEL_id_usuario, tipo, pergunta,
                     resposta, nivel_urgencia, modo_ia, dt_interacao)
                VALUES (:id_pet, :id_tutor, :tipo, :pergunta, :resposta, :nivel, :modo, :agora)""",
                        params)
        con.commit()
    finally:
        con.close()


def listar_triagens(limite=20):
    return _consultar("""
        SELECT i.id_interacao, i.pergunta, i.resposta, i.nivel_urgencia, i.dt_interacao,
               p.id_pet, p.nome_pet, r.nome_usuario, r.telefone
          FROM T_CLY_INTERACAO_IA i
          JOIN T_CLY_PETS p ON p.id_pet = i.T_CLY_PETS_id_pet
          JOIN T_CLY_RESPONSAVEL r ON r.id_usuario = i.T_CLY_RESPONSAVEL_id_usuario
         WHERE i.tipo = 'TRIAGEM'
         ORDER BY i.id_interacao DESC""")[:limite]


def listar_interacoes(id_pet, limite=10):
    return _consultar("""
        SELECT id_interacao, tipo, pergunta, resposta, nivel_urgencia, modo_ia, dt_interacao
          FROM T_CLY_INTERACAO_IA
         WHERE T_CLY_PETS_id_pet = :id_pet
         ORDER BY id_interacao DESC""", {"id_pet": id_pet})[:limite]
