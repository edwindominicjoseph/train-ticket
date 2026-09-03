#!/usr/bin/env bash
set -euo pipefail

: "${TRAVEL_MYSQL_USER:?set TRAVEL_MYSQL_USER}"
: "${TRAVEL_MYSQL_PASSWORD:?set TRAVEL_MYSQL_PASSWORD}"
: "${TRAVEL_MYSQL_ROOT_PASSWORD:?set TRAVEL_MYSQL_ROOT_PASSWORD}"
: "${JWT_SECRET:?set JWT_SECRET}"

namespace="train-ticket-prod"
kubectl create namespace "${namespace}" --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "${namespace}" create secret generic ts-travel-mysql \
  --from-literal=username="${TRAVEL_MYSQL_USER}" \
  --from-literal=password="${TRAVEL_MYSQL_PASSWORD}" \
  --from-literal=root-password="${TRAVEL_MYSQL_ROOT_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "${namespace}" create secret generic ts-travel-runtime \
  --from-literal=jwt-secret="${JWT_SECRET}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Production runtime secrets are present in namespace ${namespace}."
