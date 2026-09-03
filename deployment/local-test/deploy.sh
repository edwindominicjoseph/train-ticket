#!/usr/bin/env bash
set -euo pipefail

cluster_name="${KIND_CLUSTER_NAME:-train-ticket-dev}"
namespace="${K8S_NAMESPACE:-train-ticket-test}"
image="${IMAGE:?IMAGE is required, for example ts-travel-service:abc123}"

: "${TRAVEL_MYSQL_USER:?TRAVEL_MYSQL_USER is required}"
: "${TRAVEL_MYSQL_PASSWORD:?TRAVEL_MYSQL_PASSWORD is required}"
: "${TRAVEL_MYSQL_ROOT_PASSWORD:?TRAVEL_MYSQL_ROOT_PASSWORD is required}"
: "${JWT_SECRET:?JWT_SECRET is required}"

kind load docker-image "$image" --name "$cluster_name"
kubectl apply -f deployment/local-test/namespace.yaml
kubectl -n "$namespace" create secret generic ts-travel-mysql \
  --from-literal=username="$TRAVEL_MYSQL_USER" \
  --from-literal=password="$TRAVEL_MYSQL_PASSWORD" \
  --from-literal=root-password="$TRAVEL_MYSQL_ROOT_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "$namespace" create secret generic ts-travel-runtime \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f deployment/local-test/mysql.yaml
kubectl -n "$namespace" rollout status statefulset/ts-travel-mysql --timeout=180s
kubectl apply -f deployment/local-test/travel-service.yaml
kubectl set image --local -f deployment/local-test/travel.yaml \
  ts-travel-service="$image" -o yaml | kubectl apply -f -
kubectl -n "$namespace" rollout status deployment/ts-travel-service --timeout=240s
