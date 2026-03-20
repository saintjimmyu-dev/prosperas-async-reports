# Historial del SSOT

## 2026-03-20 - v1.0.6

- Se actualizo el estado global del SSOT para declarar Fase 3 como validada.
- Se documento el frontend React dockerizado con login JWT demo, formulario de jobs, badges de estado, polling y layout responsive.
- Se agrego la ruta oficial de validacion local de Fase 3 en local/scripts/testing/phase3_runtime_validate.sh.

## 2026-03-20 - v1.0.5

- Se actualizo el estado global del SSOT para declarar Fase 2 como validada.
- Se incorporo el estado actual de Fase 2 con evidencia de worker concurrente, transiciones de estado, B1 (prioridad), B4 (backoff) y DLQ.
- Se formalizo el estandar de nombres por fase para scripts de validacion bajo local/scripts/testing con prefijo phaseN.
- Se actualizaron las rutas oficiales de scripts hacia phase1_runtime_validate.sh y phase2_runtime_validate.sh.

## 2026-03-20 - v1.0.4

- Se establecio como regla del SSOT que todo script de pruebas tecnicas y validacion runtime debe vivir en local/scripts/testing.
- Se actualizo la referencia de validacion de Fase 1 para usar local/scripts/testing/runtime_validate.sh como ruta oficial.
- Se ordeno la estructura objetivo del repositorio para incluir local/scripts/testing y evitar archivos sueltos en local.

## 2026-03-19 - v1.0.3

- Se actualizo el SSOT para declarar Fase 1 como completada y validada en runtime local.
- Se incorporo el estado de validacion end to end con local/runtime_validate.sh y los endpoints de smoke test.
- Se documento explicitamente que la asociacion formal de RedrivePolicy con DLQ queda en Fase 2.

## 2026-03-19 - v1.0.0

- Se creo la constitucion inicial del SSOT para la prueba tecnica de Prosperas.
- Se fijo la arquitectura seleccionada como Arquitectura Event-Driven Contenerizada sobre EC2.
- Se agregaron fases de entrega, guardrails de costo AWS, estructura de diagramas, mapeo de rubrica y catalogo de prompts.
- Se declaro la fase final opcional de Terraform con el requisito de verificar documentacion actual de HashiCorp antes de implementarla.

## 2026-03-19 - v1.0.1

- Se tradujo al espanol el contenido documental inicial del proyecto.
- Se agrego la regla explicita de generar documentacion del proyecto en espanol.

## 2026-03-19 - v1.0.2

- Se fijo en el SSOT que toda documentacion y todo comentario explicativo del codigo deben escribirse en espanol.
- Se alinearon las instrucciones del proyecto con la nueva regla global de idioma.
- Se agregaron plantillas base en espanol para README.md, TECHNICAL_DOCS.md, SKILL.md y AI_WORKFLOW.md.