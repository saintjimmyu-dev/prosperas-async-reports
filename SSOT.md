# SSOT - Reto de Reportes Asincronos Prosperas

Version: 1.3.9
Status: Activo (Fase 7 cerrada: backend y frontend operativos en produccion, B1-B6 implementados y validados)
Last Updated: 2026-03-22
Owner: GitHub Copilot + project owner
Project Root: D:/C U R S O S/AI Projects/Prosperas
Primary Source: Prueba_Tecnica_Prosperas_FullStack_4.docx

## 1. Proposito y Gobernanza

Este documento es la fuente unica de verdad para la implementacion de la prueba tecnica de Prosperas.

Su proposito es:
- traducir el documento original de requerimientos a una constitucion de implementacion accionable
- definir la arquitectura seleccionada, restricciones, prioridades y fases de entrega
- guiar decisiones de desarrollo, documentacion, pruebas y despliegue
- servir como referencia estable para README, TECHNICAL_DOCS.md, SKILL.md y la defensa tecnica

Reglas de gobernanza:
- toda decision relevante del proyecto debe alinearse con este SSOT salvo aprobacion explicita del owner
- toda actualizacion del SSOT debe aumentar la version y crear un snapshot fechado en docs/ssot/versions
- el objetivo de implementacion valido mas reciente es siempre este archivo
- toda nueva generacion de codigo y toda edicion futura deben seguir este documento antes de implementar trabajo nuevo
- el owner realiza siempre el merge en todos los casos y ramas del repositorio; el agente puede avanzar hasta ramas y PR (incluyendo codigo, pruebas, documentacion y preparacion de release), pero nunca ejecutar merge a master/main
- el codigo del proyecto debe incluir comentarios explicativos detallados en espanol para logica importante, flujos, efectos secundarios, integraciones y comportamiento no obvio
- toda documentacion generada dentro del proyecto debe escribirse en espanol
- todo script de pruebas tecnicas o validacion runtime debe ubicarse bajo local/scripts/testing para evitar archivos sueltos en la raiz de local
- los scripts de local/scripts/testing deben nombrarse por fase con el prefijo phaseN para permitir reejecucion historica ordenada

## 2. Resumen Ejecutivo

Identidad del proyecto:
- Nombre: Sistema de Procesamiento Asincrono de Reportes Prosperas
- Objetivo: construir una plataforma de reportes asincronos con FastAPI, React, mensajeria AWS, workers concurrentes, persistencia de estado, actualizacion de frontend en tiempo real, desarrollo local con LocalStack y despliegue productivo en AWS con CI/CD
- Meta de entrega: satisfacer los 100 puntos core y maximizar bonus hasta +25 sin elevar el riesgo de entrega mas alla de la ventana disponible

Decision arquitectonica central:
- Arquitectura seleccionada: Arquitectura Event-Driven Contenerizada sobre EC2
- Patron principal: API FastAPI + desacoplamiento con SQS + worker concurrente + persistencia en DynamoDB + frontend React + CI/CD con GitHub Actions
- Motivo: es la arquitectura mas segura para el tiempo disponible, la mas facil de explicar en entrevista, compatible con LocalStack y docker compose, y mantiene el menor riesgo de costo dentro del AWS Free Tier

Objetivo de puntaje:
- Objetivo core: 100 / 100
- Objetivo bonus: implementar B1, B4 y B5 como metas por defecto; agregar B3 si el cronograma sigue saludable; considerar B2 y B6 solo si no desestabilizan la entrega

## 3. Restricciones No Negociables

- La solucion completa vive bajo D:/C U R S O S/AI Projects/Prosperas
- La arquitectura de produccion se mantiene como Arquitectura Event-Driven Contenerizada sobre EC2 salvo que el SSOT se actualice y versiona de forma intencional
- El desarrollo local debe levantar con docker compose up usando LocalStack y sin configuracion manual de AWS
- Produccion debe ejecutarse en una cuenta AWS real con URL publica
- El repositorio debe incluir GitHub Actions CI/CD que despliegue al hacer push a main
- El repositorio debe incluir TECHNICAL_DOCS.md, SKILL.md, README.md, .env.example y evidencia del flujo asistido por IA
- No se pueden commitear credenciales ni secretos
- El gasto total en AWS debe mantenerse con seguridad por debajo de USD 10 para este ejercicio
- Toda documentacion entregable y de soporte debe estar en espanol
- Todo comentario explicativo agregado al codigo debe redactarse en espanol

