# BLOQUE 3: PLANIFICACIÓN DEL PROYECTO

## B3.1. Planificación Temporal Inicial

El proyecto se planificó para una duración total de 16 semanas (aproximadamente 4 meses), divididas en las siguientes fases críticas:

1.  **Investigación y Estado del Arte (Semanas 1-2):** Estudio de bibliografía sobre TinyML y protocolos inerciales.
2.  **Adquisición de Hardware y Pruebas de Concepto (Semanas 3-4):** Montaje del prototipo básico y validación de la comunicación I2C.
3.  **Desarrollo del Firmware y Puente WiFi (Semanas 5-8):** Implementación del código en C y C++.
4.  **Captura de Datasets y Entrenamiento de IA (Semanas 9-11):** Recopilación de miles de muestras y uso de NanoEdge AI Studio.
5.  **Pruebas de Integración y Validación (Semanas 12-14):** Test de campo y refinamiento del modelo.
6.  **Redacción de Memoria y Conclusiones (Semanas 15-16):** Documentación final.

---

## B3.2. Planificación Financiera Inicial

### Estimación de Costes de Personal (Método COCOMO)
Para un proyecto de estas características, se estima una carga de trabajo de aproximadamente 4 meses-hombre.
*   **Perfil:** Ingeniero Junior.
*   **Coste por hora:** 25 €/h.
*   **Dedicación:** 400 horas totales.
*   **Coste Personal Estimado:** 10.000 €.

### Factura de Materiales (BOM)
| Concepto | Unidades | Precio Unitario | Total |
| :--- | :---: | :---: | :---: |
| STM32L476RG Nucleo-64 | 1 | 25 € | 25 € |
| ESP32 DevKit V1 | 1 | 10 € | 10 € |
| Sensor MPU6050 / GY-521 | 1 | 5 € | 5 € |
| Cableado, Protoboard y Varios | 1 | 20 € | 20 € |
| **Total Materiales** | | | **60 €** |

---

## B3.3. Planificación Temporal Final (Real)

A lo largo del desarrollo, surgieron imprevistos que obligaron a reajustar el calendario:
*   **Desviación en Semanas 9-10:** La captura de datos "Anormales" fue más compleja de lo previsto, requiriendo fabricar hélices dañadas artificialmente para generar vibraciones realistas. Esto retrasó el entrenamiento una semana.
*   **Optimización de Memoria:** Se dedicó una semana extra a reducir la huella de la biblioteca de IA para asegurar la estabilidad del sistema.
*   **Justificación:** A pesar de los retrasos, se compensó reduciendo el tiempo de redacción de la memoria, logrando finalizar en el plazo previsto de 16 semanas.

---

## B3.4. Planificación Financiera Final

El coste final de materiales se mantuvo estable, pero el coste de personal aumentó ligeramente debido a las horas extra de captura de datos.
*   **Coste Personal Real:** 11.250 € (450 horas).
*   **Coste Materiales:** 60 €.
*   **Coste Total del Prototipo:** 11.310 €.

---

## B3.5. Estudio de Mercado

### a. Clientes Potenciales
1.  **Empresas de Inspección Industrial (40%):** Compañías que operan drones en entornos cerrados (túneles, silos).
2.  **Sector de Búsqueda y Rescate (30%):** Equipos que requieren drones autónomos en zonas sin GPS ni WiFi.
3.  **Fabricantes de Drones (OEM) (30%):** Empresas que quieran integrar seguridad proactiva en sus chasis.

### b. Plan de Comercialización (Escala de 2000 unidades)
*   **Reducción de Coste Materiales (20%):** Al comprar en volumen, el coste del kit pasa de 60 € a 48 €.
*   **Precio de Venta al Público (PVP):**
    *   Coste Fabricación: 48 €
    *   Margen de Beneficio (30%): 14,4 €
    *   Precio Final (sin IVA): 62,4 €
    *   **PVP Final (con 21% IVA): 75,50 €**

### Packs Comercializados
*   **Kit Starter (75,50 €):** Todo el hardware necesario y acceso al modelo estándar.
*   **Pack Industrial (150 €):** Incluye soporte técnico y personalización del modelo de IA para chasis específicos.
