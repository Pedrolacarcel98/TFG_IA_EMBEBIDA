# MEMORIA TÉCNICA: IA EMBEBIDA PARA SISTEMAS NO TRIPULADOS (DRONES)
## Clasificación de Terreno y Análisis Vibracional mediante Edge AI

**Autor:** Pedro Jardi  
**Tutor:** [Nombre del Tutor]  
**Departamento:** Tecnología Electrónica / Ciencias de la Computación  
**Grado:** Grado en Ingeniería Informática  
**Centro:** Escuela Técnica Superior de Ingeniería Informática  
**Universidad:** Universidad de Sevilla  
**Fecha:** Mayo 2026

---

## ESTRUCTURA DE LA MEMORIA (ÍNDICE PROPUESTO)

1. **INTRODUCCIÓN**
   - 1.1 Contexto y Motivación
   - 1.2 Objetivos del Proyecto
   - 1.3 Metodología de Trabajo
2. **ESTADO DEL ARTE**
   - 2.1 Evolución del Edge AI (TinyML)
   - 2.2 Algoritmos Clásicos de Clasificación vs. Aprendizaje Automático
   - 2.3 Soluciones de Mercado y Herramientas (NanoEdge AI, TensorFlow Lite)
3. **DISEÑO DEL SISTEMA (HARDWARE)**
   - 3.1 Arquitectura del Microcontrolador (STM32L476RG)
   - 3.2 Sensores Inerciales (MPU6050 y LSM6DSL)
   - 3.3 El subsistema de comunicaciones (ESP32 y WiFi)
4. **DESARROLLO DEL SOFTWARE (FIRMWARE Y COMUNICACIONES)**
   - 4.1 Adquisición y Procesamiento de Señal en C
   - 4.2 Protocolo de Puente UART-WiFi
   - 4.3 Servidor de Recepción y Limpieza en Python
5. **INTELIGENCIA ARTIFICIAL Y MODELADO**
   - 5.1 Captura de Datasets y Ventaneo Temporal
   - 5.2 Análisis de Características (Features)
   - 5.3 Selección del Modelo y Optimización (XGBoost)
6. **LOGÍSTICA, NEGOCIO E IMPACTO**
   - 6.1 Casos de Uso Industriales
   - 6.2 Análisis de Costes y Viabilidad
7. **CONCLUSIONES Y LÍNEAS FUTURAS**

---

## 1. INTRODUCCIÓN

### 1.1 Contexto y Motivación
En la última década, los sistemas de aeronaves no tripuladas (UAVs) han pasado de ser herramientas militares exclusivas a dispositivos omnipresentes en la agricultura, la inspección de infraestructuras y la logística. Sin embargo, la mayoría de estos sistemas operan de forma "ciega" respecto al entorno físico inmediato que no sea captado por cámaras. La vibración, una fuente de datos rica y subestimada, contiene información crítica sobre la salud del motor, el equilibrio de las hélices y, lo más importante, el tipo de superficie con la que el dron interactúa.

La motivación de este TFG nace de la necesidad de dotar a estos dispositivos de una "consciencia inercial" utilizando **IA Embebida (Edge AI)**. Procesar estos datos en la nube es inviable por la latencia; hacerlo mediante algoritmos de umbrales rígidos es poco fiable. La IA en el borde se presenta como la solución definitiva.

### 1.2 Objetivos del Proyecto
1.  **Diseñar un sistema de adquisición de datos** de alta frecuencia capaz de capturar vibraciones mecánicas sin pérdida de información.
2.  **Desarrollar un puente de comunicación inalámbrico** para la telemetría de datos crudos (Raw Data) necesaria para el entrenamiento.
3.  **Entrenar y desplegar un modelo de clasificación** de IA en un microcontrolador de recursos limitados, garantizando una precisión superior al 95%.
4.  **Evaluar el impacto** de esta tecnología en la autonomía y seguridad de los drones sonda.

---

## 2. ESTADO DEL ARTE (INVESTIGACIÓN TÉCNICA)

### 2.1 El auge del TinyML
El concepto de TinyML (IA en dispositivos de milivatios) ha revolucionado la informática industrial. Tradicionalmente, la IA requería GPUs masivas. Hoy, mediante técnicas de **Cuantización** (pasar de 32 bits flotantes a 8 bits enteros) y **Pruning** (eliminación de neuronas redundantes), podemos ejecutar modelos complejos en un ARM Cortex-M4 como el de este proyecto.

