# SKILL - Contexto Operativo para Agentes de IA

Estado: Activo para trabajo guiado por SSOT

## 1. Proposito de Este Archivo

Este archivo permite que un agente de IA opere sobre el proyecto Prosperas sin tener que leer todo el repositorio desde cero en cada sesion.

Si existe conflicto entre este archivo y el SSOT, prevalece:
- [SSOT.md](SSOT.md)

## 2. Descripcion del Sistema

El sistema implementa procesamiento asincrono de reportes:
- el usuario solicita un reporte desde frontend
- la API crea un job y lo publica en una cola AWS
- el worker procesa el job en segundo plano
- el estado se persiste y se refleja en frontend sin recarga

Arquitectura oficial:
- Arquitectura Event-Driven Contenerizada sobre EC2

## 3. Reglas Obligatorias de Trabajo

- toda documentacion debe mantenerse en espanol
- todo comentario explicativo de codigo debe escribirse en espanol
- mantener costos AWS por debajo de USD 10
- no iniciar Terraform hasta tener la aplicacion core estable
- todo cambio significativo debe respetar [SSOT.md](SSOT.md)

## 4. Mapa del Repositorio Actual

Rutas base actuales:
- [SSOT.md](SSOT.md): constitucion del proyecto
- [README.md](README.md): resumen ejecutivo y guia de entrada
- [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md): especificacion tecnica
- [SKILL.md](SKILL.md): contexto operativo para agentes
- [AI_WORKFLOW.md](AI_WORKFLOW.md): evidencia de uso de IA
- [AGENTS.md](AGENTS.md): reglas de operacion del agente
- [docs/ssot/CHANGELOG.md](docs/ssot/CHANGELOG.md): historial de cambios del SSOT
- [docs/diagrams/architecture/system-architecture.md](docs/diagrams/architecture/system-architecture.md): diagrama de arquitectura
- [docs/diagrams/workflow/job-lifecycle.md](docs/diagrams/workflow/job-lifecycle.md): secuencia del job
- [docs/diagrams/workflow/ci-cd-overview.md](docs/diagrams/workflow/ci-cd-overview.md): flujo CI/CD

Estructura objetivo de implementacion:
- backend/app/api
- backend/app/core
- backend/app/models
- backend/app/services
- backend/app/worker
- backend/tests
- frontend/src
- local/docker-compose.yml

## 5. Flujo Operativo Canonico

1. Frontend envia POST /jobs.
2. API valida JWT y payload.
3. API crea job en DynamoDB con estado PENDING.
4. API publica mensaje en SQS.
5. Worker consume mensaje en paralelo y marca PROCESSING.
6. Worker termina en COMPLETED o FAILED con retry y DLQ.
7. Frontend consulta estado o recibe push y actualiza badge.

## 6. Como Funciona POST /jobs

Comportamiento esperado:
- autentica usuario
- valida payload con Pydantic v2
- genera job_id
- persiste estado PENDING
- publica mensaje a cola
- responde sin bloquear

Respuesta minima:

```json
{
	"job_id": "uuid",
	"status": "PENDING"
}
```

## 7. Como Funciona el Worker

Comportamiento esperado:
- consumo de SQS con al menos 2 consumidores concurrentes
- actualizacion de estado a PROCESSING al iniciar
- procesamiento simulado del reporte
- cierre en COMPLETED o FAILED
- manejo de retries y backoff exponencial
- derivacion a DLQ en fallos repetidos

## 8. Patron para Agregar un Nuevo Tipo de Reporte

Pasos operativos:
1. agregar nuevo valor en el enum de report_type
2. agregar validacion en schema de request
3. implementar handler de procesamiento en worker
4. definir si requiere cola de prioridad
5. agregar pruebas unitarias y de integracion
6. actualizar TECHNICAL_DOCS y README

## 9. Comandos Frecuentes (objetivo)

Arranque local:

```bash
docker compose up --build
```

Pruebas backend:

```bash
pytest -q
```

Nota:
- estos comandos quedan como objetivo y se validaran cuando el codigo se implemente.

## 10. Errores Comunes y Resolucion

LocalStack no levanta:
- validar puertos ocupados
- validar version de Docker
- revisar logs del contenedor

Worker no consume mensajes:
- revisar queue URL y credenciales
- revisar long polling
- revisar visibilidad y permisos IAM

Jobs no cambian de estado:
- validar actualizaciones en DynamoDB
- validar manejo de excepciones en worker
- revisar trazas por job_id

Frontend no muestra actualizaciones:
- validar endpoint de estado
- validar polling interval o canal WebSocket
- validar manejo de errores en cliente

## 11. Reglas de Extension

Cuando extiendas el sistema:
- mantener separacion entre api, servicios y worker
- evitar logica AWS acoplada a routers
- centralizar manejo de errores
- documentar toda decision no obvia
- actualizar docs al mismo tiempo que el codigo

## 12. Guia para Agentes de IA

Si eres un agente trabajando en este repositorio:
- lee primero [SSOT.md](SSOT.md)
- despues revisa [README.md](README.md) y [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)
- si modificas alcance o arquitectura, versiona SSOT y changelog
- no afirmes funcionalidad implementada sin verificar archivos reales
- prioriza soluciones explicables para entrevista tecnica