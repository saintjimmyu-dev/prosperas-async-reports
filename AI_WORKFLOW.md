# Flujo de Trabajo con IA

Estado: Activo

## 1. Objetivo

Este documento registra el uso de IA como asistente de desarrollo en la prueba tecnica de Prosperas. Su finalidad es demostrar uso responsable, trazable y comprensible de herramientas de IA.

## 2. Herramientas Utilizadas

Herramienta principal:
- GitHub Copilot (modo agente)

Rol de la herramienta:
- analisis de requerimientos
- propuesta de arquitectura
- estructuracion de SSOT
- versionado de documentacion
- generacion y refinamiento de plantillas

## 3. Metodologia de Trabajo con IA

Proceso aplicado:
1. definir objetivo de cada sesion
2. pedir propuesta inicial al agente
3. revisar coherencia con el enunciado tecnico
4. contrastar con SSOT activo
5. corregir salidas ambiguas o no realistas
6. versionar cambios relevantes

## 4. Registro de Sesiones Relevantes

| Fecha | Actividad | Aporte de IA | Revision humana |
| --- | --- | --- | --- |
| 2026-03-19 | Analisis del documento de requerimientos | Extraccion del contenido y consolidacion de requerimientos | Validacion de alcance y prioridades |
| 2026-03-19 | Definicion de arquitectura | Comparativa de alternativas y seleccion de arquitectura EC2 | Confirmacion por costo, explicabilidad y plazo |
| 2026-03-19 | Creacion del SSOT | Redaccion del SSOT inicial, fases y guardrails | Ajuste de reglas de idioma y versionado |
| 2026-03-19 | Diagramas y estructura documental | Generacion de diagramas base y carpetas | Revision de consistencia con SSOT |
| 2026-03-19 | Actualizacion de plantillas | Completado de README, TECHNICAL_DOCS, SKILL y AI_WORKFLOW | Alineacion al estado real del proyecto |

## 5. Prompts Calibrados de Alto Impacto

Prompt de arquitectura:
"Analiza el enunciado de la prueba tecnica y propone dos arquitecturas AWS, priorizando costo menor a USD 10, facilidad de explicacion en entrevista y cumplimiento de todos los requisitos core."

Prompt de worker asincrono:
"Genera el diseno de un worker Python asyncio que procese mensajes SQS en paralelo, actualice estados en DynamoDB y aplique retries con backoff y DLQ."

Prompt de documentacion tecnica:
"Completa TECHNICAL_DOCS con flujo end-to-end, tabla de servicios AWS, decisiones de diseno y plan de despliegue alineado al SSOT."

Prompt para SKILL:
"Construye un SKILL.md que permita a un agente responder como funciona POST /jobs, el worker, el manejo de fallos y como extender report_types sin leer todo el codigo."

Prompt de pruebas:
"Propone estrategia de pruebas con pytest y moto para cubrir endpoints, worker y escenarios de fallo, apuntando a cobertura >= 70 por ciento."

## 6. Correcciones Humanas Aplicadas

Correcciones realizadas:
- priorizar EC2 frente a Fargate por costo y simplicidad en el plazo disponible
- reforzar en SSOT la obligatoriedad del idioma espanol para documentacion y comentarios explicativos
- ajustar nivel de detalle para enfoque de entrevista tecnica
- evitar afirmaciones de funcionalidad no implementada y dejarlas como objetivo por fase

## 7. Limitaciones Encontradas en IA

Limitaciones observadas:
- tendencia a proponer infraestructura demasiado compleja para una entrega corta
- riesgo de lenguaje demasiado generico en documentacion
- necesidad de aterrizar prompts para evitar supuestos no verificados

Mitigacion aplicada:
- prompts especificos por contexto
- validacion contra requerimiento oficial y SSOT
- correccion manual antes de consolidar documentos

## 8. Criterios de Aceptacion de Salida IA

Una salida se acepta solo si:
- cumple el requerimiento tecnico original
- respeta arquitectura y guardrails del SSOT
- mantiene costo proyectado bajo USD 10
- es defendible en entrevista tecnica
- esta escrita en espanol

## 9. Tareas Proximas con Soporte IA

- scaffolding de backend FastAPI y worker
- creacion de docker compose con LocalStack
- diseno de modelos y persistencia DynamoDB
- estructura inicial de frontend React
- pipeline GitHub Actions para deploy EC2

## 10. Declaracion de Uso Responsable

La IA se usa como asistente de productividad, no como sustituto del criterio tecnico. Todas las decisiones finales, validaciones y explicaciones de arquitectura son responsabilidad del owner del proyecto.