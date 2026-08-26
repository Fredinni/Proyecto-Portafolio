# GUÍA DE ROL Y MANUAL OPERATIVO: HARDENING PERIMETRAL, INTELIGENCIA PFBLOCKERNG Y CONTROL DE CALIDAD (QA)
## Integrante: Kevin Retamales
**Carrera:** Ingeniería en Conectividad y Redes — Duoc UC Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122) — Proyecto KRONOS SENTINEL  
**Rol Oficial:** *Hardening Perimetral, Listas de Inteligencia de Amenazas pfBlockerNG y Control de Calidad*

---

## 1. MISIÓN Y RESPONSABILIDADES PRINCIPALES

Como Especialista en Hardening, Inteligencia de Amenazas y QA de KRONOS SENTINEL, eres el responsable de la **primera línea de defensa en firewall, las listas de reputación global y el aseguramiento de calidad**:

1. **Hardening del Firewall pfSense CE 2.9.0:**
   * Auditar la matriz de reglas de filtrado en todas las interfaces, aplicando la política de *Deny All Implicit*.
   * Garantizar el aislamiento de las redes de gestión (VLAN 99) y corporativa (VLAN 10), impidiendo movimientos laterales desde la DMZ.
   * Desactivar servicios y puertos innecesarios en pfSense (SSH accesible únicamente desde VLAN 99 / Consola segura).
2. **Inteligencia de Amenazas y Filtrado Geográfico (pfBlockerNG-devel):**
   * Configurar y mantener la integración con la base de datos comunitaria gratuita **MaxMind GeoLite2** ($0 CLP).
   * Administrar las listas de bloqueo por país (*Top Spammers* e infraestructura hostil: CN, RU, IR, KP, VN, NG) en modo regla flotante *Deny Inbound*.
   * Integrar y auditar los feeds de reputación IP de alta severidad: **FireHOL Level 1** (botnets, C2 y atacantes activos) y **Spamhaus DROP/EDROP**.
3. **Aseguramiento de Calidad y Pruebas de Estrés (QA):**
   * Diseñar y ejecutar matrices de pruebas funcionales antes de la presentación final.
   * Validar que el flujo completo (Ataque SQLi ➔ Suricata Inline Drop ➔ Tabla `snort2c` ➔ Disparo Asterisk ➔ Voz Gemini) se ejecute en menos de 1.5 segundos.

---

## 2. CHECKLIST PASO A PASO PARA EL DESPLIEGUE TÉCNICO

### Fase A: Verificación de Listas de Amenazas pfBlockerNG
```bash
# Comprobar el estado de las tablas de pfBlockerNG en pfSense:
pfctl -s Tables | grep pfB_

# Ver las IPs bloqueadas por el feed FireHOL Level 1:
pfctl -t pfB_FireHOL_L1 -T show | head -n 20
```

### Fase B: Comprobación de Logs de Bloqueo GeoIP
```bash
# Monitorear bloqueos en tiempo real de pfBlockerNG:
tail -f /var/log/pfblockerng/ip_block.log
```

### Fase C: Matriz de Control de Calidad y Pruebas de Intrusión (QA)
| Escenario de Prueba | Acción Ejecutada | Resultado Esperado | Estado QA |
| :--- | :--- | :--- | :--- |
| **Test 1: Bloqueo GeoIP** | Petición HTTP desde IP de rango bloqueado (ej. feed FireHOL) | Descarte perimetral inmediato antes de llegar a HAProxy | **PASS** |
| **Test 2: Inline IPS Suricata** | Inyección SQL `admin' OR '1'='1 --` hacia HAProxy VIP | Drop en Netmap, registro en `eve.json` y adición a `snort2c` | **PASS** |
| **Test 3: Supresión Ruido** | Escaneo simple de puertos `nmap -sS -p 80,443` | Detección en firewall pero supresión en motor (sin llamada) | **PASS** |
| **Test 4: Latencia de Alerta** | Ataque crítico validado ➔ Timbrado telefónico softphone | Timbrado en softphone PJSIP/1001 en menos de 1.5 segundos | **PASS** |

---

## 3. GUÍA DE DEFENSA ANTE LA COMISIÓN EVALUADORA (PREGUNTAS CLAVE)

### P1: "¿Cómo garantizan que las listas de pfBlockerNG no bloqueen tráfico legítimo de la institución?"
* **Respuesta Senior:** *"Profesor, pfBlockerNG se configuró con reglas de Deny Inbound únicamente para listas de máxima certeza (FireHOL Level 1 y Spamhaus DROP), que contienen direcciones IP de botnets y centros de comando comprobados. Además, se aplican listas de excepción (whitelisting) para los rangos corporativos y los servicios de Google Cloud."*

### P2: "¿Por qué se eligió la versión libre de MaxMind GeoLite2 y qué costo representa para el proyecto?"
* **Respuesta Senior:** *"MaxMind ofrece licencias comunitarias gratuitas para fines académicos y de investigación. Implementamos la integración oficial en pfSense con un Account ID gratuito, cumpliendo al 100% el requerimiento institucional de Costo Cero ($0 CLP) sin renunciar a precisión geográfica de nivel empresarial."*
