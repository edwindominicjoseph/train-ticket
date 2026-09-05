#!/usr/bin/env bash
set -euo pipefail

env_file="${TRAIN_TICKET_PROD_ENV_FILE:-${XDG_CONFIG_HOME:-${HOME}/.config}/train-ticket/prod.env}"

if [[ "${1:-}" == "--init" ]]; then
  command -v openssl >/dev/null || {
    echo "openssl is required to generate production credentials." >&2
    exit 1
  }
  if [[ -e "${env_file}" ]]; then
    echo "Refusing to overwrite existing credential file ${env_file}." >&2
    exit 1
  fi

  install -d -m 700 "$(dirname "${env_file}")"
  umask 077
  {
    printf 'TRAVEL_MYSQL_USER=ts\n'
    printf 'TRAVEL_MYSQL_PASSWORD=%s\n' "$(openssl rand -hex 32)"
    printf 'TRAVEL_MYSQL_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 32)"
    printf 'JWT_SECRET=%s\n' "$(openssl rand -hex 48)"
  } >"${env_file}"
  chmod 600 "${env_file}"
  echo "Generated protected credential file ${env_file}."
fi

if [[ -f "${env_file}" ]]; then
  permissions="$(stat -c '%a' "${env_file}")"
  if [[ "${permissions}" != "600" && "${permissions}" != "400" ]]; then
    echo "Refusing to load ${env_file}: expected permissions 600, found ${permissions}." >&2
    exit 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "${env_file}"
  set +a
fi

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
