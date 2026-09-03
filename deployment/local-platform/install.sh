#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f deployment/local-test/namespace.yaml
kubectl apply -f deployment/local-platform/namespaces.yaml
kubectl apply -f deployment/local-platform/jenkins-rbac.yaml
kubectl apply -f deployment/local-platform/registry.yaml
kubectl -n registry rollout status deployment/registry --timeout=180s
./deployment/local-platform/configure-registry-pull.sh
kubectl apply -f deployment/local-platform/buildkit.yaml
kubectl -n buildkit rollout status deployment/buildkitd --timeout=180s
