# Auditoría de instancia Odoo 18

El archivo audit_odoo18.py es un inventario de solo lectura para ejecutar dentro de una consola Odoo autenticada. No crea, escribe ni elimina registros. No exporta nombres, correos, descripciones, mensajes ni documentos de clientes.

## Ejecución

Desde la raíz de la instalación de Odoo, usando la misma configuración de addons con la que inicia la instancia:

    ./odoo-bin shell -d NOMBRE_BD --addons-path=/ruta/odoo/addons,/ruta/enterprise,/ruta/custom

Dentro de la consola Odoo:

    exec(open("/ruta/al/repositorio/scripts/audit_odoo18.py", encoding="utf-8").read())

El script imprime un JSON. Guarda la salida completa en un archivo local y compártela para completar la fase 1. Antes de compartir, puedes revisar el JSON; no contiene valores de clientes, pero sí metadatos técnicos como nombres de modelos, módulos, reglas y conteos agregados.

## Información recopilada

- Versión de Odoo y si la URL base está configurada con HTTPS.
- Estado/versión de módulos base, web, portal, website, mail, project, project_enterprise, helpdesk y documents.
- Existencia de modelos y campos relevantes de Proyectos, Tareas, Hitos, Actualizaciones, Portal, Helpdesk y Documents.
- Cantidad de usuarios Portal (sin nombres ni correos).
- Conteos agregados de proyectos, tareas, hitos, actualizaciones, tickets y documentos.
- Modelos/campos personalizados definidos manualmente.
- ACL y reglas de registro aplicables a los modelos auditados.

La auditoría no reemplaza pruebas de acceso con dos usuarios Portal reales ni la revisión de adjuntos y mensajes. Esos casos forman parte de la matriz de pruebas de staging.
