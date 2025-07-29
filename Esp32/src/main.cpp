#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// --- CONFIGURAZIONI ---
#define DHTPIN 25
#define DHTTYPE DHT11
#define BUTTON_PIN 35
#define SERVER_URL "http://192.168.1.11:5000/timestamp"  // <-- Modifica IP se necessario

const char* ssid = "Alfio";         // <-- Modifica
const char* password = "vittoriaa"; // <-- Modifica

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT);
  dht.begin();
  

  WiFi.begin(ssid, password);
  Serial.print("Connessione al WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnesso al WiFi!");
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println("Bottone premuto, lettura e invio dati...");

    float temperatura = dht.readTemperature();
    float umidita = dht.readHumidity();

    if (isnan(temperatura) || isnan(umidita)) {
      Serial.println("Errore nella lettura del sensore DHT11.");
      return;
    }

    String payload = "Temperatura: " + String(temperatura) + ", Umidita: " + String(umidita);

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.setTimeout(5000);

      http.begin(SERVER_URL);
      http.addHeader("Content-Type", "text/plain; charset=UTF-8");

      int httpResponseCode = http.POST(payload);

      /*if (httpResponseCode > 0) {
        Serial.print("Risposta server: ");
        Serial.println(http.getString());
      } else {
        Serial.print("Errore nella richiesta POST. Codice: ");
        Serial.println(httpResponseCode);
      }*/

      http.end();
    } else {
      Serial.println("WiFi disconnesso.");
    }

    delay(1000);  // debounce
  }
}
