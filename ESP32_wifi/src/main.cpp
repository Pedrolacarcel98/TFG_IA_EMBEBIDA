#include <Arduino.h>
#include <WiFi.h>

// --- CONFIGURACIÓN DE RED ---
const char* ssid = "PixelPedro";
const char* password = "pua12398";
const char* ip_PC = "192.168.157.23"; // IP de tu PC
const uint16_t puerto = 8082;

WiFiClient cliente;

void setup() {
  Serial.begin(115200);   
  
  // Aumentamos el buffer de recepción para no perder datos en ráfagas (Batch)
  Serial2.setRxBufferSize(4096); 
  Serial2.begin(115200);  

  Serial.println("Iniciando ESP32 en modo Puente Robusto...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n¡Wi-Fi Conectado!");
}

void loop() {
  // Mejora en la reconexión: stop() asegura que el socket se limpie
  if (!cliente.connected()) {
    Serial.println("Buscando servidor PC...");
    cliente.stop(); 
    if (cliente.connect(ip_PC, puerto)) {
      Serial.println("Conexión establecida con el Servidor.");
    } else {
      delay(2000); // Esperar un poco antes de reintentar
    }
  }

  // Lectura eficiente y reenvío
  if (cliente.connected()) {
    while (Serial2.available() > 0) {
      char c = Serial2.read();
      cliente.write(c); // Reenvío byte a byte es más síncrono y evita esperas de newline
      
      // Opcional: ver por debug (solo si no satura)
      // Serial.print(c); 
    }
  }
}