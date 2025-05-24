CREATE TABLE SILOS (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Identificador único do silo
    nome_produto VARCHAR2(100),                         -- Nome do produto
    tipo_produto INTEGER,                               -- Tipo do produto (milho: 1, arroz: 2...)
    quantidade FLOAT,                                   -- Quantidade do produto em toneladas
    silo_nome VARCHAR2(100),                            -- Nome do silo      
    endereco VARCHAR2(255),                             -- Localização do silo
    capacidade FLOAT,                                   -- Capacidade total do silo em toneladas
    data_hora_registro DATE,                            -- Momento em que foi cadastrado
    umidade FLOAT,                                      -- Nível de umidade no silo
    temperatura FLOAT,                                  -- Temperatura do silo
    ph FLOAT,                                           -- PH do silo
    observacoes CLOB                                    -- Observações adicionais
)