# Diario de Reflexión - Fase 2 (Proyecto APT)

**Estudiante / Representante:** Cristóbal Andre Quezada  
**Asignatura / Proyecto:** APT122

---

## 1. Seguimiento de Carta Gantt y Cumplimiento de Cronograma
> **¿Has podido cumplir todas las actividades en los tiempos definidos? ¿Qué factores han facilitado o dificultado el desarrollo de las actividades de tu plan de trabajo?**

En cuanto a los tiempos, venimos súper bien; hemos cumplido con todo lo que nos propusimos en la Carta Gantt sin atrasarnos. 

Lo que más nos ayudó fue que varios del grupo ya teníamos experiencia con Proxmox y pfSense, así que armar la base del laboratorio, meter HAProxy y dejar Suricata funcionando fue bastante rápido. 

¿Lo más difícil? Ajustar el tema de las alertas. Suricata nos generaba mucho "ruido" y falsos positivos, así que nos costó un poco sincronizar bien esos registros con los bloqueos reales de pfSense para que el sistema no saltara por cualquier cosa.

## 2. Resolución de Dificultades y Contingencias Técnicas
> **¿De qué manera has enfrentado y/o planeas enfrentar las dificultades que han afectado el desarrollo de tu Proyecto APT?**

Para solucionar el problema de las falsas alarmas, armamos una doble revisión: 
1. Primero, analizamos el tráfico directamente en el HAProxy para detectar de forma limpia si hay un intento de inyección SQL. 
2. Si vemos algo raro, el sistema hace una consulta rápida a pfSense (revisando la tabla `snort2c`) para confirmar que la IP del atacante de verdad haya sido bloqueada. 

Además, para que la alerta por voz funcione rápido, armamos una conexión por WebSockets. Así, el sistema le avisa casi al instante a la IA de Gemini Live y la llamada a través de Asterisk sale sin retrasos molestos.

## 3. Evaluación de Evidencias de Avance
> **¿Cómo evalúas tu(s) evidencia(s) de avance? ¿Qué destacas y qué podrías hacer para mejorar tus evidencias?**

Creemos que los respaldos que tenemos están súper sólidos y son 100% demostrables. Tenemos desde los pantallazos y registros de los bloqueos en vivo, hasta las grabaciones y datos técnicos de las llamadas que hace la IA. 

Además, tenemos todo el código y los contenedores ordenados en GitHub para que el proyecto se pueda replicar fácil. Como un "plus" que nos gustaría agregar después, pensamos en armar un panel visual que muestre gráficamente cuántos segundos pasan desde que entra el ataque hasta que suena el teléfono.

## 4. Inquietudes y Consultas para el Docente / Pares
> **¿Qué inquietudes te quedan sobre cómo proceder? ¿Qué pregunta te gustaría hacerle a tu docente o a tus pares?**

Tenemos una duda puntual sobre cómo prefieren que hagamos la presentación final de la Fase 3. Queremos saber qué formato les gusta más para la demostración en vivo de la llamada con la IA: ¿Suma puntos mostrar en pantalla el tráfico de red en Wireshark al mismo tiempo que se escucha la llamada en directo con Gemini Live, o es mejor enfocarnos en otra cosa para cumplir con la rúbrica?

## 5. Gestión y Distribución del Trabajo en Equipo
> **¿Consideran que las actividades deben ser redistribuidas entre los miembros del grupo? ¿Hay nuevas actividades que deban ser asignadas a algún miembro del grupo?**

Nos hemos organizado bastante bien porque repartimos las tareas según lo que cada uno maneja mejor (ya sea el tema de redes, los servidores, la telefonía o armar la documentación). Para esta etapa en específico, ya acordamos quiénes van a armar el guion para simular los ataques SQL y quiénes van a recolectar lo que falta para el informe final.

## 6. Evaluación del Trabajo Grupal
> **¿Cómo evalúan el trabajo en grupo? ¿Qué aspectos positivos destacan? ¿Qué aspectos podrían mejorar?**

Como equipo venimos funcionando excelente. Hay mucho compromiso de todos, nos comunicamos constantemente y hemos logrado mezclar bien todo lo que hemos aprendido en la carrera (redes, ciberseguridad, programación y telefonía). 

El único "tirón de orejas" que nos hacemos es que tenemos que acostumbrarnos a subir los documentos al repositorio con más frecuencia, para no andar sufriendo con versiones desactualizadas justo un día antes de entregar.