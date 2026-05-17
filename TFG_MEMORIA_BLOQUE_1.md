# TRABAJO DE FIN DE GRADO: INTELIGENCIA ARTIFICIAL EMBEBIDA EN DRONES DE PROSPECCIÓN
## Clasificación de Terreno y Análisis Vibracional mediante Edge AI

**Autor:** Pedro Jardi  
**Grado:** Ingeniería Informática  
**Centro:** Escuela Técnica Superior de Ingeniería Informática  
**Universidad:** Universidad de Sevilla  
**Fecha:** Mayo 2026

---

# BLOQUE 1: DESCRIPCIÓN DEL PROYECTO

## B1.1. Introducción y Motivación

### El Susurro de las Hélices: Una Nueva Era de Consciencia Maquinal

Imagine un escenario de catástrofe natural: una inundación ha devastado una región costera. Los equipos de rescate necesitan desplegar sensores de calidad del agua y suministros médicos en puntos críticos. Sin embargo, el terreno es traicionero; lo que desde el aire parece tierra firme puede ser en realidad un fango movedizo que devoraría cualquier equipo pesado. En este caos, un pequeño enjambre de drones surca el cielo. Pero no son drones convencionales. No son meras cámaras voladoras que dependen de que un humano interprete una imagen borrosa a kilómetros de distancia.

Estos dispositivos poseen lo que podríamos denominar un "sentido del tacto digital". A medida que se acercan a la superficie, la interacción del flujo de aire de sus hélices con el suelo y las sutiles vibraciones mecánicas de su chasis cuentan una historia que el ojo humano no puede ver. En milisegundos, el dron "siente" la densidad del terreno. Detecta si el motor está sufriendo un estrés inusual debido a una hélice dañada por los escombros. Toma la decisión de abortar un aterrizaje en una zona "Anormal" y buscar suelo firme ("Normal"), todo ello sin enviar un solo bit de datos a la nube, operando en un silencio radioeléctrico total si es necesario.

### Problemática Social y Técnica
La problemática que este proyecto resuelve es doble. Por un lado, la **dependencia tecnológica de la conectividad**. En situaciones críticas (rescates, zonas de guerra, inspecciones en túneles), el WiFi o el 5G fallan. Un dron que "piensa" en la nube es un dron que queda inutilizado ante la mínima interferencia. Por otro lado, la **seguridad operativa**. Los drones actuales son frágiles; un fallo en un rodamiento de un motor puede derribar una aeronave de miles de euros. 

Este proyecto se focaliza en el ámbito de la **Ingeniería de Sistemas Inteligentes y la Robótica Autónoma**. Buscamos dotar al microcontrolador, el humilde corazón de silicio de la aeronave, de la capacidad de discernir su entorno y su propio estado de salud. Al integrar Inteligencia Artificial directamente en el hardware inercial (Edge AI), transformamos un juguete teledirigido en una sonda científica autónoma, capaz de interactuar con la sociedad de forma más segura, eficiente y privada.

---

## B1.2. Objetivos del Proyecto

### Objetivos Profesionales
*   **Desarrollo de un Sistema de Edge AI Real:** Implementar un pipeline completo de Machine Learning, desde la adquisición de señales crudas hasta el despliegue de un modelo optimizado en un sistema embebido.
*   **Optimización de Recursos en Hardware Limitado:** Demostrar que es posible ejecutar algoritmos de alta complejidad (XGBoost) en microcontroladores con menos de 100KB de RAM, maximizando la eficiencia energética.
*   **Diseño de Arquitecturas de Telemetría Robustas:** Crear un sistema de comunicación híbrido (UART-WiFi) que permita la monitorización en tiempo real sin interferir con los procesos críticos de control.

### Objetivos Educacionales
*   **Maestría en Sistemas Operativos de Tiempo Real y HAL:** Profundizar en el uso de capas de abstracción de hardware (STM32 HAL) y la gestión de interrupciones para procesos deterministas.
*   **Integración Multidisciplinar:** Unificar conceptos de física (análisis inercial), matemáticas (procesamiento de señales), inteligencia artificial y redes de computadores.
*   **Investigación en AutoML:** Evaluar la eficacia de herramientas de vanguardia como NanoEdge AI Studio frente al desarrollo manual de modelos.

