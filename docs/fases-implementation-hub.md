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
