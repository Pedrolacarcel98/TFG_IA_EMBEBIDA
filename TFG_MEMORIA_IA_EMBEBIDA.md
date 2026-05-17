# Memoria del Trabajo de Fin de Grado: IA Embebida en Drones de Prospección

**Título:** Sistema de Clasificación de Terreno en Tiempo Real mediante IA Embebida para Drones Sonda  
**Autor:** Pedro Jardi  
**Grado:** Ingeniería Informática  
**Institución:** Universidad de Sevilla  

---

## 1. Introducción y Resumen

Este proyecto presenta el desarrollo de un sistema avanzado de **Inteligencia Artificial Embebida (Edge AI)** diseñado para drones de prospección. El objetivo principal es clasificar de forma autónoma el tipo de terreno o el estado de navegación ("Normal", "Anormal", "Parado") basándose exclusivamente en datos inerciales (acelerometría).

A diferencia de las soluciones basadas en la nube, este sistema procesa la información directamente en el microcontrolador (MCU), permitiendo una respuesta inmediata, mayor privacidad y una reducción drástica en el consumo de ancho de banda.

## 2. IA Embebida vs. Algoritmos Clásicos: Un Análisis Investigativo

### 2.1 El Cambio de Paradigma: Del Procesamiento Centralizado al Edge
Tradicionalmente, el análisis de vibraciones en drones se ha realizado mediante:
- **Algoritmos clásicos:** Filtros de frecuencia (FFT), umbrales fijos o análisis estadístico simple.
- **IA en la nube:** Envío de datos crudos a servidores potentes para su clasificación.

### 2.2 Ventajas de la IA Embebida (Edge AI)
1. **Latencia Determinista:** La clasificación ocurre en microsegundos, sin depender de la congestión de la red WiFi/Radio.
2. **Eficiencia Energética:** Transmitir datos por radio es una de las tareas más costosas en un dron. Clasificar localmente y solo enviar el "resultado" ahorra hasta un 90% de energía en comunicaciones.
3. **Privacidad y Seguridad:** Los datos crudos nunca abandonan el sensor, eliminando puntos de vulnerabilidad.
4. **Robustez:** El sistema sigue funcionando en zonas sin cobertura o con interferencias.

### 2.3 Desventajas y Desafíos
1. **Restricciones de Hardware:** Limitación severa en RAM (KB) y Flash. No se pueden usar modelos masivos como ResNet o Transformers.
2. **Complejidad de Despliegue:** Requiere optimización matemática específica (uso de punto fijo, optimización para Cortex-M4).
3. **Dependencia de Datos de Calidad:** La "limpieza" previa es crítica, ya que el modelo en el borde es más sensible al ruido si no está bien entrenado.

## 3. Arquitectura del Sistema

El sistema se divide en tres capas funcionales:

### 3.1 Capa de Adquisición (STM32L476RG)
El núcleo del sistema es un microcontrolador **ARM Cortex-M4**.
- **Sensor:** IMU (MPU6050/LSM6DSL) conectado vía **I2C**.
- **Muestreo:** 100Hz (ventana de 64 muestras por eje = 192 características por ventana).
- **Procesamiento:** Implementa la biblioteca generada por **NanoEdge AI Studio**.

### 3.2 Capa de Comunicación (ESP32 Bridge)
Dado que el STM32 no posee conectividad inalámbrica nativa, se utiliza un **ESP32** como puente:
- **Protocolo Local:** UART a 115200 bps.
- **Protocolo de Red:** TCP/IP sobre WiFi.
- **Función:** Durante la fase de entrenamiento, actúa como "Data Logger" inalámbrico.

### 3.3 Capa de Servidor y Entrenamiento (Python + NanoEdge AI)
- **Servidor TCP:** Un script Python recibe las ventanas de datos y las valida (filtro de integridad de 192 valores).
- **NanoEdge AI Studio:** Herramienta de AutoML que analiza los datos y selecciona el mejor algoritmo. En este caso, un **XGBoost (Extreme Gradient Boosting)** optimizado.

## 4. Desarrollo Técnico y Lógica de Programación

### 4.1 Captura de Datos (Firmware STM32)
El firmware se ha desarrollado utilizando la capa de abstracción de hardware (HAL). Se ha implementado un bucle de alta precisión que garantiza la equidistancia temporal entre muestras, vital para el análisis de vibraciones.

```c
// Lógica de ventana inercial
for(uint16_t i=0; i < N_SAMPLE; i++){
    MPU6050_ReadAccel(accel);
    // Formateo y envío por UART1
    HAL_UART_Transmit(&huart1, (uint8_t*)buffer, strlen(buffer), HAL_MAX_DELAY);
    HAL_Delay(10); // Frecuencia ~100Hz
}
```

### 4.2 Pipeline de Inteligencia Artificial
El modelo seleccionado por NanoEdge AI presenta métricas sobresalientes:
- **Precisión (KPI):** 98.96%.
- **Uso de RAM:** ~1.2 KB.
- **Uso de Flash:** ~22.5 KB.
- **Preprocesamiento:** Incluye extracción de características como entropía, PSD (Densidad Espectral de Potencia), curtosis y RMS.

## 5. Lógica de Negocio y Atractivo Comercial

El uso de esta tecnología en drones comerciales ofrece un valor diferencial:
- **Mantenimiento Predictivo:** El dron puede detectar vibraciones "Anormales" que preceden a un fallo de motor o rotura de hélice.
- **Clasificación Automática de Terreno:** Permite ajustar los parámetros de control de vuelo (PID) dinámicamente según si el dron detecta que está sobre una superficie sólida, agua o vegetación (vía vibración).
- **Reducción de Costes Operativos:** Menor necesidad de infraestructura de red y mayor autonomía de batería.

## 6. Conclusiones

Este TFG demuestra que la **IA Embebida** no es solo una posibilidad teórica, sino una realidad técnica viable para la ingeniería informática actual. La integración de modelos complejos como XGBoost en microcontroladores de baja potencia abre la puerta a una nueva generación de dispositivos IoT verdaderamente inteligentes y autónomos.

La arquitectura propuesta es escalable y sienta las bases para sistemas de control de vuelo que aprenden del entorno sin intervención humana.