---

## B1.3. Estado del Arte

### Producto 1: DJI AirSense / Sistemas Propietarios de DJI
**Descripción:** Los líderes del mercado de drones utilizan sistemas avanzados para evitar colisiones (vía visión computacional) y monitorización de salud del motor.
*   **Pros:** Extremadamente fiables y listos para usar (Plug & Play).
*   **Contras:** Sistemas "caja negra". El usuario no puede adaptar la IA a sus necesidades ni extraer los modelos para otros usos. Coste muy elevado asociado a la marca.
*   **Relación con este proyecto:** Mientras DJI se enfoca en la visión, este proyecto explora la vía inercial/vibracional, que funciona incluso en oscuridad total o humo denso.

### Producto 2: TensorFlow Lite for Microcontrollers (TFLM)
**Descripción:** Framework de Google para ejecutar redes neuronales en microcontroladores.
*   **Pros:** Gran comunidad y soporte para una vasta gama de arquitecturas.
*   **Contras:** Requiere una curva de aprendizaje muy alta. A menudo, las redes neuronales que genera son demasiado pesadas para MCUs de gama media si no se realiza un "pruning" manual exhaustivo.
*   **Relación con este proyecto:** Este proyecto utiliza **NanoEdge AI**, que a diferencia de TFLM, optimiza el modelo específicamente para señales de sensores inerciales, logrando una huella de memoria (1.2KB RAM) inalcanzable para TFLM sin meses de trabajo.

### Producto 3: Filtros de Umbral FFT (Sistemas de Mantenimiento Clásicos)
**Descripción:** Dispositivos industriales que disparan una alerta si una frecuencia de vibración supera un umbral.
*   **Pros:** Bajo coste y lógica sencilla.
*   **Contras:** Muy sensibles a falsos positivos. En un dron, el viento o un giro brusco pueden ser interpretados como un fallo de motor.
*   **Aportación del proyecto:** Mi proyecto aporta **resiliencia**. Al usar IA, el sistema aprende a distinguir el "ruido normal de vuelo" del "ruido de fallo", reduciendo drásticamente los falsos positivos por una fracción del coste de un sistema industrial.

---

## B1.4. Elicitación de Requisitos y Análisis de Riesgos

### Requisitos Hardware (RH)
*   **RH1:** Microcontrolador con unidad de punto flotante (FPU) para cálculos de IA (STM32L476RG).
*   **RH2:** Sensor inercial con alta tasa de refresco (MPU6050/LSM6DSL).
*   **RH3:** Módulo de conectividad inalámbrica para fase de entrenamiento (ESP32).

### Requisitos Software (RS)
*   **RS1:** Firmware en C capaz de muestrear a 100Hz sin deriva temporal (Jitter).
*   **RS2:** Algoritmo de clasificación de IA con una precisión mínima del 90%.
*   **RS3:** Script de limpieza de datos en Python para eliminar tramas corruptas.

### Análisis de Riesgos y Mitigación
1.  **Riesgo de Saturación de Memoria:** El modelo de IA podría exceder la RAM del STM32.
    *   *Mitigación:* Se ha seleccionado un modelo XGBoost optimizado vía NanoEdge AI que solo consume 1.2KB.
2.  **Riesgo de Corrupción de Datos en Telemetría:** La comunicación UART es sensible al ruido electromagnético de los motores.
    *   *Mitigación:* Implementación de un filtro de integridad en el servidor Python que descarta cualquier trama que no tenga exactamente 192 valores.
3.  **Riesgo de Sobrecalentamiento:** El procesamiento continuo de IA puede elevar la temperatura del MCU.
    *   *Mitigación:* Uso de modos de bajo consumo y optimización del ciclo de trabajo del procesador.