## 4. Vision General de la Solucion

### 4.1 Resumen de Arquitectura

Componentes principales en ejecucion:
- contenedor de API en EC2 ejecutando FastAPI
- contenedor de worker en EC2 consumiendo SQS de forma concurrente
- cola Amazon SQS Standard para procesamiento principal de jobs
- Amazon SQS Dead Letter Queue para fallos repetidos
- segunda cola SQS opcional para jobs de alta prioridad y bonus B1
- Amazon DynamoDB para persistencia del estado de jobs
- frontend React servido desde S3 + CloudFront, o Nginx en EC2 solo si simplifica una entrega puntual
- pipeline GitHub Actions para construir y desplegar imagenes a produccion
- CloudWatch para logs, metricas y visibilidad operativa

### 4.2 Por Que Esta Arquitectura

Esta arquitectura fue seleccionada porque:
- satisface todos los requerimientos obligatorios con la menor cantidad posible de piezas riesgosas
- soporta desacoplamiento asincrono y workers concurrentes con claridad
- es simple de probar localmente con LocalStack
- evita cold starts de Lambda y la deriva de costos de Fargate
- permite una narrativa senior solida basada en resiliencia, observabilidad y trade-offs documentados

## 5. Servicios AWS y Justificacion de Free Tier

| Servicio | Responsabilidad | Por que se eligio | Justificacion de Free Tier / costo |
| --- | --- | --- | --- |
| EC2 t2.micro o t3.micro | Hospedar los contenedores de API y worker en produccion | Es mas simple que ECS/Fargate para este reto, mas facil de depurar y explicar | Cubierto por horas del Free Tier para cuentas elegibles; es la opcion con menor riesgo de costo |
| ECR | Almacenar imagenes de API y worker | Registro nativo de contenedores para CI/CD | El tamano de imagenes debe mantenerse dentro de uso gratuito o costo despreciable |
| SQS Standard | Cola principal de jobs asincronos | Cola administrada con reintentos y visibility timeout | El trafico esperado del reto es practicamente gratuito |
| SQS DLQ | Aislar mensajes problematicos | Evita bloquear la cola y soporta resiliencia | Mismo perfil de costo bajo que la cola principal |
| SQS Standard o FIFO de prioridad | Jobs de alta prioridad para B1 | Modela de forma limpia el enrutamiento por tipo de reporte | El trafico sigue siendo bajo y de costo despreciable |
| DynamoDB | Persistir jobs, transiciones de estado y metadata de resultado | No requiere administrar servidor y el patron de acceso es simple por job_id y user_id | El volumen bajo de lectura y escritura debe mantenerse en cero o casi cero costo |
| S3 | Hospedar assets estaticos del frontend | Hosting estatico simple y barato | El volumen de almacenamiento y requests del reto es pequeno |
| CloudFront | URL publica del frontend, HTTPS y cache | Mejora la experiencia de entrega y demo frente al endpoint crudo de S3 | El volumen esperado es muy bajo |
| CloudWatch | Logs estructurados, metricas, alarmas y soporte a salud | Necesario para B5 y visibilidad operativa | Logs y metricas basicos con volumen bajo se mantienen dentro de rango seguro |
| IAM | Roles de minimo privilegio para EC2, CI/CD y acceso de revision | Componente obligatorio del plano de control AWS | Sin costo directo |

Posicion de control de costo:
- objetivo preferido: entre USD 0 y USD 5 totales
- techo duro: menos de USD 10
- evitar Fargate, topologias dependientes de ALB, NAT Gateway y bases de datos administradas siempre encendidas

## 6. Flujo de Datos End-to-End

El flujo canonico del job tiene 7 pasos:

1. El usuario se autentica en el frontend y envia POST /jobs con report_type, date_range y format.
2. FastAPI valida el JWT y el payload con Pydantic v2, crea un nuevo job_id y persiste el job en DynamoDB con estado PENDING.
3. La API publica un mensaje en la cola principal SQS, o en la cola de prioridad si el report_type activa el comportamiento de B1.
4. La API responde de inmediato con { job_id, status: "PENDING" } para no bloquear al usuario.
5. El worker consume mensajes desde SQS con al menos dos consumidores concurrentes, actualiza DynamoDB a PROCESSING, ejecuta la generacion simulada del reporte y guarda la metadata del resultado.
6. Si el procesamiento termina bien, el worker actualiza el job a COMPLETED y guarda result_url o una referencia equivalente; si falla, la logica de retry y la DLQ manejan el mensaje sin bloquear la cola.
7. El frontend refresca el estado mediante polling o notificaciones push, y el badge cambia de PENDING a PROCESSING y luego a COMPLETED o FAILED sin recargar la pagina.

## 7. Plan de Entrega por Fases

### Fase 0 - Fundacion y SSOT

Entregables:
- SSOT establecido y versionado
- carpetas de diagramas creadas
- instrucciones del workspace alineadas con el SSOT
- roadmap de desarrollo acordado

### Fase 1 - Dia 1: Core Backend y Emulacion AWS Local

Entregables:
- estructura del backend
- bootstrap de FastAPI
- base de autenticacion JWT
- modelos de request y response con Pydantic v2
- POST /jobs
- GET /jobs/{job_id}
- GET /jobs paginado
- LocalStack levantando con docker compose
- script de inicializacion de tabla DynamoDB local

Criterios de exito:
- la API levanta localmente con docker compose up
- se puede crear un job y persistirlo como PENDING

Estado actual (2026-03-19):
- fase completada y validada en runtime local con docker compose
- smoke test end to end ejecutado con local/scripts/testing/phase1_runtime_validate.sh
- validacion verificada para GET /health, POST /auth/login, POST /jobs, GET /jobs/{job_id} y GET /jobs
- los jobs se persisten en DynamoDB local y se publican en SQS local con estado inicial PENDING
- la asociacion de RedrivePolicy hacia DLQ se mantiene planificada para Fase 2

### Fase 2 - Dia 2: Mensajeria, Workers y Transiciones de Estado

Entregables:
- integracion SQS en la publicacion desde la API
- servicio worker con al menos 2 consumidores concurrentes
- ciclo de vida PENDING -> PROCESSING -> COMPLETED / FAILED
- configuracion de DLQ
- estrategia de errores documentada

Objetivos bonus:
- B1 prioridad de mensajes
- B4 retry con backoff exponencial

Criterios de exito:
- al menos 2 jobs se procesan en paralelo
- los mensajes fallidos no bloquean la cola

Estado actual (2026-03-20):
- fase completada y validada en runtime local con docker compose
- validacion end to end ejecutada con local/scripts/testing/phase2_runtime_validate.sh
- se verifico worker con al menos 2 consumidores concurrentes
- se verificaron transiciones PENDING -> PROCESSING -> COMPLETED y ruta de fallo a FAILED
- se verifico B1 con enrutamiento por cola de prioridad segun report_type
- se verifico B4 con retry y backoff exponencial con evidencias en logs
- RedrivePolicy y DLQ quedaron operativas con maxReceiveCount=3

### Fase 3 - Dia 3: UX Frontend y Visibilidad de Estado

Entregables:
- scaffold de React
- flujo de login o manejo basico de token
- formulario de solicitud de reporte
- lista de jobs con badges de estado
- refresco automatico via polling
- layout responsive para movil y desktop
- estados visuales de error sin alert nativa

Objetivos bonus:
- B3 actualizaciones push con WebSocket si el cronograma lo permite

Criterios de exito:
- los cambios de estado del job se ven sin recargar la pagina

