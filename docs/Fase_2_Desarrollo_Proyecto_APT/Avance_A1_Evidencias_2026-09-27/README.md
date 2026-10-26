# Evidencias de la mini presentación A1

Capturadas el 27/09/2026, hora local de Chile. El dashboard pfSense muestra
28/09 en UTC. Se realizaron consultas y navegación de solo lectura: no se
configuró A2 durante esta entrega.

La presentación tiene siete diapositivas, texto editable y capturas reales:
versión e interfaces de pfSense, controles de offloading y transporte WireGuard.
La diapositiva 6 reserva recuadros editables para la evidencia de A2 de Freddy.
Las imágenes de comandos son transcripciones visuales
de stdout obtenido por SSH; no se presentan como capturas de una consola nativa.
El Device ID Netgate está oculto. No se incluyen contraseñas, claves privadas o PSK.

## Estados académicos

- A1: Bruno/Freddy; completado según Carta Gantt histórica. En la plataforma
  actual se comprobó red y offloading, con revalidación de tuning parcial.
- A2: Freddy; el equipo informa que Freddy la tiene lista y dispone de
  evidencia propia. No se recibió ni revisó esa evidencia durante esta entrega;
  se reserva espacio para integrarla. No se modificó la configuración de A2.

La presentación final incluye solamente los avances de Bruno y Freddy.
Las capturas DVWA auxiliares de esta carpeta no forman parte de la PPT final.

## Observaciones actuales

pfSense CE 2.9: WAN activa; tres offloads deshabilitados; nmbclusters=1000000;
intr_queue_maxlen=1000; states_hashsize=262144; fastforwarding no existe como OID;
/dev/netmap existe. No se declara Suricata Inline probado.

Edge: forwarding=1, policy routing tabla51820, handshake reciente, ping AWS2/2
y pfSense2/2. DVWA login devolvió HTTP200. La persistencia y base MariaDB
citadas en la PPT corresponden a pruebas del 23/09, identificadas por fecha.

Fuentes académicas: Carta Gantt oficial y guías de roles. Las fuentes por
diapositiva se incluyen en notas de la PPT y `fuentes-y-alcance.json`.

`Presentacion.html` permite visualizar la misma composición en un navegador;
`Slide-01.png` a `Slide-07.png` son previsualizaciones. El PDF y la PPTX finales
se encuentran en la carpeta superior.
