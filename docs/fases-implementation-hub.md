# Fases — Implementation Hub

Fecha: 25 de noviembre de 2026  
Rama: `test`

## Fase 1. Auditoría

**Estado: parcial.**

- El repositorio antes del desarrollo contenía solamente `.gitignore` y la auditoría inicial.
- APIs generales y modelos públicos de Odoo 18.0 contrastados con documentación y código fuente.
- Pendiente auditar la base CJG Enterprise real: aplicaciones instaladas, personalizaciones, campos, grupos, usuarios Portal, reglas, multiempresa, HTTPS y configuración.

## Fase 2. Propuesta funcional y prototipo navegable

**Estado: prototipo inicial implementado; aprobación funcional pendiente.**

- Dashboard con indicadores de proyectos publicados.
- Mis implementaciones y detalle.
- Progreso, hitos, tareas, actualizaciones y línea de tiempo.
- Cronograma y documentos adjuntos autorizados.
- Perfil de solo lectura y cierre de sesión nativo.
- Sección Tickets visible como pendiente de integración, a la espera de confirmar Helpdesk.

## Fase 3. Arquitectura y plan

**Estado: arquitectura inicial implementada en código; aprobación final pendiente.**

- Módulo Odoo `implementation_hub`.
- Controladores HTTP de sesión nativa.
- OWL en `web.assets_frontend`.
- Extensión de modelos Proyecto, Tarea, Hito, Actualización y Adjunto.
- Un solo modelo nuevo: historial de publicación.
- ACL y reglas Portal, con publicación explícita.
- PWA con página genérica offline y sin caché de datos privados.
- Falta contrastar la solución con la configuración real de la base y aprobar las decisiones pendientes.

## Fase 4. Desarrollo

**Estado: primera versión de módulo subida a la rama `test`.**

- Publicación por proyecto, alcance y método de avance.
- Publicación individual de tareas, hitos y actualizaciones.
- Historial de publicación.
- Portal OWL responsive, resumen, detalle, cronograma y documentos publicados.
- Rutas protegidas para datos y adjuntos.
- Tickets/Helpdesk y Documents app pendientes de auditoría de instalación y permisos.
- No está instalado en una instancia Odoo desde este entorno.

## Fase 5. Pruebas

**Estado: pruebas automatizadas iniciales escritas; ejecución pendiente.**

Se incluyen pruebas para exigir alcance y método de avance antes de publicar, excluir proyectos sin cliente del dominio de portal y mostrar avance no disponible cuando no hay registros publicados.

No se reporta ninguna prueba como ejecutada. En staging Odoo 18 Enterprise se debe ejecutar:

- instalación/actualización del módulo y carga de vistas;
- aislamiento entre dos empresas comerciales;
- contacto de empresa y colaborador frente a usuario no autorizado;
- tareas e hitos visibles/no visibles;
- comentarios públicos frente a notas internas;
- adjuntos válidos, adjuntos ajenos y acceso directo por URL;
- exclusión de horas, costos, márgenes y otros clientes;
- Service Worker, HTTPS y ausencia de caché privada;
- Helpdesk y Documents si están instalados.

## Fase 6. Entrega

**Estado: entrega de código inicial y documentación; cierre pendiente.**

Se incluye README técnico, verificación de compatibilidad y estado de fases. Falta ejecutar la batería en la instancia real, completar matriz de permisos, manual de usuario, aprobación de negocio y autorización de producción.

## Decisiones originales aún abiertas

El documento de alcance deja pendientes:
1. Resultado de auditoría de módulos, modelos personalizados y usuarios Portal.
2. Regla por defecto del avance. Esta implementación exige una selección explícita por proyecto y no inventa un valor por defecto.
3. Alcance: Implementación o también Soporte. Se ofrece selección por proyecto; el dueño del producto debe confirmar la política inicial.
4. Datos de prototipo de ejemplo o reales tras auditoría. Esta primera versión consulta datos reales ya publicados, pero requiere validación en staging.


## Matriz de pruebas pendiente de ejecución en la instancia destino

