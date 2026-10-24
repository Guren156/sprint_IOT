-- Banco LOCAL de demonstracao (SQLite), usado so quando o Oracle nao esta
-- configurado no .env. Mesmas tabelas e dados do Oracle da FIAP
-- (script de BD da Sprint 4 + 01_oracle_ia.sql).

CREATE TABLE T_CLY_CLINICA (
    id_clinica   INTEGER PRIMARY KEY,
    nome_clinica TEXT NOT NULL,
    nmr_cnpj     TEXT NOT NULL,
    endereco     TEXT NOT NULL,
    telefone     TEXT NOT NULL
);

CREATE TABLE T_CLY_RESPONSAVEL (
    id_usuario   INTEGER PRIMARY KEY,
    nome_usuario TEXT NOT NULL,
    email        TEXT NOT NULL,
    senha        TEXT NOT NULL,
    telefone     TEXT NOT NULL
);

CREATE TABLE T_CLY_PETS (
    T_CLY_RESPONSAVEL_id_usuario INTEGER NOT NULL,
    id_pet                       INTEGER PRIMARY KEY,
    nome_pet                     TEXT NOT NULL,
    especie                      TEXT NOT NULL,
    raca                         TEXT NOT NULL,
    dt_nascimento                TEXT NOT NULL,
    peso                         REAL,
    T_CLY_CLINICA_id_clinica     INTEGER NOT NULL
);

CREATE TABLE T_CLY_HISTORICO_SAUDE (
    T_CLY_PETS_id_pet INTEGER NOT NULL,
    id_registro       INTEGER PRIMARY KEY,
    tipo_registro     TEXT NOT NULL,
    detalhes          TEXT,
    dt_evento         TEXT NOT NULL
);

CREATE TABLE T_CLY_INTERACAO_IA (
    id_interacao                 INTEGER PRIMARY KEY AUTOINCREMENT,
    T_CLY_PETS_id_pet            INTEGER NOT NULL,
    T_CLY_RESPONSAVEL_id_usuario INTEGER NOT NULL,
    tipo                         TEXT NOT NULL,
    pergunta                     TEXT NOT NULL,
    resposta                     TEXT,
    nivel_urgencia               TEXT,
    modo_ia                      TEXT NOT NULL,
    dt_interacao                 TEXT NOT NULL
);

INSERT INTO T_CLY_CLINICA VALUES (10, 'Clyvo Vet Centro',     '12.345.678/0001-99', 'Av Paulista, 1000',       '(11) 99999-1111');
INSERT INTO T_CLY_CLINICA VALUES (20, 'Clyvo Vet Zona Sul',   '12.345.678/0002-88', 'Av Santo Amaro, 2000',    '(11) 99999-2222');
INSERT INTO T_CLY_CLINICA VALUES (30, 'Clyvo Vet Zona Norte', '12.345.678/0003-77', 'Av Cruzeiro do Sul, 300', '(11) 99999-3333');
INSERT INTO T_CLY_CLINICA VALUES (40, 'Clyvo Vet Zona Leste', '12.345.678/0004-66', 'Av Aricanduva, 400',      '(11) 99999-4444');
INSERT INTO T_CLY_CLINICA VALUES (50, 'Clyvo Vet Zona Oeste', '12.345.678/0005-55', 'Av Sumare, 500',          '(11) 99999-5555');

INSERT INTO T_CLY_RESPONSAVEL VALUES (1, 'Henrique',  'henrique@email.com', 'hash123', '(11) 98888-1111');
INSERT INTO T_CLY_RESPONSAVEL VALUES (2, 'Ana Clara', 'anaclara@email.com', 'hash456', '(11) 98888-2222');
INSERT INTO T_CLY_RESPONSAVEL VALUES (3, 'Isis',      'isis@email.com',     'hash789', '(11) 98888-3333');
INSERT INTO T_CLY_RESPONSAVEL VALUES (4, 'Pedro',     'pedro@email.com',    'hash101', '(11) 98888-4444');
INSERT INTO T_CLY_RESPONSAVEL VALUES (5, 'Rafael',    'rafael@email.com',   'hash112', '(11) 98888-5555');

INSERT INTO T_CLY_PETS VALUES (1, 101, 'Thor', 'Cao',  'Vira-lata', '2022-05-10', 15.4, 10);
INSERT INTO T_CLY_PETS VALUES (1, 102, 'Mel',  'Cao',  'Poodle',    '2021-08-20',  6.2, 10);
INSERT INTO T_CLY_PETS VALUES (1, 103, 'Tom',  'Gato', 'Siames',    '2023-01-15',  4.5, 20);
INSERT INTO T_CLY_PETS VALUES (2, 104, 'Nina', 'Cao',  'Labrador',  '2020-03-03', 28.0, 20);
INSERT INTO T_CLY_PETS VALUES (2, 105, 'Luna', 'Gato', 'Persa',     '2021-07-12',  3.8, 30);
INSERT INTO T_CLY_PETS VALUES (3, 106, 'Rex',  'Cao',  'Pastor',    '2019-02-25', 32.5, 40);
INSERT INTO T_CLY_PETS VALUES (4, 107, 'Bidu', 'Cao',  'Vira-lata', '2022-09-30', 12.0, 50);

INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (101, 1, 'Vacinacao', 'V10 aplicada',              '2023-06-15');
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (101, 2, 'Consulta',  'Check-up anual - saudavel', '2024-01-10');
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 3, 'Vacinacao', 'Antirrabica aplicada',      '2023-09-22');
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 4, 'Exame',     'Hemograma - normal',        '2024-03-05');
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 5, 'Cirurgia',  'Castracao realizada',       '2023-11-18');

INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (101, 1001, 'Vacinacao', 'V10 - reforco anual',                         date('now', '-355 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (101, 1002, 'Vacinacao', 'Antirrabica aplicada',                        date('now', '-200 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 1003, 'Vacinacao', 'V10 aplicada',                                date('now', '-400 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 1004, 'Consulta',  'Otite no ouvido esquerdo',                    date('now', '-3 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 1005, 'Medicacao', 'Amoxicilina 250mg de 12/12h por 10 dias',     date('now', '-3 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 1006, 'Vacinacao', 'V4 felina aplicada',                          date('now', '-30 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 1007, 'Vacinacao', 'Antirrabica aplicada',                        date('now', '-30 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 1008, 'Exame',     'Hemograma - normal',                          date('now', '-60 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 1009, 'Consulta',  'Displasia leve de quadril - controlar peso',  date('now', '-90 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 1010, 'Medicacao', 'Condroitina 1 comprimido/dia (uso continuo)', date('now', '-90 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 1011, 'Vacinacao', 'V10 aplicada',                                date('now', '-120 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (105, 1012, 'Vacinacao', 'Antirrabica aplicada',                        date('now', '-360 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (106, 1013, 'Consulta',  'Check-up - artrose inicial',                  date('now', '-200 days'));
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (106, 1014, 'Vacinacao', 'V10 aplicada',                                date('now', '-200 days'));
