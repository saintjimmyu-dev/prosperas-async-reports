# Terraform de Fase 4 (AWS real)

Este directorio aprovisiona una base productiva minima para Prosperas:
- ECR para imagen backend/worker
- DynamoDB para jobs
- SQS principal, prioridad y DLQ
- IAM Role + Instance Profile para EC2
- EC2 Amazon Linux 2023 con Docker + SSM Agent
- Security Group para API en puerto 8000

## 1. Requisitos

- Terraform >= 1.6
- AWS CLI autenticado contra la cuenta destino
- Permisos para EC2, IAM, SQS, DynamoDB, ECR y SSM

## 2. Uso rapido

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## 3. Outputs clave

Despues de apply, usa estos valores para GitHub Secrets:
- ecr_repository_url
- ec2_instance_id
- dynamodb_table_name
- sqs_queue_url
- sqs_priority_queue_url
- sqs_dlq_url

## 4. Destroy

```bash
terraform destroy
```

## 5. Nota de seguridad

Para demos rapidas se deja `allowed_api_cidr = 0.0.0.0/0`. En entrega final se recomienda restringir a IPs controladas o usar reverse proxy con TLS.
