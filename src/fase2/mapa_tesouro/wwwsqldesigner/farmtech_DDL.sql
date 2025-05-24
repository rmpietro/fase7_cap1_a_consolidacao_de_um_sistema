/*
ALTER TABLE AREA_CULTIVO DROP CONSTRAINT FK_AREA_CULTIVO_TIPO_CULTURA;
ALTER TABLE PREVISAO_AJUSTE DROP CONSTRAINT FK_EVISAO_AJUSTE_AREA_CULTIVO;
ALTER TABLE PREVISAO_AJUSTE DROP CONSTRAINT FK_EVISAO_AJUSTE_TIPO_INSUMO;
ALTER TABLE REG_APLICACAO_INSUMO DROP CONSTRAINT FK_ICACAO_INSUMO_AREA_CULTIVO;
ALTER TABLE REG_APLICACAO_INSUMO DROP CONSTRAINT FK_ICACAO_INSUMO_TIPO_INSUMO;
ALTER TABLE REG_LEITURA_SENSOR DROP CONSTRAINT FK_EITURA_SENSOR_AREA_CULTIVO;
ALTER TABLE REG_LEITURA_SENSOR DROP CONSTRAINT FK_EITURA_SENSOR_SENSOR;
ALTER TABLE SENSOR DROP CONSTRAINT FK_SENSOR_AREA_CULTIVO;
DROP TABLE AREA_CULTIVO PURGE;
DROP SEQUENCE SQ_AREA_CULTIVO;
DROP TABLE PREVISAO_AJUSTE PURGE;
DROP SEQUENCE SQ_PREVISAO_AJUSTE;
DROP TABLE TIPO_INSUMO PURGE;
DROP SEQUENCE SQ_TIPO_INSUMO;
DROP TABLE REG_APLICACAO_INSUMO PURGE;
DROP SEQUENCE SQ_REG_APLICACAO_INSUMO;
DROP TABLE REG_LEITURA_SENSOR PURGE;
DROP SEQUENCE SQ_REG_LEITURA_SENSOR;
DROP TABLE SENSOR PURGE;
DROP SEQUENCE SQ_SENSOR;
DROP TABLE TIPO_CULTURA PURGE;
DROP SEQUENCE SQ_TIPO_CULTURA;
-- */

-------------------------------------------------------------------------------
--            AREA_CULTIVO
-------------------------------------------------------------------------------

CREATE TABLE AREA_CULTIVO (
    "id_area"                         NUMBER(5)           NOT NULL
  , "area_extensao"                   NUMBER(15)          NOT NULL
  , "end_localizacao"                 VARCHAR2(255)
  , "id_cultura"                      NUMBER(5)
  , CONSTRAINT PK_AREA_CULTIVO PRIMARY KEY ( "id_area" )
  , CONSTRAINT KK_2 ??INDEX?? (  )
);

COMMENT ON TABLE  AREA_CULTIVO                                 IS 'Armazena e gera as áreas de plantio para cada cultura de forma a localizar os
            sensores atuantes, recomendações e previsões de aplicação de água e nutrientes.';

CREATE SEQUENCE SQ_AREA_CULTIVO;

CREATE OR REPLACE TRIGGER TG_AREA_CULTIVO_BI
    BEFORE INSERT ON AREA_CULTIVO
    FOR EACH ROW
BEGIN
    if :NEW."id_area" is NULL then
        :NEW."id_area" := SQ_AREA_CULTIVO.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------
--            PREVISAO_AJUSTE
-------------------------------------------------------------------------------

CREATE TABLE PREVISAO_AJUSTE (
    "id_previsao"                     NUMBER(5)           NOT NULL
  , "data_ajuste"                     DATE                NOT NULL
  , "acao_recomendada"                VARCHAR2(255)       NOT NULL
  , "quantidade"                      NUMBER(10,2)        NOT NULL
  , "unidade_qtd"                     CHAR(10)            NOT NULL
  , "id_area"                         NUMBER(5)           NOT NULL
  , "id_insumo"                       NUMBER(5)           NOT NULL
  , CONSTRAINT PK_PREVISAO_AJUSTE PRIMARY KEY ( "id_previsao" )
);

