suppressWarnings({
library(tidyverse)
# Importando os dados do CSV gerado
corn_data <- read.csv("csv/corn_data_output.csv", header = TRUE)
sugarcane_data <- read.csv("csv/sugarcane_data_output.csv", header = TRUE)

# Removendo a primeira coluna
corn_df <- subset(corn_data, select = -1)
sugarcane_df <- subset(sugarcane_data, select = -1)

stats_corn_df <- corn_df %>%
  pivot_longer(cols = everything(), names_to = "Variable", values_to = "Value") %>%
  group_by(Variable) %>%
  summarise(
    Média = mean(Value),
    Minimo = min(Value),
    Máximo = max(Value),
    Desvio_Padrão = sd(Value)
  )

write.csv(stats_corn_df, "csv/corn_stats_R.csv", row.names=FALSE)

stats_sugarcane_df <- sugarcane_df %>%
  pivot_longer(cols = everything(), names_to = "Variable", values_to = "Value") %>%
  group_by(Variable) %>%
  summarise(
    Média = mean(Value),
    Minimo = min(Value),
    Máximo = max(Value),
    Desvio_Padrão = sd(Value)
  )

write.csv(stats_sugarcane_df, "csv/sugarcane_stats_R.csv", row.names=FALSE)
})