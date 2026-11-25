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
