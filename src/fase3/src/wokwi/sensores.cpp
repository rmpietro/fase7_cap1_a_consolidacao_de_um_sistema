#include "DHTesp.h"
#include <array>

const int RELE_PIN = 22;
const int DHT_PIN = 23;
const int BUTTON_PINS[] = {34, 35};
const int LDR_DO_PIN = 32;
const int LDR_AO_PIN = 33;
const float GAMMA = 0.7;
const float RL10 = 50;

DHTesp dhtSensor;

void setup() {
// Configuração dos pinos de cada componente
  Serial.begin(115200);
  // Sensor humdade e temperatura
  dhtSensor.setup(DHT_PIN, DHTesp::DHT22);

  //Botões que simulam a presença de nutrientes P e K
  pinMode(BUTTON_PINS[0], INPUT_PULLUP);
  pinMode(BUTTON_PINS[1], INPUT_PULLUP);

  //LDR que simula o sensor de pH
  pinMode(LDR_AO_PIN, INPUT);

  //Rele que simula a bomba de água
  pinMode(RELE_PIN, OUTPUT);
}

void loop() {
  TempAndHumidity  data = getTempAndHumidityFromSensor();

  // Saída formatada para JSON de forma a ser importada no programa Python
  Serial.println("{");
  Serial.println("\t\"temp\": " + String(data.temperature, 2) + ",");
  Serial.println("\t\"humid\": " + String(data.humidity, 1) + ",");

  std::array<bool, 2> states = {false, false};
    states[0] = (digitalRead(BUTTON_PINS[0]) == LOW);
    states[1] = (digitalRead(BUTTON_PINS[1]) == LOW);

  for(size_t i = 0; i < states.size(); i++) {
      if (i == 0) {
        Serial.print ("\t\"P\": ");
      } else {
        Serial.print ("\t\"K\": ");
      }
      Serial.print(states[i] ? "\"presente\",\n" : "\"não-presente\",\n");
  }

//Leitura do LDR e divisão do valor lido pela constante 288 para obter o range similar ao do pH
  float analogValue = analogRead(LDR_AO_PIN);
  float pHConverted = analogValue / 288;
  Serial.printf("\t\"pH\": %.2f,\n", pHConverted);


  // Decisão por ligar ou não a bomba de água da irrigação - Cenários:
  Serial.printf("\t\"irrigacao\": {\n");
  // Cenário 1: Solo seco - Liga a bomba
  if (data.humidity < 55) {
    Serial.printf("\t\t\"estado\": \"ligada\",\n");
    Serial.printf("\t\t\"motivo\": \"Solo seco, pouca humidade.\"\n");
    // Ligar irrigação
    digitalWrite(RELE_PIN, HIGH);
  } else

  // Cenário 2: Solo úmido e temperatura alta - Liga a bomba
  if ((data.humidity >= 55 && data.humidity <= 70) && data.temperature > 35) {
    Serial.printf("\t\t\"estado\": \"ligada\",\n");
    Serial.printf("\t\t\"motivo\": \"Solo úmido com temperatura alta.\"\n");
    digitalWrite(RELE_PIN, HIGH);
  } else

  // Cenário 3: pH básico e falta de nutrientes - Liga a bomba
  if (pHConverted > 7.5 && (!states[0] || !states[1])) {
    Serial.printf("\t\t\"estado\": \"ligada\",\n");
    Serial.printf("\t\t\"motivo\": \"pH básico e nutrientes ausentes no solo.\"\n");
    digitalWrite(RELE_PIN, HIGH);
  } else

  // Cenário 4: Solo já úmido e irrigado
  {
    Serial.printf("\t\t\"estado\": \"desligada\",\n");
    Serial.printf("\t\t\"motivo\": \"Solo suficientemente úmido com nutrientes e temperatura adequada.\"\n");
    digitalWrite(RELE_PIN, LOW);
  }
  Serial.printf("\t}\n");

  Serial.println("},");

  delay(3000);
}

TempAndHumidity getTempAndHumidityFromSensor() {
  return dhtSensor.getTempAndHumidity();
}

