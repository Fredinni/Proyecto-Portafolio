# GUÍA DE ROL Y MANUAL OPERATIVO: ADMINISTRACIÓN DE SERVICIOS WEB, PROXY INVERSO HAPROXY Y LABORATORIO DMZ
## Integrante: Cristóbal Quezada
**Carrera:** Ingeniería en Conectividad y Redes — Duoc UC Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122) — Proyecto KRONOS SENTINEL  
**Rol Oficial:** *Administración de Servicios Web, Proxy Inverso HAProxy y Laboratorio DVWA*

---

## 1. MISIÓN Y RESPONSABILIDADES PRINCIPALES

Como Administrador de Servicios Web y DMZ de KRONOS SENTINEL, eres el responsable de la **capa de publicación de aplicaciones, la terminación SSL/TLS y el entorno de pruebas vulnerable en DMZ**:

1. **Gestión del Proxy Inverso HAProxy 2.8+ Community Edition:**
   * Configurar el Frontend HTTPS (puerto TCP 443 en WAN VIP) con terminación y descarga SSL/TLS (*SSL Offloading*).
   * Administrar las *Stick-Tables* en memoria RAM para mitigación de ataques DoS de capa de aplicación y *fuzzing* L7.
   * Configurar las ACLs (*Access Control Lists*) para responder `429 Too Many Requests` ante tasas anormales de peticiones (>100 reqs/10s) y `403 Forbidden` ante ráfagas de errores 4xx (>25 errores/10s).
2. **Despliegue y Aislamiento del Laboratorio DVWA (Damn Vulnerable Web App):**
   * Gestionar el contenedor Docker de DVWA (`src/haproxy_dvwa/docker-compose.dvwa.yml`) ubicado en la VLAN 20 (`192.168.20.50:80`).
   * Configurar el nivel de seguridad de DVWA en `Low` / `Medium` para permitir la inyección de payloads de prueba controlados (SQLi, XSS, Command Injection) durante la demostración presencial.
3. **Health-Checks y Monitoreo del Backend:**
   * Configurar chequeos de salud activos (*HTTP GET /index.php*) para asegurar disponibilidad permanente del servidor web de pruebas.

---

## 2. CHECKLIST PASO A PASO PARA EL DESPLIEGUE TÉCNICO

### Fase A: Despliegue del Contenedor Web DVWA en DMZ
```bash
# 1. Acceder al directorio del servicio web:
cd src/haproxy_dvwa

# 2. Iniciar el laboratorio DVWA en segundo plano:
docker compose -f docker-compose.dvwa.yml up -d

# 3. Comprobar que DVWA responda localmente en el puerto 8080/80:
curl -I http://127.0.0.1:8080/login.php
```

### Fase B: Validación de HAProxy en pfSense
```bash
# Comprobar la configuración de HAProxy desde la consola de pfSense:
haproxy -c -f /var/etc/haproxy/haproxy.cfg

# Verificar estadísticas del socket administrativo de HAProxy:
echo "show info" | socat stdio /var/run/haproxy.socket
echo "show stat" | socat stdio /var/run/haproxy.socket
```

### Fase C: Prueba de Rate Limiting y Detección de Fuzzing L7
```bash
# Simular ráfaga de peticiones para activar la stick-table en HAProxy:
for i in {1..120}; do curl -s -o /dev/null -w "%{http_code}\n" https://198.51.100.1/dvwa/ -k; done
```

---

## 3. GUÍA DE DEFENSA ANTE LA COMISIÓN EVALUADORA (PREGUNTAS CLAVE)

### P1: "¿Por qué se utiliza HAProxy como proxy inverso frente a DVWA en lugar de exponer DVWA directamente en la WAN?"
* **Respuesta Senior:** *"Profesor, exponer un servidor web vulnerable directamente a la WAN sin proxy inverso viola las directrices de arquitectura segura. HAProxy actúa como punto de terminación SSL, oculta la IP real del servidor de backend (`192.168.20.50`), normaliza las cabeceras HTTP y ejecuta rate-limiting en microsegundos mediante stick-tables en memoria RAM antes de que el tráfico toque la aplicación."*

### P2: "¿Cómo opera la stick-table de HAProxy para frenar ataques de fuerza bruta o escaneos automáticos?"
* **Respuesta Senior:** *"La stick-table almacena la tasa de peticiones y códigos de error HTTP de cada IP cliente en una ventana de 10 segundos (`store http_req_rate(10s),http_err_rate(10s)`). Si un scanner dispara más de 25 errores 404 o supera 100 peticiones en 10 segundos, HAProxy bloquea la conexión inmediatamente devolviendo códigos 429 o 403, reduciendo la carga sobre Suricata."*
