#!/bin/bash
set -euo pipefail

echo "[init] Inicializando recursos AWS locales para Prosperas..."

if ! awslocal dynamodb describe-table --table-name prosperas-jobs >/dev/null 2>&1; then
  echo "[init] Creando tabla DynamoDB prosperas-jobs..."
  awslocal dynamodb create-table \
    --table-name prosperas-jobs \
    --attribute-definitions AttributeName=job_id,AttributeType=S AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=job_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes '[{"IndexName":"user_id-index","KeySchema":[{"AttributeName":"user_id","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"}}]'
fi

echo "[init] Creando o validando cola DLQ..."
DLQ_URL=$(awslocal sqs create-queue --queue-name prosperas-jobs-dlq --output text --query QueueUrl)
DLQ_ARN=$(awslocal sqs get-queue-attributes --queue-url "$DLQ_URL" --attribute-names QueueArn --output text --query Attributes.QueueArn)

echo "[init] Creando o validando cola principal..."
awslocal sqs create-queue \
  --queue-name prosperas-jobs-queue \
  --attributes VisibilityTimeout=30,ReceiveMessageWaitTimeSeconds=20,RedrivePolicy="{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}" \
  >/dev/null

echo "[init] Creando o validando cola de prioridad..."
awslocal sqs create-queue \
  --queue-name prosperas-jobs-priority-queue \
  --attributes VisibilityTimeout=30,ReceiveMessageWaitTimeSeconds=20 \
  >/dev/null

echo "[init] Recursos locales listos."
