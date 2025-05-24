# Instalação e carregamento dos pacotes necessários
packages <- c("jsonlite", "tidyverse", "lubridate", "forecast",
              "tseries", "ggplot2", "gridExtra", "corrplot",
              "randomForest", "caret")

# Função para instalar/carregar pacotes
install_and_load <- function(packages) {
  new_packages <- packages[!(packages %in% installed.packages()[,"Package"])]
  if(length(new_packages)) install.packages(new_packages)
  invisible(lapply(packages, library, character.only = TRUE))
}

install_and_load(packages)
# Função para obter dados do arquivo JSON
get_data_from_json <- function(json_file_path) {
  # Ler o arquivo JSON
  dados_json <- fromJSON(json_file_path)
  
  # Extrair as leituras
  leituras <- dados_json$leituras[[1]] %>%
    as_tibble() %>%
    mutate(
      timestamp = ymd_hms(timestamp),
      data = date(timestamp),
      hora = hour(timestamp),
      P = factor(P),
      K = factor(K),
      irrigacao_status = factor(irrigacao$estado),
      irrigacao_num = ifelse(irrigacao_status == "ligada", 1, 0),
      sensor_tipo = "Sensor Combinado",  # Assumindo um tipo padrão
      end_localizacao = "Localização Padrão",  # Assumindo uma localização padrão
      cultura_nome = "Cultura Padrão"  # Assumindo uma cultura padrão
    ) %>%
    select(-irrigacao)  # Removendo a coluna irrigacao após extrair o estado
  
  return(leituras)
}


