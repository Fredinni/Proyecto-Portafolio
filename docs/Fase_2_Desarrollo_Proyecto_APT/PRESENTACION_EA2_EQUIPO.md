# Presentación recomendada — Evaluación 2

Entrega ampliada a **cinco diapositivas**, por indicación del equipo: las tres de la pauta más dos anexos de pruebas con screenshots. Corte de evidencia: **2 de octubre de 2026**.

- [PowerPoint editable](Evaluacion2_Avance_S7_Equipo_5_Slides_2026-10-02.pptx)
- [PDF](Evaluacion2_Avance_S7_Equipo_5_Slides_2026-10-02.pdf)
- [Banco de imágenes para adaptar la presentación](../../evidencias/README.md)
- [Informe completo de pruebas y correcciones](AVANCE_SEMANA7_2026-10-02.md)
- [Gantt oficial](Informacion_EA2/Plan_Trabajo_Carta_Gantt.md)

Esta versión reemplaza la recomendación de usar la presentación anterior `Evaluacion2_Avance_Semana7_2026-10-02`. Las versiones anteriores de tres diapositivas permanecen como registro histórico.

## Relación con la pauta

| Diapositiva | Contenido solicitado | Respaldo |
|---|---|---|
| 1 · Ejecución | Tareas técnicas, responsables, fechas Gantt, porcentaje, estado y evidencia; Gantt reducida con marcador del corte; desviaciones y correcciones | Cronograma oficial e informe de avance |
| 2 · Entregables | Entregables vinculados a tareas, criterios de aceptación medibles y fechas; ajustes desde Fase 1 con su justificación | Criterios del proyecto y pruebas documentadas |
| 3 · Verificación | Topología del laboratorio real, herramientas, tres pruebas con esperado/obtenido y capturas; alcance que falta simular | Capturas nativas y resultados medidos |
| 4 · Base y conectividad | Screenshots de auditoría A1, DHCP/aislamiento A2 y transporte/administración | Resultados reales con fecha, criterio y fuente |
| 5 · Protección | Screenshots de descartes IPS, arranque/fallos y bloqueos de reputacion/GeoIP | Registros y contadores medidos; pruebas completas enlazadas |

La presentación acredita resultados concretos, sin prometer una calificación ni una garantía universal de funcionamiento. Los porcentajes corresponden al alcance documentado; las tareas futuras no se presentan como pruebas completadas.

## Guion breve sugerido

1. **Qué construimos y quién responde por cada parte:** explicar el cierre de la base de red y protección hasta S7. Reconocer que la validación de A2 y A3 ocurrió después de sus fechas planificadas y describir las correcciones.
2. **Qué debe entregar el proyecto:** distinguir entregables actuales de las integraciones posteriores. Explicar por qué AWS transporta el tráfico y pfSense conserva la función de firewall, y por qué la administración del equipo usa una tailnet separada.
3. **Qué demostramos:** contrastar resultados esperados y obtenidos de segmentación, descarte IPS y reputación/GeoIP. Cerrar con las pruebas futuras de HTTPS, respuesta automatizada, voz/IA y rendimiento integral.

4. **Anexo de base y conectividad:** mostrar auditoría compatible A1, pruebas DHCP/segmentación A2 y preservacion de la IP del cliente entre WireGuard y Ethernet.
5. **Anexo de protección:** mostrar los descartes en ambos sensores, los ensayos de reinicio/fallos y los incrementos de contadores de A4. Diferenciar configuración, prueba puntual y objetivos futuros.

Los responsables son los asignados en la Gantt. La ejecución de automatizaciones no prueba por sí sola participación personal. A10 conserva su carácter de trabajo del equipo, con Kevin como referente de QA según su rol en el proyecto.

Las capturas muestran el estado en su fecha, no una medición en vivo al abrir la PPT. Una captura de configuración acredita un ajuste; los resultados de tráfico y contadores acreditan su funcionamiento dentro del ensayo descrito. Los resúmenes de comandos se identifican como transcripciones, no como capturas nativas de terminal.
