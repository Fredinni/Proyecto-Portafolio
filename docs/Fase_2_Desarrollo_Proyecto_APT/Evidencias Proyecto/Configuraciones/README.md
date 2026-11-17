# Exportación sanitizada de configuración pfSense

Archivo: [kronos-pfsense_config.xml](kronos-pfsense_config.xml).

Esta evidencia procede del archivo real `/conf/config.xml` del equipo `kronos-pfsense`, leído por SFTP/SSH mediante la red de gestión el **17 de noviembre de 2026 a las 18:21:42 UTC** (15:21:42 de Chile). No es una plantilla. La extracción fue de solo lectura; no se aplicó ni se restauró configuración en el firewall.

El dispositivo informa **pfSense 2.9.0-RELEASE**. El valor `24.6` del elemento XML `version` corresponde al formato de configuración, no a la versión del sistema. La fecha de modificación del archivo original era **16 de noviembre de 2026 a las 11:11:46 UTC**.

## Alcance de la copia pública

**No restaurar este archivo.** Se publica como evidencia académica de la configuración exportada. Los campos confidenciales fueron sustituidos por `[ELIMINADO_PARA_PUBLICACION]`; el respaldo completo de recuperación permanece fuera del repositorio, bajo custodia del operador.

Se conservan la estructura y las relaciones del dispositivo: 5 interfaces, 4 VLAN, 68 reglas de firewall, reglas de salida/NAT, alias, servicios, HAProxy y la configuración de Suricata en 2 interfaces. Las direcciones privadas que aparecen describen la topología del laboratorio.

Se sustituyeron **84 valores**:

| Información retirada | Valores |
| --- | ---: |
| Nombres y descripciones de cuentas de acceso | 4 |
| Hashes bcrypt de contraseña | 2 |
| Claves SSH autorizadas | 1 |
| Comunidad SNMP | 1 |
| Usuarios en los metadatos de creación y actualización de reglas | 67 |
| Usuario del registro de revisión | 1 |
| Certificados y sus claves privadas, incluida la CA | 6 |
| Cuenta y clave de licencia MaxMind | 2 |
| **Total** | **84** |

La configuración de GeoIP permanece documentada, pero la cuenta y la licencia de MaxMind no se publican. No se alteraron esas credenciales ni los servicios del laboratorio al generar esta evidencia.

## Método y verificación

1. Confirmar el perfil Tailscale autorizado, sin cambiarlo.
2. Leer el archivo real mediante SFTP con la clave del servidor SSH previamente registrada. Guardar el original únicamente en el almacenamiento privado del operador.
3. Analizar el XML y sustituir los campos de autenticación, identidades de acceso, certificados y licencias antes de escribir una copia en el repositorio.
4. Revisar patrones de claves privadas, hashes, tokens, claves API y URLs con credenciales. Decodificar también los contenidos Base64 para inspeccionarlos.
5. Comparar la copia con el original: se mantienen **2.670 elementos XML y todos sus atributos**; únicamente cambian los 84 textos enumerados. El XML resultante se vuelve a analizar correctamente.
6. Comparar la copia con 27 valores confidenciales conocidos, incluidos credenciales actuales y anteriores y el material retirado del original: sin coincidencias restantes.

SHA-256 de la copia pública:

```text
45dc7ae0eaf4a362366eef6ce6da7a081d94b0aeb3bd8b41432ef7a779f0265c
```

## Revisión de archivos de acceso

El 17 de noviembre de 2026 se revisaron los **14 archivos PHP versionados** y [TEAM_LAB_ACCESS.md](../../../TEAM_LAB_ACCESS.md). No se encontraron contraseñas actuales o anteriores conocidas incorporadas como literales en esos archivos. Los scripts de cambio de contraseña reciben el valor por entrada estándar. La guía pública de acceso se actualizó para utilizar parámetros y remitir la entrega de usuarios y credenciales al canal privado.

Como comprobación adicional se inspeccionaron 148 archivos de texto del árbol versionado buscando contraseñas conocidas y patrones de API, claves privadas, hashes, SIP/AMI y URLs autenticadas. No se detectaron secretos en claro con esos criterios. Los ejemplos de tokens enmascarados se mantuvieron como ejemplos. Esta revisión corresponde al contenido actual; no implica que se haya reescrito o eliminado el historial de Git.
