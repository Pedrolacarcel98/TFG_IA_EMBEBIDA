# Sistema Inteligente de Clasificación de Terrenos para Vehículos RC (TFG IA Embebida)

Este proyecto desarrolla un **Sistema Inteligente de Clasificación de Terrenos en Tiempo Real** para vehículos RC mediante técnicas de Inteligencia Artificial Embebida (TinyML). El sistema permite que el vehículo detecte el tipo de terreno (arena, grava, asfalto, etc.) por el que circula basándose en la "huella vibratoria" capturada por un acelerómetro.

## 🚀 Arquitectura del Sistema

El flujo de información del sistema sigue la siguiente arquitectura:
**Sensor (Acelerómetro)** ➔ **STM32 (Procesamiento/Inferencia)** ➔ **ESP32 (Transmisión)** ➔ **PC (Servidor/NanoEdge AI Studio)**

### 🧩 Descripción de Módulos

El repositorio está estructurado en los siguientes módulos principales:

* **`DataLogger_STM32/`**: Contiene el código fuente para la placa STM32 (Cortex-M4). Este módulo se encarga de la recolección inicial de datos (Data Logging) desde el acelerómetro. Prepara las ventanas de tiempo (Buffers) con la frecuencia de muestreo adecuada para extraer la vibración.
* **`ESP32_wifi/`**: Firmware para el microcontrolador ESP32. Actúa como un puente (Bridge) UART-to-WiFi, recibiendo los datos procesados o en crudo desde la STM32 a través de comunicación serie y enviándolos de forma inalámbrica al servidor TCP en el PC.
* **`server/`**: Contiene la implementación del servidor de recepción en Python. Dispone de dos versiones:
  * `servidor.py`: Servidor básico de línea de comandos para la recolección de datos crudos (`datos_entrenamiento.csv`) para entrenamiento en NanoEdge AI.
  * `server_implementation.py`: Interfaz gráfica avanzada (Tkinter) que permite ver la recepción en vivo, almacenar el historial de viajes en una base de datos SQLite (`viajes_terrenos.db`) y mostrar métricas analíticas (gráficos con Matplotlib).
* **`nanoEdgeAI/`**: Almacena las configuraciones, proyectos y modelos generados utilizando la herramienta NanoEdge AI Studio de STMicroelectronics.
* **`implemetation_AI_libraries/`**: Contiene las librerías generadas (estáticas/dinámicas) de IA ya compiladas y listas para ser integradas y llamadas desde el código del microcontrolador STM32.
* **`TerrainDetector/`**: Proyecto final de integración para la STM32 que incluye tanto la captura de datos como la inferencia en tiempo real utilizando el modelo embebido de NanoEdge AI.
* **`PruebasLedUserButton/`**: Código de prueba para verificar el funcionamiento básico de los periféricos de la placa (LEDs y botón de usuario) antes de la integración compleja.

---

## 🛠️ Instrucciones de Despliegue del Servidor

El servidor de análisis recibe los datos enviados por la ESP32 a través de WiFi. Sigue estos pasos para ponerlo en marcha:

### Requisitos Previos
* Python 3.8 o superior instalado en el PC.
* Dependencias de Python. Abre una terminal y ejecuta el siguiente comando (necesario para la versión gráfica avanzada):
  ```bash
  pip install matplotlib
  ```
  *(Nota: Los demás módulos como `socket`, `tkinter`, `sqlite3` y `csv` forman parte de la librería estándar de Python).*

### Opción 1: Servidor Básico (Recolección para Entrenamiento)
Este script es ideal para la fase inicial del proyecto (Data Logging), guardando matrices perfectas para NanoEdge AI.
1. Abre una terminal en la carpeta `server/`.
2. Ejecuta el servidor:
   ```bash
   python servidor.py
   ```
3. El servidor quedará escuchando en el puerto `8082`. Cuando la ESP32 se conecte, guardará los datos limpios en `datos_entrenamiento.csv`.

### Opción 2: Servidor Avanzado (Analítica de Viajes e Interfaz Gráfica)
Este servidor es el panel de control completo, con base de datos e interfaz gráfica.
1. Abre una terminal en la carpeta `server/`.
2. Ejecuta la aplicación:
   ```bash
   python server_implementation.py
   ```
3. Se abrirá la interfaz gráfica "TFG IA Embebida - Analítica de Terrenos".
4. Ve a la pestaña **"Recepción en Vivo"** y pulsa el botón **"Iniciar Servidor"**.
5. Asegúrate de que tanto el PC como la ESP32 estén conectados a la misma red WiFi y que la ESP32 apunte a la IP del PC en el puerto `8082`.
6. En la pestaña **"Historial de Viajes"** podrás consultar viajes anteriores, ver gráficos de proporciones de terreno pulsando **"Ver Métricas"** o analizar todos los datos con **"Métricas Globales"**.

---
*Documentación generada para el Trabajo de Fin de Grado.*
