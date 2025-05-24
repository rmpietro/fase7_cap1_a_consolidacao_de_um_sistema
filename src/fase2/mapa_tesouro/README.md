# Farm Tech - Documentação do Modelo de Dados

## Visão Geral

Projeto de modelagem de dados para um sistema de armazenamento (banco de dados) e análise dos dados coletados por sensores agrícolas com o fim de prover informação, recomendação de ajustes imediatos ou previsões futuras na quantidade de insumos (incluindo água) aplicados na plantação.

## Observações importantes

Nosso grupo incluiu as versões do DER, Scripts SQL DDL e imagem do diagrama **tanto para o Oracle SQL DataModeler quanto para a ferramenta solicitada no enunciado do trabalho, o SQLDesigner**, disponível no link compartilhado. Estão em pastas individuais no repositório.

## MER - Entidades

### TIPO_CULTURA

Armazena informações sobre os diferentes tipos de culturas geridas pelo modelo.

| Campo        | Tipo         | Opcional? | Descrição                              |
| ------------ | ------------ | --------- | -------------------------------------- |
| id_cultura   | NUMERIC(6)   | Não       | Identificador único do tipo de cultura |
| nome         | VARCHAR(100) | Não       | Nome da cultura                        |
| data_plantio | Date         | Não       | Data de plantio da cultura             |

### AREA_CULTIVO

Contém dados sobre as áreas específicas (com extensão e localização) de cada cultura e sob observação de um ou mais sensores (a mesma cultura pode ter várias áreas atribuídas e vários sensores instalados).

| Campo           | Tipo          | Opcional? | Descrição                                  |
| --------------- | ------------- | --------- | ------------------------------------------ |
| id_area         | NUMERIC(6)    | Não       | Identificador único da área de cultivo     |
| id_cultura      | NUMERIC(6)    | Não       | Referência ao tipo de cultura cultivada    |
| area_extensao   | NUMERIC(20,2) | Não       | Extensão da área de cultivo                |
| end_localizacao | VARCHAR(255)  | Sim       | Endereço ou localização da área de cultivo |

### TIPO_INSUMO

Lista os diferentes tipos de insumos utilizados no cultivo e que são alvo de recomendações e previsões para ajustes nas diferentes culturas.

| Campo     | Tipo         | Opcional? | Descrição                             |
| --------- | ------------ | --------- | ------------------------------------- |
| id_insumo | NUMERIC(6)   | Não       | Identificador único do tipo de insumo |
| nome      | VARCHAR(100) | Não       | Nome do insumo                        |
| descricao | VARCHAR(255) | Sim       | Descrição detalhada do insumo         |

### PREVISAO_AJUSTE

Registra previsões e ajustes para aplicação de insumos em áreas específicas. Essas previsões podem ser aplicações de insumos imediatos ou para uma data futura.

| Campo            | Tipo          | Opcional? | Descrição                              |
| ---------------- | ------------- | --------- | -------------------------------------- |
| id_previsao      | NUMERIC(6)    | Não       | Identificador único da previsão/ajuste |
| id_area          | NUMERIC(6)    | Não       | Referência à área de cultivo           |
| id_insumo        | NUMERIC(6)    | Não       | Referência ao tipo de insumo           |
| data_ajuste      | Date          | Não       | Data do ajuste ou previsão             |
| acao_recomendada | VARCHAR(255)  | Sim       | Descrição da ação recomendada          |
| quantidade       | NUMERIC(10,2) | Não       | Quantidade de insumo prevista/ajustada |
| unidade_qtd      | CHAR(10)      | Não       | Unidade de medida da quantidade        |

### REG_APLICACAO_INSUMO

Registra as aplicações efetivas de insumos nas áreas de cultivo.