| Caso | Resultado esperado | Estado |
|---|---|---|
| Instalar/actualizar módulo en Odoo 18 Enterprise | Manifiesto, ACL, reglas, vistas y assets cargan sin error | Pendiente |
| Publicar proyecto sin cliente | No aparece en el Portal | Pendiente de ejecutar |
| Publicar proyecto sin alcance o método de avance | El servidor rechaza la publicación | Prueba escrita; ejecución pendiente |
| Portal de empresa A consulta proyecto de empresa B | No encontrado / no aparece | Pendiente de ejecutar |
| Colaborador autorizado abre proyecto compartido | Solo ve recursos publicados y autorizados | Pendiente de ejecutar |
| Tarea/hito/actualización con visibilidad desactivada | No aparece en listas ni endpoints | Pendiente de ejecutar |
| Nota interna del chatter | Nunca aparece en la línea de tiempo | Pendiente de ejecutar |
| Comentario público autorizado | Puede aparecer en línea de tiempo | Pendiente de ejecutar |
| Adjunto no marcado o adjunto de recurso no visible | Descarga rechazada / not found | Pendiente de ejecutar |
| Adjunto marcado cuyo registro padre no es accesible | Descarga rechazada / not found | Pendiente de ejecutar |
| Proyecto sin fecha final | No se muestra retraso | Pendiente de ejecutar |
| Progreso sin elementos publicados | Se muestra no disponible | Prueba escrita; ejecución pendiente |
| Service Worker fuera de conexión | Solo se presenta la página genérica offline; no hay datos privados | Pendiente de ejecutar |
| Inspección de campos internos | Horas, costos, márgenes y notas privadas ausentes del payload | Pendiente de ejecutar |

El workflow de GitHub Actions de validación estática completó con resultado `success` para el commit `d1eaee8165a65884d605f0b8fee02b7cdfe41365`. Verificó compilación de Python (módulo y script de auditoría), parseo del manifiesto, XML/CSV y sintaxis JavaScript. Esto confirma validación estática del repositorio; no equivale a instalar el módulo ni ejecutar pruebas dentro de Odoo Enterprise.


## Limitaciones funcionales conocidas de esta primera versión

- Helpdesk: el menú existe como sección informativa, pero no hay consulta de tickets. Cuando se integre, debe conservar la regla de Odoo 18: el Portal solo consulta tickets que sigue en equipos con visibilidad Portal habilitada.
- Documents: no se consulta el modelo de la aplicación Documents ni sus espacios de trabajo. Se listan solamente adjuntos directos marcados en proyecto/tarea/hito/actualización.
- No se publica el nombre de asignados internos como “responsable público”: el documento no define qué identidades del equipo pueden exponerse. La línea de tiempo presenta estados y comentarios que son públicos.
- Notificaciones push quedan fuera de esta fase según el alcance original.
- El avance usa exclusivamente elementos publicados como numerador y denominador. Es una elección conservadora para no revelar la cantidad/estado de elementos ocultos; requiere aprobación funcional frente a la fórmula propuesta en el PDF.

- Se añadió scripts/audit_odoo18.py, un inventario de solo lectura para identificar módulos, modelos, campos, ACL, reglas y disponibilidad de Helpdesk/Documents en la base destino.
- Pendiente: ejecutar ese script contra la base CJG Enterprise real y revisar su JSON de salida.


## Decisión sobre cálculo del avance que requiere aprobación

El PDF usa la expresión “tareas en etapa final”. El código Odoo 18 confirma los estados terminales `1_done` (Done) y `1_canceled` (Cancelled), mientras que `project.task.type.fold` solo describe el plegado Kanban. La implementación cuenta `1_done` y no cuenta `1_canceled`; no usa `fold=True` como señal de finalización. Esta interpretación debe confirmarse con el flujo CJG.

La implementación también calcula sobre elementos visibles/publicados, tanto en numerador como en denominador, para no filtrar el volumen de trabajo interno. El borrador original plantea el total de hitos/tareas del proyecto; la diferencia debe ser aprobada antes de cerrar la fase 3.

