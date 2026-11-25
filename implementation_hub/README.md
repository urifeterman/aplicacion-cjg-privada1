# Implementation Hub — Odoo 18.0

Módulo inicial para Odoo 18.0. Es una capa de consulta sobre modelos de Proyecto y Portal existentes; no crea cuentas, contraseñas ni sesiones propias.

## Dependencias

`base`, `web`, `portal`, `project` y `mail`.

No se declara dependencia a Helpdesk ni Documents: su instalación debe comprobarse en la instancia destino antes de escribir integraciones específicas.

## Instalación

1. Copiar la carpeta `implementation_hub` a una ruta de addons del servidor.
2. Reiniciar Odoo y actualizar la lista de aplicaciones.
3. Instalar el módulo en una base de pruebas/staging Odoo 18.0 Enterprise.
4. Ejecutar las pruebas automatizadas y la matriz manual de seguridad.
5. No instalar en producción sin respaldo, validación y aprobación.

Ejemplo de pruebas desde el servidor:

```bash
odoo-bin --addons-path=/ruta/odoo/addons,/ruta/enterprise,/ruta/custom \
  -d NOMBRE_BD -i implementation_hub --test-enable --stop-after-init
```

## Configuración de publicación

Un usuario del grupo **Proyecto / Administrador** configura la pestaña **Implementation Hub** del proyecto:

1. Seleccionar alcance: Implementación o Soporte.
2. Seleccionar expresamente método de avance: hitos publicados o tareas publicadas.
3. Activar la publicación.
4. Marcar individualmente las tareas, hitos y actualizaciones que puede consultar el cliente.
5. Marcar explícitamente los adjuntos autorizados.

No se publica nada por defecto. Los proyectos sin cliente asignado nunca se muestran.

## Reglas de avance

- **Hitos publicados:** hitos visibles y alcanzados / hitos visibles.
- **Tareas publicadas:** tareas visibles con estado Odoo `1_done` / tareas visibles.
- Las tareas `1_canceled` no se cuentan como trabajo terminado.
- Un denominador vacío produce “avance no disponible”, no 0% ni 100%.
- No hay método por defecto: la selección es explícita por proyecto.

El cálculo usa solo registros publicados para evitar que el porcentaje revele el estado de trabajo interno no publicado.

## Seguridad implementada en el código

- Sesión y autenticación Portal nativas de Odoo (`auth='user'`).
- Rutas de consulta ejecutadas con el usuario real; sin elevación global a `sudo()`.
- ACL y reglas de registro para los recursos publicados, limitadas a Portal y a empresa comercial/colaborador.
- Proyecto, tarea e hito conservan los controles de Odoo; se añaden reglas Portal estrechas para registros publicados.
- Lectura de actualizaciones de proyecto concedida de forma explícita y solo lectura, con regla de publicación.
- Mensajes filtrados a `message_type='comment'` y `is_internal=False`.
- Adjuntos marcados por el equipo y servidos después de volver a validar el acceso al adjunto y al documento vinculado.
- Respuestas privadas con `Cache-Control: private, no-store`.
- Service worker sin caché de respuestas privadas, documentos ni sesiones.

## Alcance pendiente de confirmar

- **Helpdesk:** vista reservada en el prototipo; integración funcional pendiente de confirmar el módulo instalado, su modelo, campos y reglas.
- **Documents:** se implementa publicación de adjuntos vinculados a proyectos, tareas, hitos y actualizaciones. No se habilita una integración con carpetas/espacios de trabajo Documents hasta verificar esa aplicación y configuración.
- **Notificaciones push:** fuera de esta versión.
- **Edición de datos del proyecto por cliente:** no implementada.
- Perfil visible en modo solo lectura.

## Estado de validación

Este módulo se generó contrastando las APIs generales y los modelos públicos de Odoo 18.0. No ha sido instalado ni ejecutado contra una instancia CJG Enterprise desde este entorno. La compatibilidad final de vistas, módulos Enterprise, personalizaciones, permisos y pruebas end-to-end requiere esa instancia.

## Historial y administración

El menú Implementation Hub permite consultar proyectos publicados, documentos y el historial. El historial registra publicación/despublicación del proyecto, cambios de alcance y publicación/despublicación de cada recurso visible (tareas, hitos, actualizaciones y adjuntos). Las acciones de publicación quedan limitadas al grupo Proyecto / Administrador.

## PWA

Se incluye manifest, icono SVG, registro de Service Worker y una página genérica sin conexión. El Service Worker almacena únicamente esa página genérica; no almacena respuestas privadas, adjuntos, cookies ni sesiones. La caché completa de assets del portal no se ha activado para evitar ampliar el alcance del Service Worker sobre otras páginas Odoo.

## Validación automática

El workflow `.github/workflows/static-validation.yml` comprueba compilación sintáctica de Python, parseo del manifest, XML, CSV y sintaxis JavaScript. Es una validación estática del repositorio; no sustituye la instalación o pruebas dentro de Odoo 18 Enterprise.


## Integraciones Enterprise a validar

- **Helpdesk 18:** La documentación oficial indica que los usuarios Portal solo pueden consultar tickets que siguen cuando el equipo tiene la visibilidad “Usuarios del portal invitados y todos los usuarios internos”. El Hub no amplía esos permisos ni consulta tickets todavía; la integración debe conservar esos controles por equipo/ticket y la autorización nativa. Referencia: https://www.odoo.com/documentation/18.0/applications/services/helpdesk.html
- **Documents 18:** La aplicación administra permisos de carpetas y documentos de forma independiente, y los usuarios Portal acceden a elementos con permiso de lectura o edición. El módulo actual no integra ese modelo; solo lista adjuntos directamente vinculados a registros de Proyecto y marcados para publicación. Referencia: https://www.odoo.com/documentation/18.0/applications/productivity/documents.html

La integración con estas aplicaciones se debe implementar como extensión opcional después de confirmar que están instaladas y auditar sus ACL/reglas en la base CJG.

## Auditoría de la base destino

Antes de instalar en staging, ejecutar el inventario de solo lectura disponible en scripts/audit_odoo18.py. Las instrucciones están en scripts/README.md. El script permite confirmar el estado de Helpdesk/Documents, campos personalizados y reglas/ACL reales sin extraer nombres ni contenidos de clientes.


## Estado y retrasos publicados

El estado público se toma de la actualización de proyecto más reciente que el equipo marcó explícitamente como visible. No se usa `project.last_update_status`, porque puede reflejar una actualización no publicada. La alerta de retraso solo se muestra cuando existe fecha final planificada vencida y hay una actualización pública que no marca el proyecto como terminado. Sin estado público no se infiere un retraso.


## Decisión pendiente: estado de tarea y fórmula de avance

La propuesta del PDF habla de tareas en la “etapa final”. En Odoo 18, el campo `project.task.state` distingue estados operativos, incluidos `1_done` (Done) y `1_canceled` (Cancelled); `project.task.type.fold` significa que la etapa se pliega en la vista Kanban y no equivale por sí solo a una etapa final. Por eso el código usa `1_done` como numerador y excluye canceladas. El dueño funcional debe confirmar que esta interpretación corresponde al flujo CJG.

Además, tanto numerador como denominador cuentan solo elementos publicados. Esto evita revelar por porcentaje la cantidad de tareas/hitos internos ocultos, pero puede diferir de la fórmula de total de registros del borrador. Requiere aprobación funcional antes de producción.

