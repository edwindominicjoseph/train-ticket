# Local CI/CD Platform Infrastructure

This directory contains the shared platform components deployed into the local `train-ticket-dev` kind cluster. It provides a completely self-contained, rootless CI/CD ecosystem inside Kubernetes:

- **Private Container Registry**: In-cluster OCI/Docker registry backed by persistent storage.
- **Rootless BuildKit**: In-cluster daemon (`moby/buildkit:v0.25.1-rootless`) for building container images without mounting the host Docker socket or running with root privileges.
- **Node Pull Configuration**: Node-level containerd configuration allowing kind nodes to resolve and pull from the insecure in-cluster registry over HTTP.
- **Jenkins Agent RBAC**: Scoped ServiceAccount and RoleBindings enabling dynamic Jenkins agents to run in `jenkins-agents` and deploy workloads to `train-ticket-test`.
- **Argo CD Exposure**: NodePort configuration exposing the Argo CD GitOps server on loopback (`127.0.0.1:8082`).

---

## Prerequisites

Ensure the local tools and base kind cluster are ready before installing the platform:

- Docker Desktop, `kind`, `kubectl`, Bash, and curl.
- The `train-ticket-dev` cluster must be running. If not already created, spin it up using:

```bash
./deployment/local-test/create-cluster.sh
```

---

## Install the Platform

Run the automated installer:

```bash
./deployment/local-platform/install.sh
```

This script:
1. Creates the required namespaces (`jenkins-agents`, `buildkit`, `registry`, `train-ticket-prod`, and `train-ticket-test`).
2. Deploys the Jenkins RBAC resources (`ServiceAccount`, token Secret, and Roles).
3. Deploys the internal container registry and waits for the rollout to complete.
4. Executes `./deployment/local-platform/configure-registry-pull.sh` to configure containerd within each kind node.
5. Deploys the rootless BuildKit daemon and verifies readiness.

---

## Verify with Smoke Tests

Two batch jobs are provided to verify image building and image pulling in the local cluster:

1. **Verify In-Cluster Image Build**:
   ```bash
   kubectl apply -f deployment/local-platform/smoke-build.yaml
   kubectl -n buildkit wait --for=condition=complete job/platform-smoke-build --timeout=120s
   ```
   *Builds a minimal BusyBox image using `buildctl` against the `buildkitd` daemon and pushes it to `registry.registry.svc.cluster.local:5000/platform-smoke:latest`.*

2. **Verify Node Image Pull**:
   ```bash
   kubectl apply -f deployment/local-platform/smoke-pull.yaml
   kubectl -n buildkit wait --for=condition=complete job/platform-smoke-pull --timeout=120s
   ```
   *Pulls and runs `platform-smoke:latest` from the internal registry to verify containerd node resolution and pulling.*

3. **Clean up Smoke Jobs**:
   ```bash
   kubectl -n buildkit delete job platform-smoke-build platform-smoke-pull
   ```

---

## Jenkins Agent Integration

The platform provides dedicated RBAC for Jenkins to dynamically spawn disposable Kubernetes build agents:

- **Service Account**: `jenkins-agent` in the `jenkins-agents` namespace.
- **Retrieve Authentication Token**:
  ```bash
  kubectl -n jenkins-agents get secret jenkins-agent-token -o jsonpath='{.data.token}' | base64 -d
  ```
- **Permissions Granted**:
  - Full pod lifecycle management (`pods`, `pods/log`, `pods/exec`) in `jenkins-agents`.
  - Deployment and service management (`deployments`, `pods`, `services`) in `train-ticket-test`.

Refer to `jenkins-ci/local/README.md` for running the local Jenkins controller in Docker.

---

## Argo CD (GitOps) Access

Argo CD server is exposed via static NodePorts (`30080` HTTP, `30443` HTTPS):

```bash
kubectl apply -f deployment/local-platform/argocd-server-nodeport.yaml
```

- **Access URL**: <https://127.0.0.1:8082>
- **Retrieve Admin Password**:
  ```bash
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
  ```

---

## Inspect or Troubleshoot

```bash
# Check platform pods across namespaces
kubectl -n registry get all,pvc
kubectl -n buildkit get all
kubectl -n jenkins-agents get sa,secret,role,rolebinding

# View BuildKit daemon logs
kubectl -n buildkit logs deployment/buildkitd -c buildkitd

# View Container Registry logs
kubectl -n registry logs deployment/registry
```

