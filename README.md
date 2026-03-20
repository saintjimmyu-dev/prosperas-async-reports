# Prosperas - Sistema de Procesamiento Asincrono de Reportes

Estado: Fase 3 validada

## 1. Resumen Ejecutivo

Este repositorio contiene la solucion para la prueba tecnica de Prosperas. El objetivo del sistema es recibir solicitudes de reportes sin bloquear al usuario, procesarlas de forma asincrona y reflejar su estado en el frontend en tiempo real.

La arquitectura seleccionada es Arquitectura Event-Driven Contenerizada sobre EC2, definida como decision oficial en [SSOT.md](SSOT.md).

## 2. Objetivo de la Entrega

- cumplir la totalidad de requerimientos core del enunciado
- maximizar bonus sin comprometer estabilidad de la entrega
- mantener costos AWS por debajo de USD 10
- demostrar decisiones tecnicas defendibles en entrevista

## 3. Arquitectura Seleccionada

Componentes principales:
- API FastAPI para exponer endpoints y publicar jobs
- Worker concurrente para consumir mensajes y procesar reportes
- Amazon SQS como canal de mensajeria asincrona
- Amazon DynamoDB para persistencia del estado de jobs
- Frontend React para solicitud y seguimiento de reportes
- LocalStack para emulacion local de AWS
- EC2 para ejecucion en produccion

Diagrama de referencia:
- [docs/diagrams/architecture/system-architecture.md](docs/diagrams/architecture/system-architecture.md)

## 4. Requerimientos Core Cubiertos por Diseno

- POST /jobs con respuesta inmediata y estado inicial PENDING
- desacoplamiento API y worker mediante cola AWS
- procesamiento concurrente de al menos 2 jobs en paralelo
- persistencia de estados PENDING, PROCESSING, COMPLETED, FAILED
- estrategia de resiliencia con retry y DLQ
- actualizacion de estado en frontend sin recarga de pagina
- pipeline CI/CD con despliegue automatico a AWS

## 5. Bonus Planificados

Orden de prioridad definido:
- B1 prioridad de mensajes
- B4 retry con backoff exponencial
- B5 observabilidad
- B3 notificaciones push en tiempo real
- B2 circuit breaker
- B6 cobertura avanzada de pruebas

## 6. Plan de Trabajo (5 dias activos + 2 buffer)

- Dia 1: backend base, JWT, endpoints core y LocalStack
- Dia 2: SQS, worker concurrente, transiciones de estado, DLQ
- Dia 3: frontend, formulario, lista de jobs, badges y auto-actualizacion
- Dia 4: despliegue en AWS, pipeline CI/CD y URL publica
- Dia 5: documentacion final, pruebas y preparacion de defensa
- Buffer A: estabilizacion tecnica
- Buffer B: rehearsal y cierre de entrega

Plan fuente:
- [SSOT.md](SSOT.md)

## 7. Setup Local (objetivo de implementacion)

El entorno debe levantar con un solo comando:

```bash
docker compose up --build
```

El setup final incluira:
- backend FastAPI
- worker
- LocalStack
- frontend React
- script de inicializacion de recursos locales

URLs locales previstas:
- backend: http://localhost:8000
- frontend: http://localhost:5173

## 8. Despliegue a Produccion (objetivo de implementacion)

El flujo de despliegue final se ejecutara con GitHub Actions:
- push a main
- build de imagenes API y worker
- push a ECR
- despliegue en EC2

El README final de entrega incluira:
- badge de pipeline en verde
- URL publica de produccion

## 9. Costo y Guardrails

Guardrail de costo:
- objetivo entre USD 0 y USD 5
- tope maximo menor a USD 10

Servicios elegidos para minimizar costo:
- EC2 micro
- SQS
- DynamoDB
- S3 y CloudFront
- CloudWatch con volumen bajo

## 10. Documentacion del Proyecto

- [SSOT.md](SSOT.md)
- [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)
- [SKILL.md](SKILL.md)
- [AI_WORKFLOW.md](AI_WORKFLOW.md)

## 11. Estado Actual

Estado actual real del repositorio:
- constitucion SSOT definida y versionada
- estructura documental base creada
- diagramas iniciales creados
- plantillas obligatorias completadas y alineadas
- backend de Fase 1 y Fase 2 implementado y validado
- frontend React dockerizado implementado y validado para Fase 3

Pendiente en siguientes fases:
- implementacion de infraestructura operativa y pipeline

## 12. Reglas Operativas

- toda documentacion debe escribirse en espanol
- todos los comentarios explicativos del codigo deben escribirse en espanol
- toda decision de arquitectura y alcance debe alinearse con [SSOT.md](SSOT.md)