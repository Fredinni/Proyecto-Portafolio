# Guía de Configuración: MaxMind GeoIP Gratis en pfSense (pfBlockerNG-devel)
### Autor: Bruno Urrea Ortiz | KRONOS SENTINEL

---

## 1. Obtención de License Key Gratuita de MaxMind
1. Crear una cuenta gratuita en [MaxMind GeoLite2](https://www.maxmind.com/en/geolite2/signup).
2. Dirigirse a **Account > Manage License Keys**.
3. Generar una nueva clave con soporte para `GeoIP Update`.
4. Copiar la **License Key** alfanumérica generada.

---

## 2. Configuración en pfSense
1. Ingresar a la interfaz web de pfSense: `https://192.168.1.1`.
2. Navegar a **Firewall > pfBlockerNG > IP > MaxMind GeoIP configuration**.
3. Pegar la **MaxMind License Key** en el campo correspondiente.
4. En **MaxMind Country Database**, seleccionar `Enable`.
5. En **Top Spammers / High Risk Continents**, configurar acción en `Deny Inbound` o `Deny Both`.
6. Guardar cambios y ejecutar una actualización forzada en **pfBlockerNG > Update > Force Reload**.
