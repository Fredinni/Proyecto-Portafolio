# Diario de Reflexión - Fase 2
### Experiencia de Aprendizaje 2 (EA2) | Desarrollo y Monitoreo del Proyecto APT
**Estudiante:** Bruno Urrea Ortiz  
**Carrera:** Ingeniería en Conectividad y Redes  
**Institución:** Duoc UC - Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122)

---

### 1. Seguimiento de Carta Gantt y Cumplimiento de Cronograma
> **¿Has podido cumplir todas las actividades en los tiempos definidos? ¿Qué factores han facilitado o dificultado el desarrollo de las actividades de tu plan de trabajo?**

El cronograma establecido en la Carta Gantt oficial (Segundo Semestre 2026: Agosto a Diciembre 2026) se encuentra estructurado y ejecutándose rigurosamente dentro de los plazos proyectados. Tras culminar exitosamente el hito A1 de la Fase 1 (Setup Base pfSense CE 2.9.0 y Netmap Kernel Tuning) y encontrándose actualmente en ejecución el hito A2 (Segmentación de VLANs 802.1Q a cargo de Freddy Vásquez), la Fase 2 de Desarrollo (Semanas 5 a 15) proyecta la implementación secuencial del motor de prevención Suricata IPS, el proxy HAProxy, el Motor de Correlación KRONOS en Python y la centralita Asterisk PBX con Gemini Live.

* **Factores facilitadores:** La amplia experiencia previa en virtualización con Proxmox VE y configuración de redes aceleró significativamente el despliegue del entorno base de pfSense y la parametrización de kernel para el framework Netmap.
* **Factores de dificultad:** El principal desafío técnico del Hito A1 consistió en la incompatibilidad nativa de Netmap con la aceleración por hardware (TSO/LRO), lo cual requirió desactivar el hardware offloading y cuadruplicar los buffers mbuf en FreeBSD. Para los siguientes hitos de la Fase 2, el desafío clave será afinar la correlación de eventos entre `eve.json` y las tablas de estados de `pfctl` para suprimir el ruido de falsos positivos.

---

### 2. Resolución de Dificultades y Contingencias Técnicas
> **¿De qué manera has enfrentado y/o planeas enfrentar las dificultades que han afectado el desarrollo de tu Proyecto APT?**

Para resolver el cuello de botella del Hito A1, se diseñó e implementó un script de verificación automatizada (`verify_kernel_hardening.py`) y un script de shell (`tune_loader_conf.sh`) que aseguran la persistencia del tuning de kernel (`net.inet.ip.fastforwarding=0`, `kern.ipc.nmbclusters=1000000`) en `/boot/loader.conf.local`.

Asimismo, para la Fase 2 en desarrollo se tiene estructurado el algoritmo de doble verificación del **Motor de Correlación KRONOS**:
1. **Verificación Heurística de Payload:** Análisis sintáctico del payload HTTP y decodificación de parámetros SQLi en la capa de aplicación expuesta por HAProxy hacia DVWA.
2. **Validación de Estado de Red en Kernel:** Consulta en tiempo real a la tabla `snort2c` de FreeBSD pfctl (`pfctl -t snort2c -T show`) y tabla de estados (`pfctl -s state`) para confirmar que la dirección IP atacante fue efectivamente expulsada y bloqueada en la capa de red del kernel FreeBSD.

Adicionalmente, se proyecta un pipeline asíncrono con WebSockets para conectar el motor de eventos con la API de voz **Gemini Live Flash 3.1**, asegurando baja latencia en la llamada telefónica iniciada por Asterisk PBX hacia el CISO.

---

### 3. Evaluación de Evidencias de Avance
> **¿Cómo evalúas tu(s) evidencia(s) de avance? ¿Qué destacas y qué podrías hacer para mejorar tus evidencias?**

Las evidencias acumuladas hasta la fecha corresponden al Hito A1 completado y a las pruebas preliminares de arquitectura:
* Scripts testeados y validados de tuning de kernel FreeBSD (`verify_kernel_hardening.py`, `tune_loader_conf.sh`) ejecutados en Proxmox VE.
* Parche XML de pfSense CE 2.9.0 con Hardware Offloading deshabilitado para habilitar la inspección sin drop de Netmap.
* Repositorio Git estructurado con la arquitectura modular objetivo, documentación técnica oficial y Carta Gantt alineada al semestre.

**Oportunidad de mejora:** Incorporar registros de telemetría y capturas de paquetes PCAP conforme se ejecuten los hitos A2 (VLANs) y A3 (Suricata IPS) durante las próximas semanas de la Fase 2.

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
