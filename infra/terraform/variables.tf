variable "aws_region" {
  description = "Region AWS para recursos de produccion"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nombre del proyecto para tags y nombres"
  type        = string
  default     = "prosperas"
}

variable "environment" {
  description = "Ambiente objetivo"
  type        = string
  default     = "prod"
}

variable "ec2_instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "ec2_key_name" {
  description = "Nombre de Key Pair para SSH (opcional)"
  type        = string
  default     = ""
}

variable "enable_ssh" {
  description = "Si es true, abre puerto 22 segun ssh_cidr"
  type        = bool
  default     = false
}

variable "ssh_cidr" {
  description = "CIDR permitido para SSH cuando enable_ssh=true"
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_api_cidr" {
  description = "CIDR permitido para exponer API en puerto 8000"
  type        = string
  default     = "0.0.0.0/0"
}

variable "ecr_repository_name" {
  description = "Nombre del repositorio ECR para imagen backend/worker"
  type        = string
  default     = "prosperas-backend"
}

variable "dynamodb_table_name" {
  description = "Nombre de tabla DynamoDB de jobs"
  type        = string
  default     = "prosperas-jobs"
}

variable "dynamodb_user_index_name" {
  description = "Nombre del GSI por user_id"
  type        = string
  default     = "user_id-index"
}

variable "jobs_queue_name" {
  description = "Nombre cola principal"
  type        = string
  default     = "prosperas-jobs-queue"
}

variable "priority_queue_name" {
  description = "Nombre cola de prioridad"
  type        = string
  default     = "prosperas-jobs-priority-queue"
}

variable "dlq_queue_name" {
  description = "Nombre cola DLQ"
  type        = string
  default     = "prosperas-jobs-dlq"
}

variable "jwt_secret_key" {
  description = "Secreto JWT para produccion (solo referencia documental)"
  type        = string
  default     = ""
  sensitive   = true
}
