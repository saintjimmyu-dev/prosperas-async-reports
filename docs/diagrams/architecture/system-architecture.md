# Arquitectura del Sistema

```mermaid
flowchart LR
    U[Usuario] --> FE[Frontend React]
    FE -->|JWT + REST| API[FastAPI API on EC2]
    API -->|Guardar job PENDING| DDB[(Jobs en DynamoDB)]
    API -->|Publicar mensaje| Q[Cola principal SQS]
    API -->|Ruta opcional de prioridad| PQ[Cola SQS de prioridad]
    Q --> W[Worker en EC2]
    PQ --> W
    W -->|Actualizar PROCESSING/COMPLETED/FAILED| DDB
    W -->|Fallos repetidos| DLQ[SQS Dead Letter Queue]
    FE -->|Polling o WebSocket| API
    API -->|Datos de estado| FE
    GH[GitHub Actions] --> ECR[ECR]
    ECR --> API
    ECR --> W
    W --> CW[CloudWatch]
    API --> CW
```

Notas:
- La arquitectura prioriza simplicidad, bajo costo y facilidad de explicacion.
- La API y el worker estan contenerizados por separado, pero pueden ejecutarse en el mismo host EC2 durante el reto.
- El soporte de cola de prioridad queda reservado para el bonus B1.