| Campo           | Tipo          | Opcional? | Descrição                                  |
| --------------- | ------------- | --------- | ------------------------------------------ |
| id_aplic_insumo | NUMERIC(6)    | Não       | Identificador único da aplicação de insumo |
| id_area         | NUMERIC(6)    | Não       | Referência à área de cultivo               |
| id_insumo       | NUMERIC(6)    | Não       | Referência ao tipo de insumo aplicado      |
| data_aplicacao  | Date          | Não       | Data da aplicação do insumo                |
| quantidade      | NUMERIC(10,2) | Não       | Quantidade de insumo aplicada              |
| unidade_qtd     | CHAR(10)      | Não       | Unidade de medida da quantidade aplicada   |

### SENSOR

Contém informações sobre os sensores utilizados para monitoramento das áreas de cultivo.

| Campo     | Tipo         | Opcional? | Descrição                     |
| --------- | ------------ | --------- | ----------------------------- |
| id_sensor | NUMERIC(6)   | Não       | Identificador único do sensor |
| id_area   | NUMERIC(6)   | Não       | Referência à área monitorada  |
| descricao | VARCHAR(255) | Sim       | Descrição do sensor           |
| tipo      | VARCHAR(50)  | Não       | Tipo de sensor                |
| modelo    | VARCHAR(100) | Sim       | Modelo do sensor              |

### REG_LEITURA_SENSOR

Armazena as leituras realizadas pelos sensores nas áreas de cultivo.

| Campo           | Tipo          | Opcional? | Descrição                      |
| --------------- | ------------- | --------- | ------------------------------ |
| id_leitura      | NUMERIC(6)    | Não       | Identificador único da leitura |
| id_area         | NUMERIC(6)    | Não       | Referência à área monitorada   |
| id_sensor       | NUMERIC(6)    | Não       | Referência ao sensor utilizado |
| data_leitura    | Date          | Não       | Data da leitura                |
| valor_leitura   | NUMERIC(10,5) | Não       | Valor registrado na leitura    |
| unidade_leitura | CHAR(10)      | Não       | Unidade de medida da leitura   |

## Relacionamentos

1. TIPO_CULTURA (1) -> (N) AREA_CULTIVO

   - Uma cultura pode ser cultivada em várias áreas. Uma área de cultivo possui apenas 1 tipo de cultura.

2. AREA_CULTIVO (1) -> (N) REG_APLICACAO_INSUMO

   - Uma área pode receber múltiplas aplicações de insumos. Um registro de aplicação de insumo sempre refere-se a uma única área de cultivo

3. TIPO_INSUMO (1) -> (N) REG_APLICACAO_INSUMO

   - Um tipo de insumo pode ser aplicado várias vezes em diferentes áreas. Um registro de aplicação de insumo sempre refere-se a um único insumo aplicado (em uma determinada área de cultivo).

4. AREA_CULTIVO (1) -> (N) REG_LEITURA_SENSOR

   - Uma área pode ter múltiplas leituras de sensores. Um registro de leitura de sensor sempre refere-se a uma única área de cultivo específica.

5. SENSOR (1) -> (N) REG_LEITURA_SENSOR

   - Um sensor pode realizar várias leituras. Um registro de leitura de sensor sempre refere-se a um úni sensor , seu valor de leitura e unidade de medição.

6. AREA_CULTIVO (1) -> (N) SENSOR

   - Uma área pode ter vários sensores instalados. Um sensor específico só pode estar instalado em uma área específica de cultivo.

7. AREA_CULTIVO (1) -> (N) PREVISAO_AJUSTE

   - Uma área pode ter múltiplas previsões ou ajustes de insumos. Um registro de previsão de ajuste imediato ou recomendação futura somente pode se referir a uma única área de cultivo.

8. TIPO_INSUMO (1) -> (N) PREVISAO_AJUSTE
   - Um tipo de insumo pode estar associado a várias previsões ou ajustes. Um registro de previsão de ajuste imediato ou recomendação futura somente pode se referir a um único insumo (para uma dada área de cultivo).
