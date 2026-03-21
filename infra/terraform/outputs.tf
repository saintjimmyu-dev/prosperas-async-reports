output "ecr_repository_url" {
  description = "URL del repositorio ECR"
  value       = aws_ecr_repository.backend.repository_url
}

output "ec2_instance_id" {
  description = "ID de instancia EC2 para despliegue via SSM"
  value       = aws_instance.app.id
}

output "ec2_public_ip" {
  description = "IP publica de la instancia"
  value       = aws_instance.app.public_ip
}

output "ec2_public_dns" {
  description = "DNS publico de la instancia"
  value       = aws_instance.app.public_dns
}

output "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB"
  value       = aws_dynamodb_table.jobs.name
}

output "sqs_queue_url" {
  description = "URL de la cola principal"
  value       = aws_sqs_queue.jobs.url
}

output "sqs_priority_queue_url" {
  description = "URL de la cola de prioridad"
  value       = aws_sqs_queue.priority.url
}

output "sqs_dlq_url" {
  description = "URL de la DLQ"
  value       = aws_sqs_queue.dlq.url
}

output "github_secrets_requeridos" {
  description = "Checklist de secretos requeridos para .github/workflows/deploy.yml"
  value = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "EC2_INSTANCE_ID",
    "ECR_REPOSITORY",
    "APP_ENV",
    "JWT_SECRET_KEY",
    "DYNAMODB_TABLE_NAME",
    "DYNAMODB_USER_INDEX_NAME",
    "SQS_QUEUE_URL",
    "SQS_PRIORITY_QUEUE_URL",
    "SQS_DLQ_URL",
    "CORS_ALLOWED_ORIGINS",
    "WORKER_MAX_ATTEMPTS",
    "WORKER_RETRY_BASE_SECONDS",
    "WORKER_RETRY_MAX_SECONDS",
    "DEMO_USER_USERNAME",
    "DEMO_USER_PASSWORD"
  ]
}
