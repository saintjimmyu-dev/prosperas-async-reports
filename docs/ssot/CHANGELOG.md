# Historial del SSOT

## 2026-03-22 - v1.3.5

- Se actualizo el estado global para declarar Fase 6 cerrada con B2 y B6 verificados.
- Se registro la implementacion del circuit breaker por tipo de reporte dentro del worker.
- Se documento la validacion de B6 con 17 pruebas backend aprobadas y 75 por ciento de cobertura sobre `backend/app`.
- Se dejo Fase 7 como siguiente objetivo para B3, despliegue frontend productivo y cierre final de entrega.

## 2026-03-22 - v1.3.4

- Se actualizo el estado global para declarar Fase 5 cerrada y la ejecucion de Fase 6 para cierre de pendientes B2 y B6.
- Se agrego estado explicito para Fase 6 (hardening tecnico) y Fase 7 (cierre final y defensa).
- Se dejo documentado el orden de cierre de pendientes: B2 y B6 en Fase 6, B3 y paquete final en Fase 7.

## 2026-03-22 - v1.3.3

- Se actualizo el estado global del SSOT para reflejar que Fase 5 queda verificada en documentacion y smoke test productivo.
- Se registro la validacion exitosa del flujo smoke en produccion: GET /health, POST /auth/login, POST /jobs y polling GET /jobs/{job_id}.
- Se confirma disponibilidad operativa en la URL productiva y cierre tecnico de Fase 5.

## 2026-03-22 - v1.3.2

- Se actualizo el estado global del SSOT para reflejar Fase 5 documental cerrada y mergeada a master.
- Se dejo explicita la restriccion de entorno de esta sesion para ejecucion de smoke test productivo via HTTP/curl.
- Se marco como pendiente la evidencia de smoke test productivo desde un entorno externo habilitado.

## 2026-03-22 - v1.3.1

- Se agrego politica de gobernanza para flujo Git: el agente puede crear ramas y PR, pero no puede hacer merge a master/main.
- Se establece que el merge final queda reservado al owner y debe ejecutarse manualmente.

## 2026-03-22 - v1.3.0

- Se actualizo la IP publica de EC2 de 54.224.221.78 a 18.212.132.182 tras terraform apply que agrego dynamodb:DescribeTable (user_data hash cambio, AWS asigno IP dinamica nueva).
- Se agrego dynamodb:DescribeTable al IAM policy ec2_runtime_access; /health ahora verifica DynamoDB sin AccessDeniedException.
- Se actualizo secret CORS_ALLOWED_ORIGINS via GitHub API con la nueva IP: http://18.212.132.182:5173,http://localhost:5173,http://127.0.0.1:5173.
- Se verifico /health en produccion: status ok, dynamodb ok, sqs ok en http://18.212.132.182:8000/health.
- Se limpiaron ramas residuales: docs/actualizar-ip-ec2 y fix/iam-describetable-health absorbidos en este commit.
- Fase 4 cerrada formalmente. Inicio de Fase 5.

## 2026-03-21 - v1.2.0

- Se actualizo el estado global a "Fase 4 completada: deploy exitoso en EC2, URL publica activa, healthcheck extendido con B5".
- Se registraron los 18 GitHub Secrets cargados via API con PyNaCl.
- Se documentaron los 3 fallos de deploy corregidos en iteracion: docker-compose-plugin inexistente en AL2023, flag -f faltante en comandos compose, login ECR faltante antes del pull.
- Se registro el deploy exitoso: commit a0b1869, GitHub Actions run 23392624014, conclusion success.
- Se documento la URL publica activa: http://18.212.132.182:8000 con healthcheck en /health.
- Nota: IP publica actualizada de 54.224.221.78 a 18.212.132.182 tras terraform apply que modifico user_data de EC2 (2026-03-22).
- Se registro la implementacion del healthcheck extendido con verificacion de DynamoDB y SQS (bonus B5).
- Se actualizo el README para reflejar Fase 4 completada con URL publica e infraestructura activa.

## 2026-03-21 - v1.1.0

- Se actualizo el estado global a "Fase 4 en ejecucion: infraestructura AWS aprovisionada, pendiente cargar GitHub Secrets".
- Se registro la ejecucion exitosa de terraform apply con 12 recursos creados en us-east-1.
- Se documentaron los outputs del apply: EC2 i-085134f9bf4e85cd1 (IP 54.224.221.78), ECR prosperas-backend, DynamoDB prosperas-jobs, tres colas SQS.
- Se registro que el PAT actual no tiene scope Secrets:write; se requiere nuevo PAT o carga manual via GitHub UI.
- Se genero JWT_SECRET_KEY seguro de 48 bytes para usar en GitHub Secrets.
- Pendiente: cargar 18 GitHub Secrets y disparo del primer deploy automatico a produccion.

## 2026-03-21 - v1.0.9

- Se actualizo el estado global a "Fase 4 en implementacion: IaC Terraform + deploy CI/CD base".
- Se documento la creacion de infra/terraform con recursos base de ECR, DynamoDB, SQS, IAM y EC2.
- Se registro el workflow .github/workflows/deploy.yml para build/push de imagen y despliegue remoto via SSM.
- Se documento la creacion de infra/ec2/docker-compose.prod.yml y infra/ec2/deploy.sh para ejecucion productiva.
- Se registro la actualizacion del backend para usar endpoint y credenciales AWS opcionales, habilitando IAM Role en EC2.
- Se marco como pendiente el apply real en AWS, carga de GitHub Secrets y validacion de URL publica.

## 2026-03-21 - v1.0.8

- Se actualizo el estado global para declarar la preparacion completa de Fase 4.
- Se registro la creacion del repositorio GitHub saintjimmyu-dev/prosperas-async-reports con rama master protegida.
- Se documento el usuario IAM github-actions-deploy con PowerUserAccess, inline policy ProsperasLimitedIamScope y credenciales en SSM Parameter Store.
- Se registro la habilitacion de Secret Scanning y Push Protection en el repositorio.
- Se registro el workflow CI .github/workflows/ci.yml con job ci/lint-build aprobado.
- Se registro el script de hardening apply_github_repo_security.ps1 bajo local/scripts/security.
- Se registro la fusion del PR #1 (commit ab2ac5f) a master y la limpieza de la rama chore/ci-min-workflow.
- Se actualizo el estado global a "repositorio GitHub configurado con CI/CD y seguridad - iniciando Fase 4".

## 2026-03-20 - v1.0.7

- Se agrego branding de autor Jimmy Uruchima al frontend: eyebrow en login y dashboard, footer fijo minimalista en monospace, firma en login card y titulo del tab del navegador.
- Se documento que la generacion de PDF en Fase 3 es simulada (result_url = s3://prosperas-reports/<id>.pdf) y se anoto que Fase 4 debe incluir S3 real, generacion de archivo y URL pre-firmada.
- Se expandieron los entregables de Fase 4 para incluir: bucket S3, generacion real de PDF/CSV con weasyprint o reportlab, upload via boto3, result_url como URL pre-firmada con TTL de 1 hora, y endpoint GET /jobs/{id}/download.
- Se registro el commit caf2509 como cierre oficial de Fase 3.
- Se actualizo el estado global a "Fase 3 commiteada - preparando Fase 4".

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