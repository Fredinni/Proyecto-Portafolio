# Acceso autorizado al laboratorio KRONOS

Esta guía pública describe el procedimiento de acceso del equipo. Los destinos de administración, nombres de usuario, contraseñas, claves y certificados de confianza se entregan por el canal privado del operador. El inventario de credenciales permanece fuera de Git.

## Preparación

1. Solicitar al operador acceso a la tailnet del equipo y únicamente a la VM necesaria para la actividad.
2. Iniciar sesión en Tailscale con la cuenta autorizada y aceptar las rutas del laboratorio. Revisar `tailscale status` antes de cambiar perfiles para no interrumpir otras sesiones.
3. Obtener por el canal privado el destino de MGMT, el usuario asignado y la huella SSH o el certificado de confianza correspondiente.

## Comprobación

Los siguientes comandos usan parámetros que cada integrante completa con su entrega privada:

```powershell
$mgmt = "<destino-MGMT-autorizado>"
$usuario = "<usuario-asignado>"
tailscale ping $mgmt
ssh "$usuario@$mgmt"
```

Acceder a la WebGUI de pfSense mediante la URL privada entregada por el operador. Verificar el certificado antes de ingresar credenciales. La interfaz de administración debe permanecer restringida a la red de gestión.

Para administrar una VM, utilizar su destino privado y la credencial específica de esa VM. No reutilizar la contraseña de otro equipo. Registrar origen, destino, puerto y hora si falla una conexión; estos datos permiten revisar rutas y reglas sin compartir secretos.

## Alcance de red

MGMT actúa como router de subred hacia las VLAN autorizadas. El acceso a DMZ, VOIP, CORP y al tránsito de Edge queda sujeto a las reglas de pfSense. La tailnet del equipo no concede acceso al hipervisor y no sustituye el transporte público del laboratorio por WireGuard.

El acceso administrativo a Proxmox corresponde al operador de infraestructura. Las tareas de mantenimiento se describen en [la guía de despliegue](PROXMOX_ONPREM_DEPLOYMENT.md), sin conceder permisos adicionales al equipo.

## Manejo de credenciales

- Mantener contraseñas, claves privadas, tokens, credenciales SIP y licencias fuera del repositorio y de sus capturas de pantalla.
- Entregar a cada integrante solamente el acceso que requiere, mediante un canal privado.
- Los scripts PHP que establecen contraseñas las reciben por entrada estándar; nunca incluirlas como literales, argumentos o ejemplos publicados.
- Si se detecta una credencial publicada, retirarla y revocarla o rotarla en el servicio afectado. Borrar el texto del último commit no revoca su uso.
- Antes de publicar un respaldo, eliminar hashes de contraseña, claves, usuarios de acceso, certificados y licencias. La copia pública sanitizada sirve como evidencia y no como respaldo de recuperación.

Revisión documental: 17 de noviembre de 2026. Esta revisión describe el acceso autorizado; la disponibilidad de cada servicio debe comprobarse durante la actividad correspondiente.