COMMENT ON TABLE  PREVISAO_AJUSTE                                 IS 'Registra previsões e ajustes para aplicação de insumos em áreas específicas. Essas
            previsões podem ser aplicações de insumos imediatos ou para uma data futura.';

CREATE SEQUENCE SQ_PREVISAO_AJUSTE;

CREATE OR REPLACE TRIGGER TG_PREVISAO_AJUSTE_BI
    BEFORE INSERT ON PREVISAO_AJUSTE
    FOR EACH ROW
BEGIN
    if :NEW."id_previsao" is NULL then
        :NEW."id_previsao" := SQ_PREVISAO_AJUSTE.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------
--            TIPO_INSUMO
-------------------------------------------------------------------------------

CREATE TABLE TIPO_INSUMO (
    "id_insumo"                       NUMBER(5)           NOT NULL
  , "nome"                            VARCHAR2(100)       NOT NULL
  , "descricao"                       VARCHAR2(255)
  , CONSTRAINT PK_TIPO_INSUMO PRIMARY KEY ( "id_insumo" )
);

COMMENT ON TABLE  TIPO_INSUMO                                 IS 'Lista os diferentes tipos de insumos utilizados no cultivo e que são alvo de
            recomendações e previsões para ajustes nas diferentes culturas.';

CREATE SEQUENCE SQ_TIPO_INSUMO;

CREATE OR REPLACE TRIGGER TG_TIPO_INSUMO_BI
    BEFORE INSERT ON TIPO_INSUMO
    FOR EACH ROW
BEGIN
    if :NEW."id_insumo" is NULL then
        :NEW."id_insumo" := SQ_TIPO_INSUMO.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------
--            REG_APLICACAO_INSUMO
-------------------------------------------------------------------------------

CREATE TABLE REG_APLICACAO_INSUMO (
    "id_aplic_insumo"                 NUMBER(5)           NOT NULL
  , "data_aplicacao"                  DATE                NOT NULL
  , "quantidade"                      NUMBER(10,2)        NOT NULL
  , "unidade_qtd"                     CHAR(10)            NOT NULL
  , "id_area"                         NUMBER(5)           NOT NULL
  , "id_insumo"                       NUMBER(5)           NOT NULL
  , CONSTRAINT PK_REG_APLICACAO_INSUMO PRIMARY KEY ( "id_aplic_insumo" )
);

COMMENT ON TABLE  REG_APLICACAO_INSUMO                                 IS 'Registra as aplicações efetivas de insumos nas áreas de cultivo.';

CREATE SEQUENCE SQ_REG_APLICACAO_INSUMO;

CREATE OR REPLACE TRIGGER TG_REG_APLICACAO_INSUMO_BI
    BEFORE INSERT ON REG_APLICACAO_INSUMO
    FOR EACH ROW
BEGIN
    if :NEW."id_aplic_insumo" is NULL then
        :NEW."id_aplic_insumo" := SQ_REG_APLICACAO_INSUMO.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------
--            REG_LEITURA_SENSOR
-------------------------------------------------------------------------------

CREATE TABLE REG_LEITURA_SENSOR (
    "id_leitura"                      NUMBER(5)           NOT NULL
  , "data_leitura"                    DATE                NOT NULL
  , "valor_leitura"                   NUMBER(10,5)        NOT NULL
  , "unidade_leitura"                 CHAR(10)            NOT NULL
  , "id_area"                         NUMBER(5)           NOT NULL
  , "id_sensor"                       NUMBER(5)           NOT NULL
  , CONSTRAINT PK_REG_LEITURA_SENSOR PRIMARY KEY ( "id_leitura" )
);

COMMENT ON TABLE  REG_LEITURA_SENSOR                                 IS 'Armazena as leituras realizadas pelos sensores nas áreas de cultivo.';

CREATE SEQUENCE SQ_REG_LEITURA_SENSOR;

CREATE OR REPLACE TRIGGER TG_REG_LEITURA_SENSOR_BI
    BEFORE INSERT ON REG_LEITURA_SENSOR
    FOR EACH ROW
BEGIN
    if :NEW."id_leitura" is NULL then
        :NEW."id_leitura" := SQ_REG_LEITURA_SENSOR.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------
