-- Gerado por Oracle SQL Developer Data Modeler 23.1.0.087.0806
--   em:        2024-10-14 17:36:42 BRT
--   site:      Oracle Database 21c
--   tipo:      Oracle Database 21c



DROP TABLE area_cultivo CASCADE CONSTRAINTS;

DROP TABLE previsao_ajuste CASCADE CONSTRAINTS;

DROP TABLE reg_aplicacao_insumo CASCADE CONSTRAINTS;

DROP TABLE reg_leitura_sensor CASCADE CONSTRAINTS;

DROP TABLE sensor CASCADE CONSTRAINTS;

DROP TABLE tipo_cultura CASCADE CONSTRAINTS;

DROP TABLE tipo_insumo CASCADE CONSTRAINTS;

-- predefined type, no DDL - MDSYS.SDO_GEOMETRY

-- predefined type, no DDL - XMLTYPE

CREATE TABLE area_cultivo (
    id_area         NUMBER(5) NOT NULL,
    id_cultura      NUMBER(5) NOT NULL,
    area_extensao   NUMBER(20, 2) NOT NULL,
    end_localizacao VARCHAR2(255)
);

ALTER TABLE area_cultivo ADD CONSTRAINT pk_area_cultivo PRIMARY KEY ( id_area );

CREATE TABLE previsao_ajuste (
    id_previsao      NUMBER(5) NOT NULL,
    id_area          NUMBER(5) NOT NULL,
    id_insumo        NUMBER(5) NOT NULL,
    data_ajuste      DATE NOT NULL,
    acao_recomendada VARCHAR2(255) NOT NULL,
    quantidade       NUMBER(10, 2) NOT NULL,
    unidade_qtd      CHAR(10) NOT NULL
);

ALTER TABLE previsao_ajuste
    ADD CONSTRAINT pk_previsao_ajuste PRIMARY KEY ( id_previsao,
                                                    id_area,
                                                    id_insumo );

CREATE TABLE reg_aplicacao_insumo (
    id_aplic_insumo NUMBER(5) NOT NULL,
    id_area         NUMBER(5) NOT NULL,
    id_insumo       NUMBER(5) NOT NULL,
    data_aplicacao  DATE NOT NULL,
    quantidade      NUMBER(10, 2) NOT NULL,
    unidade_qtd     CHAR(10) NOT NULL
);

ALTER TABLE reg_aplicacao_insumo
    ADD CONSTRAINT pk_reg_aplicacao_insumo PRIMARY KEY ( id_aplic_insumo,
                                                         id_area,
                                                         id_insumo );

CREATE TABLE reg_leitura_sensor (
    id_leitura      NUMBER(5) NOT NULL,
    id_area         NUMBER(5) NOT NULL,
    id_sensor       NUMBER(5) NOT NULL,
    data_leitura    DATE NOT NULL,
    valor_leitura   NUMBER(10, 5) NOT NULL,
    unidade_leitura CHAR(10) NOT NULL
);

ALTER TABLE reg_leitura_sensor
    ADD CONSTRAINT pk_reg_leitura_sensor PRIMARY KEY ( id_leitura,
                                                       id_area,
                                                       id_sensor );

CREATE TABLE sensor (
    id_sensor NUMBER(5) NOT NULL,
    id_area   NUMBER(5) NOT NULL,
    descricao VARCHAR2(255),
    tipo      VARCHAR2(50) NOT NULL,
    modelo    VARCHAR2(100)
);

ALTER TABLE sensor ADD CONSTRAINT pk_sensor PRIMARY KEY ( id_sensor );

CREATE TABLE tipo_cultura (
    id_cultura   NUMBER(5) NOT NULL,
    nome         VARCHAR2(100) NOT NULL,
    data_plantio DATE NOT NULL
);

ALTER TABLE tipo_cultura ADD CONSTRAINT pk_tipo_cultura PRIMARY KEY ( id_cultura );

CREATE TABLE tipo_insumo (
    id_insumo NUMBER(5) NOT NULL,
    nome      VARCHAR2(100) NOT NULL,
    descricao VARCHAR2(255)
);

ALTER TABLE tipo_insumo ADD CONSTRAINT pk_tipo_insumo PRIMARY KEY ( id_insumo );

ALTER TABLE area_cultivo
    ADD CONSTRAINT fk_area_cultivo_tipo_cultura FOREIGN KEY ( id_cultura )
        REFERENCES tipo_cultura ( id_cultura );

ALTER TABLE previsao_ajuste
    ADD CONSTRAINT fk_previsao_ajuste_area_cultivo FOREIGN KEY ( id_area )
        REFERENCES area_cultivo ( id_area );

ALTER TABLE previsao_ajuste
    ADD CONSTRAINT fk_previsao_ajuste_tipo_insumo FOREIGN KEY ( id_insumo )
        REFERENCES tipo_insumo ( id_insumo );

ALTER TABLE reg_aplicacao_insumo
    ADD CONSTRAINT fk_reg_aplicacao_insumo_area_cultivo FOREIGN KEY ( id_area )
        REFERENCES area_cultivo ( id_area );

ALTER TABLE reg_aplicacao_insumo
    ADD CONSTRAINT fk_reg_aplicacao_insumo_tipo_insumo FOREIGN KEY ( id_insumo )
        REFERENCES tipo_insumo ( id_insumo );

ALTER TABLE reg_leitura_sensor
    ADD CONSTRAINT fk_reg_leitura_sensor_area_cultivo FOREIGN KEY ( id_area )
        REFERENCES area_cultivo ( id_area );

ALTER TABLE reg_leitura_sensor
    ADD CONSTRAINT fk_reg_leitura_sensor_sensor FOREIGN KEY ( id_sensor )
        REFERENCES sensor ( id_sensor );

ALTER TABLE sensor
    ADD CONSTRAINT fk_sensor_area_cultivo FOREIGN KEY ( id_area )
        REFERENCES area_cultivo ( id_area );



-- Relatório do Resumo do Oracle SQL Developer Data Modeler: 
-- 
-- CREATE TABLE                             7
-- CREATE INDEX                             0
-- ALTER TABLE                             15
-- CREATE VIEW                              0
-- ALTER VIEW                               0
-- CREATE PACKAGE                           0
-- CREATE PACKAGE BODY                      0
-- CREATE PROCEDURE                         0
-- CREATE FUNCTION                          0
-- CREATE TRIGGER                           0
-- ALTER TRIGGER                            0
-- CREATE COLLECTION TYPE                   0
-- CREATE STRUCTURED TYPE                   0
-- CREATE STRUCTURED TYPE BODY              0
-- CREATE CLUSTER                           0
-- CREATE CONTEXT                           0
-- CREATE DATABASE                          0
-- CREATE DIMENSION                         0
-- CREATE DIRECTORY                         0
-- CREATE DISK GROUP                        0
-- CREATE ROLE                              0
-- CREATE ROLLBACK SEGMENT                  0
-- CREATE SEQUENCE                          0
-- CREATE MATERIALIZED VIEW                 0
-- CREATE MATERIALIZED VIEW LOG             0
-- CREATE SYNONYM                           0
-- CREATE TABLESPACE                        0
-- CREATE USER                              0
-- 
-- DROP TABLESPACE                          0
-- DROP DATABASE                            0
-- 
-- REDACTION POLICY                         0
-- 
-- ORDS DROP SCHEMA                         0
-- ORDS ENABLE SCHEMA                       0
-- ORDS ENABLE OBJECT                       0
-- 
-- ERRORS                                   0
-- WARNINGS                                 0
