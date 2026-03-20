# Resumen de CI/CD

```mermaid
flowchart LR
    Dev[Desarrollador] -->|Push a main| GH[GitHub Actions]
    GH --> T1[Ejecutar checks y pruebas]
    T1 --> T2[Construir imagen de API]
    T1 --> T3[Construir imagen de Worker]
    T2 --> ECR[ECR]
    T3 --> ECR
    ECR --> DEPLOY[Desplegar en EC2]
    DEPLOY --> PROD[API y Worker en produccion]
```

Notas:
- La ruta de despliegue es intencionalmente simple para reducir riesgo de entrega.
- El README final debe mostrar el badge de GitHub Actions y la URL publica de produccion.