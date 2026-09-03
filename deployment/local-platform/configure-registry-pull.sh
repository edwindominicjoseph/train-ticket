#!/usr/bin/env bash
set -euo pipefail

cluster_name="${KIND_CLUSTER_NAME:-train-ticket-dev}"
registry_ip="$(kubectl -n registry get service registry -o jsonpath='{.spec.clusterIP}')"
registry_host="registry.registry.svc.cluster.local:5000"

for node in $(kind get nodes --name "$cluster_name"); do
  docker exec "$node" mkdir -p "/etc/containerd/certs.d/$registry_host"
  docker exec -i "$node" sh -c "cat >'/etc/containerd/certs.d/$registry_host/hosts.toml'" <<EOF
server = "http://$registry_ip:5000"

[host."http://$registry_ip:5000"]
  capabilities = ["pull", "resolve"]
  skip_verify = true
EOF
done

echo "Configured kind nodes to pull $registry_host through $registry_ip."
