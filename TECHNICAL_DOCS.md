# Documentacion Tecnica

Estado: Base tecnica definida y alineada al SSOT

## 1. Objetivo del Documento

Este documento describe la solucion tecnica objetivo del proyecto Prosperas Async Reports. Sirve como referencia para desarrolladores, evaluadores y defensa tecnica.

Fuente constitucional:
- [SSOT.md](SSOT.md)

## 2. Alcance Funcional

El sistema debe permitir:
- crear un job de reporte con respuesta inmediata
- procesar jobs en segundo plano mediante cola AWS
- actualizar y persistir estado del job durante su ciclo de vida
- visualizar estados en frontend sin recarga de pagina
- desplegar en AWS real mediante CI/CD

## 3. Diagrama de Arquitectura

Diagrama de referencia actual:
- [docs/diagrams/architecture/system-architecture.md](docs/diagrams/architecture/system-architecture.md)

Flujo visual complementario:
- [docs/diagrams/workflow/job-lifecycle.md](docs/diagrams/workflow/job-lifecycle.md)

## 4. Tabla de Servicios AWS

| Servicio | Responsabilidad tecnica | Motivo de seleccion | Alternativa descartada |
| --- | --- | --- | --- |
| EC2 micro | Ejecutar API y worker contenerizados | Menor riesgo de costo y complejidad para el plazo del reto | ECS Fargate por mayor costo y complejidad operativa |
| ECR | Almacenar imagenes Docker | Integracion directa con pipeline y despliegue | Registro externo sin control centralizado en AWS |
| SQS Standard | Cola principal de jobs | Desacoplamiento simple, retry y visibilidad nativa | Soluciones self-managed con mayor carga operativa |
| SQS DLQ | Aislar mensajes fallidos repetidos | Evita bloqueo de cola principal | Reintentos infinitos sin aislamiento |
| SQS prioridad | Canal de alta prioridad para B1 | Permite enrutar por tipo de reporte | Una sola cola sin prioridad |
| DynamoDB | Persistencia de estado y metadata de jobs | Patron de acceso simple, bajo costo y sin servidor | RDS con mayor sobrecarga operativa |
| S3 + CloudFront | Hosting frontend y acceso publico | Simplicidad, bajo costo y buena experiencia de demo | Servir frontend desde EC2 sin CDN |
| CloudWatch | Logs, metricas y salud | Observabilidad nativa para B5 | Logging sin centralizacion |

## 5. Contrato de API Objetivo

### 5.1 POST /jobs

Responsabilidad:
- autenticar usuario por JWT
- validar payload con Pydantic v2
- crear job en estado PENDING
- publicar mensaje en SQS
- responder de inmediato con job_id

Respuesta esperada:

```json
{
	"job_id": "uuid",
	"status": "PENDING"
}
```

### 5.2 GET /jobs/{job_id}

Responsabilidad:
- devolver estado actual del job y resultado cuando aplique

### 5.3 GET /jobs

Responsabilidad:
- listar jobs del usuario autenticado
- paginacion minima de 20 por pagina

## 6. Flujo de Datos End-to-End

1. Usuario envia POST /jobs desde frontend.
2. API valida JWT y payload.
3. API persiste job PENDING en DynamoDB.
4. API publica mensaje en SQS y responde inmediatamente.
5. Worker consume mensaje y cambia estado a PROCESSING.
6. Worker finaliza con COMPLETED o FAILED, aplicando retry y DLQ segun politica.
7. Frontend refresca por polling o push y actualiza badge.

Estados canonicos:
- PENDING
- PROCESSING
- COMPLETED
- FAILED

## 7. Worker y Concurrencia

Comportamiento objetivo:
- al menos 2 consumidores concurrentes
- procesamiento asincrono por mensaje
- actualizacion de estado en cada etapa
- manejo de fallos con reintentos y DLQ

Soporte bonus:
- B1: prioridad por tipo de reporte
- B4: backoff exponencial
- B2: circuit breaker

## 8. Persistencia y Modelo de Datos

Modelo minimo requerido:
- job_id
- user_id
- status
- report_type
- created_at
- updated_at
- result_url

Patron recomendado:
- PK principal por job_id
- indice secundario por user_id para listado eficiente

## 9. Setup Local (objetivo de implementacion)

Arquitectura local objetivo:
- backend
- worker
- frontend
- LocalStack

Flujo de arranque esperado:

```bash
docker compose up --build
```

Nota:
- los comandos definitivos quedaran validados al crear backend y frontend reales.

## 10. Despliegue y CI/CD

Pipeline objetivo:
- trigger por push a main
- validacion basica y pruebas
- build de imagen API y worker
- push a ECR
- despliegue en EC2

Referencia de flujo:
- [docs/diagrams/workflow/ci-cd-overview.md](docs/diagrams/workflow/ci-cd-overview.md)

## 11. Variables de Entorno (plan)

Variables minimas esperadas:
- APP_ENV
- API_PORT
- JWT_SECRET_KEY
- AWS_REGION
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- SQS_QUEUE_URL
- SQS_DLQ_URL
- DYNAMODB_TABLE_NAME
- FRONTEND_API_BASE_URL

Nota:
- se formalizaran en .env.example durante implementacion.

## 12. Estrategia de Pruebas

Pruebas objetivo:
- unitarias de servicios y worker
- integracion de endpoints FastAPI
- escenario de fallo de procesamiento

Meta de cobertura:
- backend >= 70 por ciento para bonus B6

Herramientas objetivo:
- pytest
- pytest-asyncio
- httpx
- moto

## 13. Observabilidad y Operacion

Elementos objetivo:
- logs estructurados en backend y worker
- metricas de negocio
- endpoint GET /health
- trazabilidad de job_id en logs

## 14. Riesgos, Mitigaciones y Evolucion

Riesgos principales:
- desviacion de tiempo por complejidad no planificada
- configuraciones AWS incompletas en despliegue
- inconsistencias entre documentacion y estado real

Mitigaciones:
- enfoque incremental por fases del SSOT
- validacion frecuente con smoke tests
- actualizacion continua de docs junto al desarrollo

Evolucion post-entrega:
- migracion opcional a ECS/Fargate
- IaC con Terraform en fase final opcional
- mejoras de observabilidad y escalado