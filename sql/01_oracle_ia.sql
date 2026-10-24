-- CLYVO VET - SPRINT 4 - COMPONENTE DE IA
-- Disciplina: Disruptive Architectures: IoT, IoB & Generative IA
--
-- Rodar no SQL Developer DEPOIS do script de Banco de Dados
-- (2TDSR_2024_CodigoSql_Integrantes.sql), com o mesmo usuario Oracle.
-- Cria a tabela de log das interacoes com a IA e insere historico de
-- saude recente (datas relativas a SYSDATE) para a IA ter o que analisar.


-- 1) LIMPEZA (ignora "objeto nao existe")
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE T_CLY_INTERACAO_IA CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        NULL;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP SEQUENCE SEQ_CLY_INTERACAO_IA';
EXCEPTION
    WHEN OTHERS THEN
        NULL;
END;
/


-- 2) TABELA DE INTERACOES COM A IA (auditoria + personalizacao)
CREATE TABLE T_CLY_INTERACAO_IA (
    id_interacao                 NUMBER(10)          NOT NULL,
    T_CLY_PETS_id_pet            NUMBER(10)          NOT NULL,
    T_CLY_RESPONSAVEL_id_usuario NUMBER(10)          NOT NULL,
    tipo                         VARCHAR2(10)        NOT NULL,
    pergunta                     VARCHAR2(1000 CHAR) NOT NULL,
    resposta                     VARCHAR2(2000 CHAR),
    nivel_urgencia               VARCHAR2(10),
    modo_ia                      VARCHAR2(20)        NOT NULL,
    dt_interacao                 DATE                NOT NULL
);
ALTER TABLE T_CLY_INTERACAO_IA ADD CONSTRAINT T_CLY_INTERACAO_IA_PK PRIMARY KEY (id_interacao);
ALTER TABLE T_CLY_INTERACAO_IA ADD CONSTRAINT T_CLY_INTERACAO_IA_CK_TIPO CHECK (tipo IN ('CHAT', 'TRIAGEM'));
ALTER TABLE T_CLY_INTERACAO_IA ADD CONSTRAINT FK_INTERACAO_PETS
    FOREIGN KEY (T_CLY_PETS_id_pet) REFERENCES T_CLY_PETS (id_pet);
ALTER TABLE T_CLY_INTERACAO_IA ADD CONSTRAINT FK_INTERACAO_RESP
    FOREIGN KEY (T_CLY_RESPONSAVEL_id_usuario) REFERENCES T_CLY_RESPONSAVEL (id_usuario);

CREATE SEQUENCE SEQ_CLY_INTERACAO_IA START WITH 1 INCREMENT BY 1;


-- 3) HISTORICO DE SAUDE RECENTE (ids 1001+ para nao conflitar)
DELETE FROM T_CLY_HISTORICO_SAUDE WHERE id_registro BETWEEN 1001 AND 1099;

-- Thor (101): V10 vence em ~10 dias, check-up atrasado
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (101, 1001, 'Vacinacao', 'V10 - reforco anual',             SYSDATE - 355);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (101, 1002, 'Vacinacao', 'Antirrabica aplicada',            SYSDATE - 200);
-- Mel (102): em tratamento de otite, V10 vencida
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 1003, 'Vacinacao', 'V10 aplicada',                    SYSDATE - 400);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 1004, 'Consulta',  'Otite no ouvido esquerdo',        SYSDATE - 3);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (102, 1005, 'Medicacao', 'Amoxicilina 250mg de 12/12h por 10 dias', SYSDATE - 3);
-- Tom (103): tudo em dia
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 1006, 'Vacinacao', 'V4 felina aplicada',              SYSDATE - 30);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 1007, 'Vacinacao', 'Antirrabica aplicada',            SYSDATE - 30);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (103, 1008, 'Exame',     'Hemograma - normal',              SYSDATE - 60);
-- Nina (104): displasia, medicacao de uso continuo
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 1009, 'Consulta',  'Displasia leve de quadril - controlar peso', SYSDATE - 90);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 1010, 'Medicacao', 'Condroitina 1 comprimido/dia (uso continuo)', SYSDATE - 90);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (104, 1011, 'Vacinacao', 'V10 aplicada',                    SYSDATE - 120);
-- Luna (105): antirrabica vence em ~5 dias
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (105, 1012, 'Vacinacao', 'Antirrabica aplicada',            SYSDATE - 360);
-- Rex (106): pet idoso (7 anos), check-up semestral
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (106, 1013, 'Consulta',  'Check-up - artrose inicial',      SYSDATE - 200);
INSERT INTO T_CLY_HISTORICO_SAUDE VALUES (106, 1014, 'Vacinacao', 'V10 aplicada',                    SYSDATE - 200);

COMMIT;


-- 4) CONFERENCIA
SELECT p.nome_pet, h.tipo_registro, h.detalhes, h.dt_evento
  FROM T_CLY_HISTORICO_SAUDE h
  JOIN T_CLY_PETS p ON p.id_pet = h.T_CLY_PETS_id_pet
 ORDER BY p.id_pet, h.dt_evento;

-- Depois de usar o assistente, as interacoes ficam aqui:
-- SELECT * FROM T_CLY_INTERACAO_IA ORDER BY id_interacao DESC;
