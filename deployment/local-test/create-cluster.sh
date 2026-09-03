#!/usr/bin/env bash
set -euo pipefail

cluster_name="${KIND_CLUSTER_NAME:-train-ticket-dev}"

if kind get clusters | grep -Fxq "$cluster_name"; then
  if kubectl --context "kind-$cluster_name" get nodes >/dev/null 2>&1; then
    echo "kind cluster $cluster_name is already ready."
    exit 0
  fi
  echo "The existing $cluster_name cluster is not reachable; recreate it manually:"
  echo "  kind delete cluster --name $cluster_name"
  echo "  ./deployment/local-test/create-cluster.sh"
  exit 1
fi

kind create cluster --config deployment/local-test/kind-config.yaml
kubectl config use-context "kind-$cluster_name"
kubectl wait --for=condition=Ready node --all --timeout=120s
