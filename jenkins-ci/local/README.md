# Local Jenkins UI

This Jenkins controller runs in Docker Desktop and schedules disposable build
agents in Kubernetes. It does not mount the Docker socket and does not build on
the controller.

```bash
export JENKINS_K8S_TOKEN="$(kubectl -n jenkins-agents get secret \
  jenkins-agent-token -o jsonpath='{.data.token}' | base64 -d)"
docker compose -f jenkins-ci/local/compose.yaml up -d --build
```

Open <http://127.0.0.1:8080>. Obtain the one-time setup password with:

```bash
docker exec train-ticket-jenkins \
  cat /var/jenkins_home/secrets/initialAdminPassword
```

The Jenkins container joins the kind Docker network at `172.18.0.10`. JCasC
configures the Kubernetes cloud and injects the restricted service-account token
from the startup environment. The token is not stored in this repository.

Create a Pipeline job using **Pipeline script from SCM**, select Git, and set the
script path to `jenkins-ci/Jenkinsfile.local`.

Add a Jenkins username/password credential named `github-train-ticket` only when
you are ready to enable the manually approved GitOps commit to `master`. Use a
fine-grained token restricted to this repository's contents.

Argo CD is persistently available at <https://127.0.0.1:8082>. New clusters
created with `deployment/local-test/kind-config.yaml` publish the Argo CD HTTPS
NodePort on that loopback-only host port. After installing Argo CD, configure
its fixed NodePorts with:

```bash
kubectl apply -f deployment/local-platform/argocd-server-nodeport.yaml
```

An existing kind cluster must be recreated before newly added
`extraPortMappings` take effect. Until then, a loopback-only Docker proxy can
bridge the fixed NodePort without recreating the cluster. Remove that proxy
before a future cluster recreation so port 8082 is available to the kind node:

```bash
docker stop argocd-local-proxy
docker rm argocd-local-proxy
```

The initial admin password remains in the Kubernetes Secret; retrieve it only
when signing in:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d
```