### 2.2 Clasificación Inercial: Métodos Tradicionales
Hasta hace poco, la detección de anomalías se basaba en la **Transformada Rápida de Fourier (FFT)**. Si una frecuencia específica superaba un umbral, se disparaba una alarma. 
*   **Limitación:** Los drones operan en entornos con mucho ruido. Un cambio de viento puede generar una frecuencia que confunda a un filtro estático.
*   **La Ventaja de la IA:** Los modelos de aprendizaje automático no solo miran una frecuencia; analizan la relación no lineal entre múltiples características (entropía, curtosis, energía), lo que los hace robustos frente al ruido ambiental.

---

## 3. DISEÑO DEL SISTEMA (ANÁLISIS DE COMPONENTES)

### 3.1 El Cerebro: STM32L476RG
Este microcontrolador de STMicroelectronics es el "sweet spot" para la IA embebida.
- **Unidad de Punto Flotante (FPU):** Permite cálculos matemáticos rápidos sin emulación por software.
- **Ultra-Low Power:** Crítico para no penalizar la batería del dron.
- **Arquitectura Harvard:** Mejora el acceso a memoria, permitiendo que las instrucciones de IA se carguen mientras los datos del sensor se procesan.

### 3.2 Los Ojos del Sistema: Sensores I2C
El proyecto utiliza una combinación de MPU6050 y LSM6DSL. La elección del **protocolo I2C** a 400kHz (Fast Mode) es estratégica:
- Permite una tasa de muestreo suficiente para capturar las vibraciones de motores que giran a miles de RPM.
- El uso de interrupciones de hardware garantiza que no perdamos muestras mientras el procesador está "ocupado" clasificando.

---

## 4. DESARROLLO DEL SOFTWARE Y COMUNICACIONES

### 4.1 La Importancia del Determinismo Temporal
En el análisis de señales, el tiempo es tan importante como el valor. Si el `HAL_Delay(10)` no es preciso, la señal se distorsiona (Jitter). En este proyecto se ha priorizado un bucle determinista que asegura 100 muestras por segundo de forma constante.

### 4.2 El Puente ESP32: Arquitectura Transparent Bridge
El ESP32 no procesa la IA, su función es puramente logística. Implementa un servidor de sockets que encapsula los datos UART provenientes del STM32 en paquetes TCP. Esto permite que el ingeniero pueda monitorizar la vibración en tiempo real desde un PC a metros de distancia, simulando el comportamiento de un dron en vuelo real.

---

## 5. INTELIGENCIA ARTIFICIAL: EL CORAZÓN DEL PROYECTO

### 5.1 Extracción de Características (Feature Engineering)
NanoEdge AI Studio ha identificado que para clasificar terreno, las métricas más útiles son:
- **Kurtosis:** Indica si los impactos de vibración son esporádicos o constantes.
- **RMS (Root Mean Square):** Da una idea de la energía total del movimiento.
- **PSD (Power Spectral Density):** Crucial para distinguir entre el ruido del motor y el impacto contra el suelo.

### 5.2 El Modelo: XGBoost Optimizado
A pesar de que las redes neuronales son populares, para datos tabulares y señales, el **XGBoost** suele ser superior en eficiencia. El modelo resultante en este proyecto utiliza solo **1.2KB de RAM**, lo cual es un hito de ingeniería informática, permitiendo que el resto de la memoria se use para tareas de control de vuelo.

---

## 6. LÓGICA DE NEGOCIO Y VISIÓN INDUSTRIAL

### 6.1 El Dron como Sonda Autónoma
Imagine una flota de drones inspeccionando un campo tras una inundación. El sistema puede clasificar automáticamente qué zonas tienen suelo firme para el aterrizaje de equipos de rescate y cuáles son fango, simplemente "tocando" o volando cerca del suelo y analizando el flujo de aire/vibración.

### 6.2 Reducción de Costes
Un sistema de telemetría por satélite para enviar datos de vibración a la nube costaría miles de euros al mes. La IA embebida reduce ese coste a **cero**, ya que el procesamiento es local.

---

## 7. CONCLUSIONES

Este trabajo demuestra que la integración de IA en el borde es el siguiente paso lógico en la robótica aérea. Hemos pasado de un prototipo que captura datos a un sistema inteligente capaz de tomar decisiones de clasificación con una precisión del 98.96%.

**Líneas futuras:** 
- Implementación de **Aprendizaje Online**, donde el dron aprenda a reconocer nuevos terrenos mientras vuela.
- Integración con el sistema de control de vuelo (Betaflight/ArduPilot) para respuestas automáticas.