--            SENSOR
-------------------------------------------------------------------------------

CREATE TABLE SENSOR (
    "id_sensor"                       NUMBER(5)           NOT NULL
  , "descricao"                       VARCHAR2(255)
  , "tipo"                            VARCHAR2(50)        NOT NULL
  , "modelo"                          VARCHAR2(100)
  , "id_area"                         NUMBER(5)           NOT NULL
  , CONSTRAINT PK_SENSOR PRIMARY KEY ( "id_sensor" )
);

COMMENT ON TABLE  SENSOR                                 IS 'Contém informações sobre os sensores utilizados para monitoramento das áreas de
            cultivo.';

CREATE SEQUENCE SQ_SENSOR;

CREATE OR REPLACE TRIGGER TG_SENSOR_BI
    BEFORE INSERT ON SENSOR
    FOR EACH ROW
BEGIN
    if :NEW."id_sensor" is NULL then
        :NEW."id_sensor" := SQ_SENSOR.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------
--            TIPO_CULTURA
-------------------------------------------------------------------------------

CREATE TABLE TIPO_CULTURA (
    "id_cultura"                      NUMBER(5)           NOT NULL
  , "nome"                            VARCHAR2(100)       DEFAULT 'NULL'       NOT NULL
  , "data_plantio"                    DATE                NOT NULL
  , CONSTRAINT PK_TIPO_CULTURA PRIMARY KEY ( "id_cultura" )
);

COMMENT ON TABLE  TIPO_CULTURA                                 IS 'Gerencia a lista de culturas plantadas que será associada ''a área de cultivo e seus
            sensores.';

CREATE SEQUENCE SQ_TIPO_CULTURA;

CREATE OR REPLACE TRIGGER TG_TIPO_CULTURA_BI
    BEFORE INSERT ON TIPO_CULTURA
    FOR EACH ROW
BEGIN
    if :NEW."id_cultura" is NULL then
        :NEW."id_cultura" := SQ_TIPO_CULTURA.nextVal;
    end if;
END;
/

SHOW ERRORS;

-------------------------------------------------------------------------------

ALTER TABLE AREA_CULTIVO ADD CONSTRAINT FK_AREA_CULTIVO_TIPO_CULTURA FOREIGN KEY ( "id_cultura" ) REFERENCES TIPO_CULTURA ( "id_cultura" );
ALTER TABLE PREVISAO_AJUSTE ADD CONSTRAINT FK_EVISAO_AJUSTE_AREA_CULTIVO FOREIGN KEY ( "id_area" ) REFERENCES AREA_CULTIVO ( "id_area" );
ALTER TABLE PREVISAO_AJUSTE ADD CONSTRAINT FK_EVISAO_AJUSTE_TIPO_INSUMO FOREIGN KEY ( "id_insumo" ) REFERENCES TIPO_INSUMO ( "id_insumo" );
ALTER TABLE REG_APLICACAO_INSUMO ADD CONSTRAINT FK_ICACAO_INSUMO_AREA_CULTIVO FOREIGN KEY ( "id_area" ) REFERENCES AREA_CULTIVO ( "id_area" );
ALTER TABLE REG_APLICACAO_INSUMO ADD CONSTRAINT FK_ICACAO_INSUMO_TIPO_INSUMO FOREIGN KEY ( "id_insumo" ) REFERENCES TIPO_INSUMO ( "id_insumo" );
ALTER TABLE REG_LEITURA_SENSOR ADD CONSTRAINT FK_EITURA_SENSOR_AREA_CULTIVO FOREIGN KEY ( "id_area" ) REFERENCES AREA_CULTIVO ( "id_area" );
ALTER TABLE REG_LEITURA_SENSOR ADD CONSTRAINT FK_EITURA_SENSOR_SENSOR FOREIGN KEY ( "id_sensor" ) REFERENCES SENSOR ( "id_sensor" );
ALTER TABLE SENSOR ADD CONSTRAINT FK_SENSOR_AREA_CULTIVO FOREIGN KEY ( "id_area" ) REFERENCES AREA_CULTIVO ( "id_area" );