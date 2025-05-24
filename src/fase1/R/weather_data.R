# Load required libraries
library(tidyverse)
library(httr)
library(glue)

current_weather_url <- "http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/3594/days/15"

api_token <- "17c8a851269fd9a002025ec91983f207"

current_query <- list(token = api_token)

response <- GET(current_weather_url, query = current_query)

json_result <- content(response, as = "parsed")
results <- json_result$data
city <- json_result$name
state <- json_result$state

print(glue("____________________________________________________________________"))
print(glue("Previsão de chuvas e temperatura para a cidade de {city}, {state}"))
print(glue("Próximos 7 dias - API Advisor Climatempo"))
print(glue("____________________________________________________________________"))

daysList <- list()
rainList <- list()
maxTempList <- list()
minTempList <- list()

for (day in results) {
    date <- day$date
    daysList <- append(daysList, date)
    rain <- day$rain$probability
    rainList <- append(rainList, rain)
    max_temp <- day$temperature$max
    maxTempList <- append(maxTempList, max_temp)
    min_temp <- day$temperature$min
    minTempList <- append(minTempList, min_temp)
    print(glue("Data: {date}, : Probabilidade de chuva: {rain} %, Máxima do dia: {max_temp}, Mínima do dia: {min_temp}"))
}
print(glue("____________________________________________________________________"))
print(glue("Os dados serão impressos no arquivo csv/weather_forecast_R.csv para uso externo."))
print(glue("____________________________________________________________________"))
df <- data.frame(Dia = daysList, Probabilidade_de_Chuva = rainList, Máxima_do_Dia = maxTempList, Mínima_do_Dia = minTempList)
write.csv(df, "csv/weather_forecast_R.csv", row.names=FALSE)