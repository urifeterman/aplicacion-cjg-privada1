# Verificación de compatibilidad — Odoo 18.0

Fecha: 25 de noviembre de 2026.

## Fuentes oficiales Odoo 18

- Portal access: https://www.odoo.com/documentation/18.0/applications/general/users/portal.html
- ORM API: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html
- Owl components en Portal/website: https://www.odoo.com/documentation/18.0/developer/howtos/frontend_owl_components.html

La documentación de Portal señala que los usuarios Portal consultan documentos de Odoo y tienen acceso de solo lectura; las credenciales son administradas por el propio Portal. La guía OWL especifica el registro en `public_components`, el bundle `web.assets_frontend` y el tag `owl-component`. La documentación ORM confirma los modelos y campos se definen/extienden por herencia.

## Código fuente público Odoo 18.0 consultado

Repositorio oficial: https://github.com/odoo/odoo/tree/18.0

| Archivo | Elementos verificados y aplicados |
|---|---|
| `addons/project/models/project_project.py` | `partner_id`, `privacy_visibility`, `date_start`, `date`, `last_update_status`, hitos y colaboradores. |
| `addons/project/models/project_task.py` | `project_id`, `stage_id`, `state`, `date_deadline`, `user_ids`, estados `1_done` y `1_canceled`. |
| `addons/project/models/project_milestone.py` | `project_id`, `deadline`, `is_reached`, `reached_date`. |
| `addons/project/models/project_update.py` | `name`, `status`, `date`, `project_id`. |
| `addons/project/security/project_security.xml` | Reglas Portal nativas para proyecto, tarea e hito. |
| `addons/mail/models/mail_message.py` | `message_type` e `is_internal` para excluir notas internas. |
| `odoo/addons/base/models/ir_binary.py` | `_find_record` y `_get_stream_from` para validar acceso y servir contenido. |
| `odoo/addons/base/models/ir_attachment.py` | `validate_access` verifica los derechos sobre el registro vinculado cuando el solicitante es Portal. |

## Decisiones técnicas derivadas

1. No se crea sistema de autenticación propio; las rutas privadas requieren `auth='user'`.
2. El frontend utiliza OWL mediante la registry pública y `web.assets_frontend`.
3. Para el avance de tareas, solo `1_done` representa trabajo finalizado; `1_canceled` queda fuera del numerador.
4. Los hitos usan `is_reached`.
5. La regla estándar Portal de Odoo para actualizaciones de proyecto no ofrece lectura general Portal. El módulo incorpora ACL de solo lectura y regla de registro adicional para actualizaciones explícitamente publicadas.
6. Se agregan reglas estrechas para que proyectos, tareas e hitos marcados para Hub puedan ser consultados por el contacto de la misma empresa comercial, manteniendo `privacy_visibility='portal'`, publicación y acceso de solo lectura.

## Límite de verificación Enterprise

La rama pública `odoo/odoo:18.0` confirma APIs y componentes generales de Odoo 18. No demuestra que Helpdesk, Documents u otras aplicaciones Enterprise estén instaladas en la base CJG, ni revela personalizaciones o reglas locales. Esos puntos solo se validan con el inventario real de la instancia destino.