# Função principal para executar a análise
run_analysis <- function(json_file_path) {
  leituras <- get_data_from_json(json_file_path)
  
  # Análise exploratória dos dados
  analise_exploratoria <- function(dados) {
    # Estatísticas descritivas
    estat_desc <- dados %>%
      select(temp, humid, pH) %>%
      summary()
    
    # Correlação entre variáveis numéricas
    cor_matrix <- dados %>%
      select(temp, humid, pH) %>%
      cor()
    
    # Distribuição temporal das irrigações
    dist_irrigacao <- dados %>%
      group_by(data) %>%
      summarise(
        media_temp = mean(temp),
        media_humid = mean(humid),
        media_pH = mean(pH),
        irrigacao_necessaria = sum(irrigacao_num) > 0
      )
    
    return(list(
      estatisticas = estat_desc,
      correlacoes = cor_matrix,
      distribuicao = dist_irrigacao
    ))
  }
  
  # Visualizações
  criar_visualizacoes <- function(dados) {
    # 1. Série temporal das variáveis principais
    p1 <- ggplot(dados, aes(x = timestamp)) +
      geom_line(aes(y = temp, color = "Temperatura")) +
      geom_line(aes(y = humid, color = "Umidade")) +
      labs(title = "Série Temporal - Temperatura e Umidade",
           y = "Valor", color = "Variável") +
      theme_minimal()
    
    # 2. Relação entre temperatura e umidade, colorido por status de irrigação
    p2 <- ggplot(dados, aes(x = temp, y = humid, color = irrigacao_status)) +
      geom_point() +
      labs(title = "Relação Temperatura x Umidade",
           x = "Temperatura", y = "Umidade") +
      theme_minimal()
    
    # 3. Distribuição do pH por status de irrigação
    p3 <- ggplot(dados, aes(x = irrigacao_status, y = pH, fill = irrigacao_status)) +
      geom_boxplot() +
      labs(title = "Distribuição do pH por Status de Irrigação",
           x = "Status da Irrigação", y = "pH") +
      theme_minimal()
    
    # 4. Presença de nutrientes por status de irrigação
    p4 <- dados %>%
      gather(nutriente, status, P:K) %>%
      ggplot(aes(x = nutriente, fill = status)) +
      geom_bar(position = "dodge") +
      facet_wrap(~irrigacao_status) +
      labs(title = "Presença de Nutrientes por Status de Irrigação") +
      theme_minimal()
    
    grid.arrange(p1, p2, p3, p4, ncol = 2)
  }
  
  # Modelagem preditiva
  criar_modelo_predicao <- function(dados) {
    # Preparar dados para modelagem
    dados_modelo <- dados %>%
      select(temp, humid, pH, P, K, irrigacao_num) %>%
      mutate(
        # Garantir que irrigacao_num seja fator com níveis corretos
        irrigacao_num = factor(irrigacao_num, levels = c(0, 1))
      )
    
    # Divisão treino/teste
    set.seed(123)
    index <- createDataPartition(dados_modelo$irrigacao_num, p = 0.7, list = FALSE)
    treino <- dados_modelo[index, ]
    teste <- dados_modelo[-index, ]
    
    # Treinar modelo Random Forest
    modelo_rf <- randomForest(
      irrigacao_num ~ .,
      data = treino,
      ntree = 500,
      importance = TRUE
    )
    
    # Avaliar modelo
    predicoes <- predict(modelo_rf, teste)
    matriz_conf <- confusionMatrix(predicoes, teste$irrigacao_num)
    
    # Importância das variáveis
    importancia <- importance(modelo_rf)
    
    return(list(
      modelo = modelo_rf,
      avaliacao = matriz_conf,
      importancia = importancia
    ))
  }
  
  # [Código anterior permanece igual até a função visualizar_previsoes]
  
  # Visualização das previsões corrigida
  visualizar_previsoes <- function(previsoes) {
    # Garantir que os dados estão em formato data.frame
    previsoes_df <- as.data.frame(previsoes)
    
    # Criar gráfico com intervalos de confiança
    p1 <- ggplot(previsoes_df, aes(x = data)) +
      geom_ribbon(aes(ymin = temp_lower, ymax = temp_upper, fill = "Temperatura"), alpha = 0.2) +
      geom_line(aes(y = temp_prevista, color = "Temperatura")) +
      geom_ribbon(aes(ymin = humid_lower, ymax = humid_upper, fill = "Umidade"), alpha = 0.2) +
      geom_line(aes(y = humid_prevista, color = "Umidade")) +
      geom_line(aes(y = prob_irrigacao * 100, color = "Prob. Irrigação")) +
      scale_y_continuous(name = "Valor",
                         sec.axis = sec_axis(~./100, name = "Probabilidade de Irrigação")) +
      labs(title = "Previsões para os Próximos Dias",
           x = "Data",
           color = "Variável",
           fill = "Intervalo de Confiança") +
      theme_minimal() +
      theme(legend.position = "bottom")
    
    # Tabela de previsões formatada com conversão explícita de tipos
    previsoes_format <- previsoes_df %>%
      mutate(
        data = format(as.Date(data), "%d/%m/%Y"),
        prob_irrigacao = sprintf("%.1f%%", as.numeric(prob_irrigacao) * 100),
        temp_prevista = round(as.numeric(temp_prevista), 1),
        humid_prevista = round(as.numeric(humid_prevista), 1)
      ) %>%
      select(data, prob_irrigacao, temp_prevista, humid_prevista)
    
    # Criar tabela mais informativa
    previsoes_detalhadas <- previsoes_df %>%
      mutate(
        data = format(as.Date(data), "%d/%m/%Y"),
        prob_irrigacao = sprintf("%.1f%%", as.numeric(prob_irrigacao) * 100),
        temp_prevista = sprintf("%.1f (%.1f - %.1f)",
                                as.numeric(temp_prevista),
                                as.numeric(temp_lower),
                                as.numeric(temp_upper)),
        humid_prevista = sprintf("%.1f (%.1f - %.1f)",
                                 as.numeric(humid_prevista),
                                 as.numeric(humid_lower),
                                 as.numeric(humid_upper))
      ) %>%
      select(data, prob_irrigacao, temp_prevista, humid_prevista)
    
    # Exibir resultados
    print(p1)
    cat("\nTabela de Previsões (com intervalos de confiança):\n")
    print(knitr::kable(previsoes_detalhadas,
                       col.names = c("Data",
                                     "Prob. Irrigação",
                                     "Temperatura (IC)",
                                     "Umidade (IC)"),
                       align = c('l', 'r', 'r', 'r')))
  }
  
  # Função de previsão atualizada para garantir tipos de dados corretos
  prever_proximos_dias <- function(dados, n_dias = 7) {
    # Preparar série temporal de irrigação diária
    serie_diaria <- dados %>%
      group_by(data) %>%
      summarise(
        irrigacao = max(as.numeric(irrigacao_num)),
        media_temp = mean(temp),
        media_humid = mean(humid),
        media_pH = mean(pH)
      ) %>%
      ungroup()
    
    # Verificar se há dados suficientes
    if(nrow(serie_diaria) < 3) {
      stop("Necessário pelo menos 3 dias de dados para fazer previsões")
    }
    
    # Criar séries temporais com tratamento de erro
    tryCatch({
      ts_irrigacao <- ts(serie_diaria$irrigacao, frequency = min(7, nrow(serie_diaria)))
      ts_temp <- ts(serie_diaria$media_temp, frequency = min(7, nrow(serie_diaria)))
      ts_humid <- ts(serie_diaria$media_humid, frequency = min(7, nrow(serie_diaria)))
      
      # Ajustar modelos ARIMA com tratamento para séries curtas
      modelo_irrigacao <- auto.arima(ts_irrigacao,
                                     allowdrift = FALSE,
                                     allowmean = TRUE,
                                     stepwise = TRUE,
                                     approximation = FALSE)
      
      modelo_temp <- auto.arima(ts_temp,
                                allowdrift = FALSE,
                                allowmean = TRUE,
                                stepwise = TRUE,
                                approximation = FALSE)
      
      modelo_humid <- auto.arima(ts_humid,
                                 allowdrift = FALSE,
                                 allowmean = TRUE,
                                 stepwise = TRUE,
                                 approximation = FALSE)
      
      # Fazer previsões
      prev_irrigacao <- forecast(modelo_irrigacao, h = n_dias)
      prev_temp <- forecast(modelo_temp, h = n_dias)
      prev_humid <- forecast(modelo_humid, h = n_dias)
      
      # Combinar previsões em um data.frame
      datas_futuras <- seq(max(dados$data) + 1, by = "day", length.out = n_dias)
      previsoes <- data.frame(
        data = datas_futuras,
        prob_irrigacao = as.numeric(pmin(pmax(prev_irrigacao$mean, 0), 1)),
        temp_prevista = as.numeric(prev_temp$mean),
        humid_prevista = as.numeric(pmin(pmax(prev_humid$mean, 0), 100)),
        temp_lower = as.numeric(prev_temp$lower[,2]),
        temp_upper = as.numeric(prev_temp$upper[,2]),
        humid_lower = as.numeric(prev_humid$lower[,2]),
        humid_upper = as.numeric(prev_humid$upper[,2])
      )
      
      return(previsoes)
    }, error = function(e) {
      warning("Erro na previsão ARIMA, usando método mais simples")
      
      # Calcular médias móveis simples
      media_irrigacao <- mean(tail(serie_diaria$irrigacao, 3))
      media_temp <- mean(tail(serie_diaria$media_temp, 3))
      media_humid <- mean(tail(serie_diaria$media_humid, 3))
      
      datas_futuras <- seq(max(dados$data) + 1, by = "day", length.out = n_dias)
      previsoes <- data.frame(
        data = datas_futuras,
        prob_irrigacao = rep(media_irrigacao, n_dias),
        temp_prevista = rep(media_temp, n_dias),
        humid_prevista = rep(media_humid, n_dias),
        temp_lower = rep(media_temp * 0.9, n_dias),
        temp_upper = rep(media_temp * 1.1, n_dias),
        humid_lower = rep(max(media_humid * 0.9, 0), n_dias),
        humid_upper = rep(min(media_humid * 1.1, 100), n_dias)
      )
      
      return(previsoes)
    })
  }
  
  # Função principal atualizada
  main <- function() {
    # Realizar análise exploratória
    analise <- analise_exploratoria(leituras)
    print("Estatísticas Descritivas:")
    print(analise$estatisticas)
    
    # Criar visualizações
    print("Gerando visualizações...")
    criar_visualizacoes(leituras)
    
    # Treinar modelo preditivo
    print("Treinando modelo...")
    modelo <- criar_modelo_predicao(leituras)
    print("Avaliação do Modelo:")
    print(modelo$avaliacao)
    
    # Fazer previsões
    print("Gerando previsões...")
    previsoes <- prever_proximos_dias(leituras)
    
    # Visualizar previsões
    print("Visualizando previsões...")
    visualizar_previsoes(previsoes)
  }
  
  # Executar análise
  main()
}

# Chamar a função run_analysis com o caminho do arquivo JSON
run_analysis("Z:/zdev/FIAP/fase_3/FIAP_fase3_cap1_maquina_agricola/src/dados/dados_app.json")

