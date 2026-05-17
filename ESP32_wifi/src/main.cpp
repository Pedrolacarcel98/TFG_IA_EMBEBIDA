#include <Arduino.h>
#include <WiFi.h>

// --- CONFIGURACIÓN DE RED ---
const char* ssid = "PixelPedro";
const char* password = "pua12398";
const char* ip_PC = "10.152.249.23"; // IP de tu PC
const uint16_t puerto = 8082;

WiFiClient cliente;

void setup() {
  // Serial USB para debug en tu pantalla
  Serial.begin(115200);   
  
  // Serial2 para leer los datos que vienen de la STM32
  // En la mayoría de ESP32: RX2 = Pin 16, TX2 = Pin 17
  Serial2.begin(115200);  

  Serial.println("Iniciando ESP32 en modo Puente Wi-Fi...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n¡Wi-Fi Conectado!");
}

void loop() {
  // Mantener la conexión con el servidor Python
  if (!cliente.connected()) {
    Serial.println("Buscando servidor Python...");
    cliente.connect(ip_PC, puerto);
    delay(1000);
  }

  // Si estamos conectados y la STM32 nos envía datos
  if (cliente.connected() && Serial2.available()) {
    // Leemos la ventana completa hasta el salto de línea
    String data = Serial2.readStringUntil('\n');
    data.trim(); // Limpiamos espacios extra o retornos de carro
    
    if (data.length() > 0) {
      // Enviamos el bloque completo por Wi-Fi con un solo salto de línea
      cliente.print(data + "\n");
      
      // Mostrar por consola un resumen para verificar que fluye
      Serial.println("Reenviado al PC -> " + data);
    }
  }
}