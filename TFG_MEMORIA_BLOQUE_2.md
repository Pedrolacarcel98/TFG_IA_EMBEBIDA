# BLOQUE 2: EJECUCIÓN DEL PROYECTO

## B2.1. Diseño del Sistema

El sistema se concibe como una arquitectura de tres capas diseñada para maximizar el determinismo en la captación de datos y la flexibilidad en el procesamiento.

### Esquema General y Diagrama de Bloques
1.  **Bloque de Adquisición (STM32L476RG + MPU6050):** Este es el núcleo físico. El sensor MPU6050 capta las aceleraciones en los ejes X, Y y Z. Estos datos son leídos por el STM32 mediante el protocolo I2C. La funcionalidad de este bloque es garantizar que las señales lleguen de forma pura y equidistante en el tiempo al algoritmo de IA.
2.  **Bloque de Comunicación (Puente ESP32):** Actúa como un intermediario transparente. Recibe los datos procesados o crudos por UART y los encapsula en paquetes TCP/IP para su transmisión vía WiFi. Su importancia radica en desacoplar las tareas de red de las tareas de tiempo real del STM32.
3.  **Bloque de Inteligencia y Servidor (Python + NanoEdge AI):** En la fase de entrenamiento, este bloque recibe los datos crudos y genera el modelo. En la fase de operación, puede actuar como una consola de mando para visualizar las clasificaciones que el dron realiza localmente.

---

## B2.2. Implementación

### B2.2.1. Tecnologías Empleadas

#### Hardware: STM32L476RG (Nucleo-64)
El microcontrolador elegido pertenece a la serie de ultra-bajo consumo de ST. Basado en el núcleo ARM Cortex-M4, incluye una FPU que es vital para las operaciones de punto flotante de los modelos de IA.
*   **Frecuencia:** 80 MHz.
*   **Memoria:** 1 MB Flash / 128 KB RAM.
*   **Periféricos:** I2C1 para el sensor, UART1 para comunicación con ESP32, UART2 para depuración USB.

#### Sensor: MPU6050 / LSM6DSL
Se utiliza un acelerómetro y giroscopio de 6 ejes. El proyecto se centra en la acelerometría, configurada en un rango de ±2g para captar vibraciones sutiles sin saturar el sensor.
*   **Comunicación:** I2C a 400kHz.
*   **Precisión:** ADC de 16 bits por canal.

#### Software: NanoEdge AI Studio
Plataforma de AutoML para Edge AI. Permite encontrar la mejor combinación de preprocesamiento y algoritmo de clasificación.
*   **Algoritmo final:** XGBoost (Extreme Gradient Boosting).
*   **Características extraídas:** Entropía, PSD, Curtosis, RMS, Cruces por cero, etc.

---

### B2.2.2. Desarrollo

#### 1. Capa de Adquisición (Firmware STM32)
El desarrollo se realizó en C sobre el entorno STM32CubeIDE. El mayor reto fue asegurar el determinismo. Se implementó una lógica de "ventaneo":
*   Se capturan 64 muestras consecutivas por cada eje (X, Y, Z).
*   Esto genera una ventana de 192 valores (64 * 3).
*   Se utiliza un retardo preciso de 10ms entre muestras para lograr 100Hz.

#### 2. Capa de Red (Puente ESP32)
El ESP32 se programó en C++ (Arduino Framework). Implementa un servidor de sockets que escucha en el puerto 8082. Su lógica es un bucle infinito de lectura UART y escritura en Socket TCP.
*   **Problema solucionado:** La latencia del WiFi a veces bloqueaba el flujo de datos. Se solucionó mediante el uso de buffers circulares y tiempos de espera no bloqueantes.

#### 3. Capa de Inteligencia (Pipeline de Datos)
El proceso de entrenamiento siguió estos pasos:
1.  **Captura de Clases:** "Normal" (vuelo estable), "Anormal" (vibración por hélice dañada), "Parado".
2.  **Limpieza:** Uso de un script Python para asegurar que cada ventana tenga exactamente 192 columnas, eliminando tramas con ruido UART.
3.  **Benchmark:** NanoEdge AI analizó más de 500 combinaciones de algoritmos, seleccionando XGBoost por su equilibrio entre precisión (98.96%) y ligereza (1.2KB RAM).

---

## B2.3. Pruebas del Sistema

### Plan de Pruebas Técnicas
*   **Prueba de Integridad de Datos:** Se verificó que el 100% de las tramas enviadas por el STM32 llegaban intactas al servidor Python tras 1 hora de funcionamiento continuo.
*   **Prueba de Tiempo de Respuesta:** La latencia de clasificación (desde que termina la ventana hasta que sale el resultado) se midió en menos de 5ms, cumpliendo con los requisitos de tiempo real.

### Pruebas de Usabilidad (Test SUS)
Se realizó una prueba con 3 voluntarios (estudiantes de ingeniería) para evaluar la facilidad de puesta en marcha del sistema.
*   **Resultado:** Puntuación de 85/100 en el System Usability Scale (SUS), indicando una alta usabilidad. Los usuarios destacaron la claridad de la visualización en la consola Python.
