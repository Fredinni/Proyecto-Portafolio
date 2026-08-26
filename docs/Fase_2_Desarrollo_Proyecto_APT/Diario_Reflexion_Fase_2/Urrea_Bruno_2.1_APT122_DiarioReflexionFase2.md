# Diario de Reflexión - Fase 2
### Experiencia de Aprendizaje 2 (EA2) | Desarrollo y Monitoreo del Proyecto APT
**Estudiante:** Bruno Urrea Ortiz  
**Carrera:** Ingeniería en Conectividad y Redes  
**Institución:** Duoc UC - Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122)

---

### 1. Seguimiento de Carta Gantt y Cumplimiento de Cronograma
> **¿Has podido cumplir todas las actividades en los tiempos definidos? ¿Qué factores han facilitado o dificultado el desarrollo de las actividades de tu plan de trabajo?**

El cronograma establecido en la Carta Gantt se ha cumplido rigurosamente y dentro de los plazos proyectados para las semanas 5 a 15 de la asignatura.

* **Factores facilitadores:** La amplia experiencia previa en virtualización con Proxmox VE y configuración de pfSense aceleró significativamente el despliegue del entorno base de laboratorio, la integración de HAProxy y el setup de Suricata en modo Inline IPS (Netmap).
* **Factores de dificultad:** El principal desafío técnico consistió en afinar la correlación de eventos entre el archivo `eve.json` de Suricata y las tablas de estados de FreeBSD `pfctl`, debido a la alta tasa de ruido y firmas genéricas que generan falsas alertas en entornos de prueba web.

---

### 2. Resolución de Dificultades y Contingencias Técnicas
> **¿De qué manera has enfrentado y/o planeas enfrentar las dificultades que han afectado el desarrollo de tu Proyecto APT?**

Para solucionar la tasa de falsos positivos característica de los motores IDS/IPS tradicionales (donde firmas genéricas disparan alertas por escaneos rutinarios o peticiones inocuas), se diseñó un algoritmo de doble verificación en el **pfctl Log Engine**:
1. **Verificación Heurística de Payload:** Análisis del contenido del payload HTTP y decodificación de parámetros SQLi en la capa de aplicación expuesta por HAProxy hacia DVWA.
2. **Validación de Estado de Red en Kernel:** Consulta en tiempo real a la tabla `snort2c` de FreeBSD pfctl (`pfctl -t snort2c -T show`) y tabla de estados (`pfctl -s state`) para confirmar que la dirección IP atacante fue efectivamente expulsada y bloqueada en la capa de red del kernel FreeBSD.

Adicionalmente, se configuró un pipeline asíncrono con WebSockets para conectar el motor de eventos con la API de voz **Gemini Live Flash 3.1**, asegurando baja latencia en la llamada telefónica iniciada por Asterisk PBX hacia el CISO.

---

### 3. Evaluación de Evidencias de Avance
> **¿Cómo evalúas tu(s) evidencia(s) de avance? ¿Qué destacas y qué podrías hacer para mejorar tus evidencias?**

Las evidencias acumuladas son de alto estándar técnico y 100% verificables:
* Capturas y logs de bloqueo activo en pfSense (Suricata en modo Inline IPS + tablas dinámicas `pfctl`).
* Grabaciones de audio y logs de telemetría de las llamadas ejecutadas por Asterisk PBX y el agente de IA Gemini Live en tiempo real.
* Repositorio estructurado en GitHub con código modular, contenedores Docker y configuraciones reproducibles.

**Oportunidad de mejora:** Incorporar un panel de métricas visuales (dashboard interactivo) que grafique el tiempo de respuesta total desde la detección del paquete malicioso hasta el descolgado telefónico de la llamada de alerta al CISO.

---

### 4. Inquietudes y Consultas para el Docente / Pares
> **¿Qué inquietudes te quedan sobre cómo proceder? ¿Qué pregunta te gustaría hacerle a tu docente o a tus pares?**

* **Consulta para el docente guía y comisión:**  
  *¿Cuál es el criterio preferido por la comisión evaluadora para la demostración en vivo de la llamada telefónica del agente de IA durante la defensa de la Fase 3? ¿Es recomendable proyectar el flujo de paquetes en Wireshark/SIP en paralelo al audio en directo de la llamada con Gemini Live para maximizar el impacto de la rúbrica?*

---

### 5. Gestión y Distribución del Trabajo en Equipo
> **¿Consideran que las actividades deben ser redistribuidas entre los miembros del grupo? ¿Hay nuevas actividades que deban ser asignadas a algún miembro del grupo?**

La distribución de tareas se encuentra equilibrada y alineada con las fortalezas individuales de cada integrante del equipo:
* **Infraestructura y Redes:** Arquitectura perimetral en pfSense, routing, VLANs y reglas de firewall.
* **Servicios Web y Proxy:** Configuración de HAProxy, certificados SSL y despliegue del entorno DVWA en DMZ.
* **Telefonía y Voz IP:** Centralita Asterisk PBX en contenedor Docker, troncales SIP y dialplan.
* **Motor de Correlación e IA:** Integración de la API de voz Gemini Live, filtrado en `pfctl` y supresión de falsos positivos.

En esta fase se acordó asignar la preparación del guión de prueba de inyecciones SQL simuladas y la recolección de evidencias para el informe final de entrega.

---

### 6. Evaluación del Trabajo Grupal
> **¿Cómo evalúan el trabajo en grupo? ¿Qué aspectos positivos destacan? ¿Qué aspectos podrían mejorar?**

* **Aspectos positivos:** Destaco el compromiso constante, la comunicación fluida a través de canales técnicos y la capacidad de articular distintas áreas de la carrera (Routing, Switching, Telefonía, Ciberseguridad y Programación).
* **Aspectos a mejorar:** Debemos sincronizar con mayor frecuencia las versiones de los documentos en el repositorio para evitar desfases previos a las entregas de hito de la Fase 2 y Fase 3.
