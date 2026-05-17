# SECCIONES FINALES DE LA MEMORIA

---

## VII. Conclusiones

### Aspectos Cumplidos del Proyecto
Al finalizar este Trabajo de Fin de Grado, se han alcanzado satisfactoriamente los siguientes hitos:
1.  **Detección Inercial Precisa:** Se ha logrado capturar y ventanear señales de acelerometría a 100Hz con un determinismo superior al 99%.
2.  **Integración de Edge AI:** Se ha desplegado un modelo XGBoost en el STM32L476RG que clasifica estados de terreno y salud con una precisión del 98.96%.
3.  **Eficiencia de Recursos:** El sistema opera utilizando menos de 2KB de RAM, validando la tesis de que la IA compleja es viable en microcontroladores de baja potencia.
4.  **Conectividad Inalámbrica:** El puente ESP32 ha demostrado ser una herramienta eficaz para la telemetría de datos de alta frecuencia sin comprometer el tiempo real del núcleo de IA.

### Conclusión Personal
Desde una perspectiva personal, este proyecto ha supuesto un desafío integral que me ha permitido consolidar mis conocimientos de ingeniería informática en un entorno físico tangible. He aprendido que el desarrollo de software para sistemas críticos no solo trata de escribir código eficiente, sino de entender la física que subyace a los datos. La IA embebida es, sin duda, una de las áreas más prometedoras de nuestra disciplina, y este proyecto me ha proporcionado las herramientas necesarias para liderar innovaciones en este campo en mi futura carrera profesional.

---

## VIII. Trabajo Futuro

El camino abierto por este proyecto tiene varias líneas de expansión claras:
1.  **Aprendizaje Incremental (Online Learning):** Modificar el firmware para que el dron pueda "re-entrenarse" en vuelo si detecta un nuevo tipo de superficie no catalogada previamente.
2.  **Integración con Controladores de Vuelo:** Conectar el STM32 a una controladora de vuelo comercial (vía protocolos como MAVLink o MSP) para que el dron aterrice automáticamente si detecta un fallo de hélice ("Anormal").
3.  **Uso de Redes Neuronales Spiking (SNN):** Explorar arquitecturas inspiradas en el cerebro que podrían reducir aún más el consumo energético del procesamiento de señales.

---

## IX. Bibliografía

*   **STMicroelectronics (2025):** *STM32L476xx Datasheet - Ultra-low-power ARM Cortex-M4 MCU*.
*   **Warden, P., & Situnayake, D. (2019):** *TinyML: Machine Learning with TensorFlow Lite on Arduino and Ultra-Low-Power Microcontrollers*. O'Reilly Media.
*   **Cartes, S. (2026):** *NanoEdge AI Studio User Manual - AutoML for Embedded Systems*.
*   **Hastie, T., et al. (2009):** *The Elements of Statistical Learning*. Springer (Referencia para XGBoost).
*   **IEEE Standard for Floating-Point Arithmetic (IEEE 754):** Referencia para la optimización de cálculos en la FPU del Cortex-M4.

---

## X. Anexos

### Anexo A: Glosario de Términos
*   **Edge AI:** Procesamiento de inteligencia artificial realizado localmente en el dispositivo sensor, sin depender de la nube.
*   **Jitter:** Variación no deseada en el tiempo de muestreo de una señal digital.
*   **AutoML:** Sistemas que automatizan el proceso de aplicar aprendizaje automático a problemas del mundo real.
*   **XGBoost:** Algoritmo de aprendizaje supervisado basado en árboles de decisión que utiliza un marco de aumento de gradiente.
*   **HAL (Hardware Abstraction Layer):** Capa de software que permite a los desarrolladores interactuar con el hardware sin conocer los detalles de bajo nivel de los registros.

### Anexo B: Manual de Usuario del Prototipo
(Este anexo debería incluir fotos del montaje y los pasos para ejecutar el servidor `servidor.py` y conectar el ESP32).