Estado actual (2026-03-20):
- fase completada, commiteada y validada en runtime local con docker compose
- frontend React dockerizado disponible en http://localhost:5173
- se implemento login con JWT demo, formulario de creacion de jobs y listado paginado
- el tablero refresca automaticamente cada 5 segundos para reflejar cambios de estado sin recargar
- se implementaron badges de estado, toasts de error y layout responsive para movil y desktop
- se agrego branding de autor: Jimmy Uruchima aparece en login, hero del dashboard y footer fijo
- la generacion de PDF es simulada (result_url = s3://prosperas-reports/<id>.pdf) hasta Fase 4
- validacion tecnica disponible en local/scripts/testing/phase3_runtime_validate.sh
- commit: caf2509 feat: Fase 3 - frontend React dockerizado con branding Jimmy Uruchima

### Fase 4 - Dia 4: AWS Productivo y CI/CD

Entregables:
- host EC2 productivo configurado
- despliegue Docker en EC2
- repositorios ECR
- pipeline GitHub Actions sobre main
- URL publica de produccion
- .env.example completo
- README con secciones iniciales de despliegue y setup local

Objetivos bonus:
- B5 logging estructurado, metricas y GET /health

Criterios de exito:
- push a main despliega automaticamente a produccion
- la aplicacion es accesible desde una URL publica

Estado de preparacion (2026-03-21):
- repositorio GitHub creado: https://github.com/saintjimmyu-dev/prosperas-async-reports (publico)
- rama protegida master con requerimiento de PR, revision y check CI obligatorio
- usuario IAM github-actions-deploy creado con PowerUserAccess e inline policy ProsperasLimitedIamScope
- credenciales IAM almacenadas en SSM Parameter Store como SecureString bajo /prosperas/github-actions-deploy/
- Secret Scanning y Push Protection habilitados en el repositorio
- workflow CI .github/workflows/ci.yml creado con job ci/lint-build pasando
- script de hardening local/scripts/security/apply_github_repo_security.ps1 commiteado
- PR #1 mergeado a master (commit ab2ac5f) via squash merge
- pendiente: Terraform infrastructure, pipeline de deploy, ECR, EC2 y URL publica

Estado de implementacion inicial (2026-03-21):
- se creo infra/terraform con recursos base para ECR, DynamoDB, SQS (main, priority, DLQ), IAM role/profile y EC2
- se creo .github/workflows/deploy.yml para build/push a ECR y despliegue remoto en EC2 via SSM
- se creo infra/ec2/docker-compose.prod.yml para backend + worker con variables de entorno de produccion
- se creo infra/ec2/deploy.sh para despliegue idempotente remoto y verificacion de health
- backend actualizado para usar credenciales IAM role en EC2 (endpoint/keys opcionales)

Infraestructura AWS aprovisionada (2026-03-21) - terraform apply completado:
- ECR: 635896495979.dkr.ecr.us-east-1.amazonaws.com/prosperas-backend
- DynamoDB tabla: prosperas-jobs (PAY_PER_REQUEST, GSI user_id-index)
- SQS cola principal: https://sqs.us-east-1.amazonaws.com/635896495979/prosperas-jobs-queue
- SQS cola prioridad: https://sqs.us-east-1.amazonaws.com/635896495979/prosperas-jobs-priority-queue
- SQS DLQ: https://sqs.us-east-1.amazonaws.com/635896495979/prosperas-jobs-dlq
- EC2 instance: i-085134f9bf4e85cd1 (IP publica: 18.212.132.182, DNS: ec2-18-212-132-182.compute-1.amazonaws.com)
- IAM role: prosperas-ec2-role con AmazonSSMManagedInstanceCore + ECR read + runtime access (incluye dynamodb:DescribeTable)
- Seguridad: sg-0aaa01b50c94f0000
Deploy exitoso en produccion (2026-03-21):
- 18 GitHub Secrets cargados via API con PyNaCl
- pipeline deploy.yml disparado automaticamente tras merge a master
- 3 fallos iterativos corregidos: docker no instalado, -f docker-compose.prod.yml ausente, login ECR faltante
- deploy #4 exitoso: conclusion success, commit a0b1869
- URL publica activa: http://18.212.132.182:8000
- healthcheck extendido con verificacion de DynamoDB y SQS implementado (B5)
- README actualizado para reflejar Fase 4 completa

Estado final Fase 4 (2026-03-22):
- dynamodb:DescribeTable agregado a IAM policy ec2_runtime_access via terraform apply
- IP publica cambio de 54.224.221.78 a 18.212.132.182 (efecto de user_data hash change en terraform apply)
- secret CORS_ALLOWED_ORIGINS actualizado via GitHub API: http://18.212.132.182:5173,http://localhost:5173,http://127.0.0.1:5173
- /health confirmado verde en produccion: status ok, dynamodb ok, sqs ok
- Fase 4 cerrada definitivamente el 2026-03-22

### Fase 5 - Dia 5: Documentacion, Pruebas y Defensa

Estado actual de Fase 5:
- documentacion tecnica y operativa cerrada y mergeada a master
- evidencia de smoke test en produccion verificada exitosamente por el owner desde cliente externo (Postman/PowerShell)

Entregables:
- TECHNICAL_DOCS.md
- SKILL.md
- AI_WORKFLOW.md
- README final con badge y URL
- smoke tests y pruebas backend
- talking points para entrevista

Objetivos bonus:
- B2 circuit breaker si el sistema esta estable
- B6 aumento de cobertura backend hacia 70 por ciento

Criterios de exito:
- todos los documentos obligatorios existen y reflejan fielmente el sistema funcionando

### Fase 6 - Buffer A

Estado actual de Fase 6:
- cerrada con hardening tecnico aplicado al backend
- B2 verificado con circuit breaker por report_type en el worker
- B6 verificado con 17 pruebas backend aprobadas y 75 por ciento de cobertura sobre `backend/app`

Usar para:
- arreglos de despliegue
- pulido de frontend
- comportamiento inestable de colas
- alineacion documental

### Fase 7 - Buffer B

Estado actual de Fase 7:
- en ejecucion con B3 implementado (WebSocket de snapshots de jobs + fallback a polling)
- despliegue frontend preparado en CI/CD y compose productivo (imagen frontend + servicio nginx)
- pendiente de cierre: validacion productiva final con evidencia runtime de interfaz publica

Usar para:
- ensayo de entrevista
- revision final de limpieza en AWS
- creacion del usuario IAM para revision
- recoleccion de evidencias y paquete final de entrega

## 8. Matriz de Implementacion de Bonus

| Bonus | Implementacion concreta | Herramientas | Dificultad | Prioridad |
| --- | --- | --- | --- | --- |
| B1 - Prioridad de mensajes | Usar dos colas, enrutar por report_type y hacer que el worker consulte primero alta prioridad | SQS principal + cola de prioridad | Baja | Alta |
| B2 - Circuit breaker | Rastrear fallos consecutivos por tipo de reporte y abrir el breaker durante una ventana de enfriamiento | Capa de servicios Python + DynamoDB o estado en memoria con reglas de reset claras | Media | Media |
| B3 - Notificaciones en tiempo real | Enviar actualizaciones al frontend cuando cambia el estado del job | WebSocket con FastAPI o fallback SSE | Media | Media |
| B4 - Backoff exponencial | Aumentar el retraso por intento fallido antes del siguiente ciclo de visibilidad o politica de reencolado | Politica de retry en worker + receive count de SQS | Baja | Alta |
| B5 - Observabilidad | Logs estructurados, metricas de negocio y verificaciones de dependencias en GET /health | CloudWatch + logger estructurado + servicio de health | Baja | Alta |
| B6 - Pruebas avanzadas | Cobertura backend >= 70 por ciento, pruebas de integracion y fallos | pytest, pytest-asyncio, httpx, moto | Media | Media |

Secuencia de bonus por defecto:
- Primero: B1
- Segundo: B4
- Tercero: B5
- Cuarto: B3
- Quinto: B2
- Sexto: B6

## 9. Estructura Objetivo del Repositorio

La implementacion debe evolucionar hacia esta estructura:

```text
Prosperas/
  SSOT.md
  AGENTS.md
  README.md
  TECHNICAL_DOCS.md
  SKILL.md
  AI_WORKFLOW.md
  .env.example
  backend/
    app/
      api/
      core/
      models/
      services/
      worker/
      main.py
    tests/
    Dockerfile
    requirements.txt
  frontend/
    - bucket S3 real para almacenar reportes generados
    - generacion real de PDF/CSV en el worker usando weasyprint o reportlab
    - upload del archivo generado al bucket S3 con boto3
    - result_url como URL pre-firmada de S3 con TTL de 1 hora
    - endpoint GET /jobs/{id}/download que redirige a la URL pre-firmada
    src/
      components/
      hooks/
      pages/
      services/
      styles/
    Dockerfile
    package.json
  local/
    docker-compose.yml
    init/
    scripts/
      testing/
        phase1_runtime_validate.sh
        phase2_runtime_validate.sh
        phase3_runtime_validate.sh
  infra/
    ec2/
    scripts/
    terraform/        # fase final opcional solamente
  docs/
    ssot/
      CHANGELOG.md
      versions/
    diagrams/
      architecture/
      workflow/
      user-flow/
  .github/
    workflows/
```

Reglas de responsabilidad:
- backend/app/api contiene solo routers FastAPI
- backend/app/services contiene la logica de negocio y la orquestacion con AWS
- backend/app/worker contiene el consumidor de cola y la logica de procesamiento
- backend/app/core contiene configuracion, auth, handlers globales y wiring de infraestructura
- backend/tests contiene pruebas unitarias, de integracion y de rutas de fallo
- local contiene el stack completo de bootstrap local con LocalStack
- local/scripts/testing contiene scripts auxiliares de smoke test y validacion tecnica nombrados por fase con prefijo phaseN
- infra contiene solo assets de despliegue productivo

## 10. Decisiones de Diseno para README y Entrevista

### 10.1 EC2 vs Fargate

Usar EC2 porque:
- reduce el riesgo de costo dentro del limite de USD 10
- simplifica despliegue y depuracion para un reto corto
- permite correr API y worker juntos con facilidad
- es mas facil de explicar que una orquestacion con ECS services, task definitions y ALB

No usar Fargate ahora porque:
- el riesgo de costo es materialmente mayor
- produccion suele requerir piezas adicionales de networking y balanceo
- agrega complejidad de infraestructura con poco beneficio en puntaje para este reto

Nota de evolucion futura:
- la aplicacion puede migrar despues de EC2 a ECS/Fargate porque API y worker ya estan contenerizados

### 10.2 DynamoDB vs RDS

Usar DynamoDB porque:
- los patrones de acceso son simples y conocidos de antemano
- no hay un servidor de base de datos que administrar
- es mas barato y seguro para el plazo del reto
- permite lookup simple por job_id y listado eficiente por user_id mediante un GSI

No usar RDS ahora porque:
- tiene mayor costo y sobrecarga operativa
- agrega complejidad en local y en produccion
- no es necesario para el modelo de datos actual

### 10.3 SQS vs Alternativas

Usar SQS porque:
- satisface de forma directa el requerimiento de cola en AWS
- soporta DLQ, visibility timeout, retries y desacoplamiento con claridad
- es mas facil de justificar que un RabbitMQ autogestionado o servicios de streaming sobredimensionados

No usar SNS o Kinesis como cola principal porque:
- SNS no es una cola y requiere consumidores adicionales
- Kinesis es innecesario para esta carga y mas dificil de explicar

### 10.4 Polling vs WebSocket

Usar polling primero porque:
- es la ruta de menor riesgo para satisfacer el requerimiento core de visibilidad en tiempo real
- reduce complejidad mientras la plataforma base se estabiliza

Agregar WebSocket si el cronograma lo permite porque:
- mejora la impresion senior y satisface B3 de forma directa

## 11. Mapeo de Rubrica

| Criterio de evaluacion | Lo que debe demostrar esta arquitectura |
| --- | --- |
| Arquitectura y diseno AWS | Seleccion clara de servicios, trade-offs documentados y flujo asincrono coherente |
| Colas y mensajeria | Desacoplamiento con SQS, DLQ, retries, no bloqueo y procesamiento concurrente |
| Concurrencia y workers | Al menos 2 consumidores en paralelo con transiciones de estado consistentes |
| API FastAPI | Endpoints correctos, JWT, Pydantic v2 y manejo global de errores |
| Frontend React | Buena UX, badges de estado, auto-refresco y responsive design |
| Despliegue en produccion | URL publica en AWS con aplicacion funcional y HTTPS si es practico |
| CI/CD | GitHub Actions despliega en main y hay ejecuciones exitosas visibles |
| TECHNICAL_DOCS.md | Arquitectura, setup, despliegue, variables y pruebas completas |
| SKILL.md | Contexto suficiente para que una IA opere sin leer todo el codigo |
| Bonus | B1, B4 y B5 como base preferida; B3 fuertemente deseado si el sistema esta estable |

## 12. Checklist de Descalificacion Automatica

Antes de entregar, verificar todo lo siguiente:

1. No hay credenciales AWS, secretos JWT, passwords ni tokens commiteados.
2. docker compose up funciona localmente siguiendo el README.
3. La aplicacion esta desplegada en AWS real y accesible mediante una URL publica.
4. GitHub Actions existe y ha ejecutado exitosamente.
5. El sistema usa realmente un servicio AWS de mensajeria para procesamiento asincrono.
6. El worker procesa mensajes concurrentemente y no es completamente sincrono.
7. El usuario IAM de revision fue creado y compartido de forma segura como se solicito.
8. TECHNICAL_DOCS.md y SKILL.md existen en el repositorio.
9. El owner puede explicar el codigo generado y las decisiones de arquitectura durante la entrevista.

## 13. Catalogo de Prompts para Tareas de Alto Impacto

### 13.1 Prompt para worker asyncio

"Construye un servicio worker en Python 3.11 para una arquitectura FastAPI usando asyncio y aioboto3. Debe consultar Amazon SQS con al menos dos consumidores concurrentes, actualizar las transiciones de estado en DynamoDB PENDING -> PROCESSING -> COMPLETED / FAILED, soportar retries con backoff exponencial, enviar fallos repetidos a una DLQ y ser facil de explicar en entrevista. Agrega comentarios detallados en cada bloque de logica importante."

### 13.2 Prompt para circuit breaker

"Implementa un circuit breaker para fallos de procesamiento por report_type en un worker Python. El breaker debe abrirse despues de N fallos consecutivos, omitir procesamiento durante una ventana de enfriamiento, registrar transiciones y exponer suficiente estado para explicarlo en entrevista. Usa una separacion clara entre politica y logica de procesamiento, y agrega comentarios detallados."

### 13.3 Prompt para pruebas con moto

"Genera pruebas pytest para un backend FastAPI + SQS + DynamoDB. Incluye pruebas unitarias del worker, una prueba de integracion para POST /jobs y una prueba de ruta de fallo donde el procesamiento falle y el job termine en FAILED o avance hacia manejo por DLQ. Usa moto cuando sea util, pytest-asyncio para codigo async y comentarios detallados en aserciones importantes."

### 13.4 Prompt para SKILL.md

"Genera un archivo SKILL.md para un agente de IA que debe operar sobre este repositorio del reto Prosperas sin leer cada archivo. Incluye descripcion del sistema, mapa del repositorio, comandos frecuentes, como funciona POST /jobs, como el worker consume SQS, como se manejan los fallos, como agregar un nuevo report_type, errores comunes, setup local, flujo de despliegue y guia de extension. Mantenlo preciso y operativo."

### 13.5 Prompt para TECHNICAL_DOCS.md

"Genera TECHNICAL_DOCS.md a partir del codebase actual del sistema de reportes asincronos Prosperas. Incluye un diagrama completo de arquitectura, tabla de servicios AWS con justificacion, setup local con LocalStack, explicacion del pipeline de despliegue, variables de entorno, suites de prueba y trade-offs principales. Alinea el documento con el SSOT activo y senala cualquier desviacion intencional."

## 14. Inventario de Diagramas

Familias de diagramas requeridas para este proyecto:
- diagramas de arquitectura
- diagramas de flujo y secuencia
- diagramas de flujo de usuario
- diagramas de CI/CD y despliegue cuando la implementacion avance

Directorios actuales para diagramas:
- docs/diagrams/architecture
- docs/diagrams/workflow
- docs/diagrams/user-flow

## 15. Fase Final Opcional - Terraform IaC

Esta fase es opcional y solo debe iniciar despues de que la entrega core este estable.

Alcance:
- definir, aprovisionar, administrar y destruir la infraestructura con Terraform
- incluir un flujo seguro de destroy y manejo del estado
- alinear la implementacion con la documentacion actual de HashiCorp al momento de ejecutar esta fase

Reglas:
- no iniciar Terraform antes de que la aplicacion funcione end to end
- validar recursos del provider y sintaxis actualizados contra documentacion vigente de HashiCorp antes de escribir codigo
- mantener Terraform aislado bajo infra/terraform
- documentar con claridad los comandos de apply y destroy

## 16. Procedimiento de Actualizacion del SSOT

Cuando este SSOT cambie:

1. Actualizar el archivo canonico SSOT.md.
2. Aumentar la version con intencion semantica.
3. Crear una copia snapshot bajo docs/ssot/versions usando el patron YYYY-MM-DD-vX.Y.Z.md.
4. Anexar una entrada concisa en docs/ssot/CHANGELOG.md.
5. Asegurar que AGENTS.md se mantenga alineado si cambiaron reglas operativas.

Este archivo es la constitucion operativa del proyecto.