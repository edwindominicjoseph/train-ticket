# Local Travel and Route service CI/CD test environment

This local kind environment runs the Travel and Route services with dedicated MySQL instances. The same Git-SHA-tagged images are tested and deployed; Kubernetes does not rebuild them. Both services use the Nacos instance bootstrapped by the local platform manifests.

## Prerequisites

Docker Desktop, `kind`, `kubectl`, Bash, and curl must be available. Jenkins also needs access to the Docker daemon and the kubeconfig used by kind.

## Create the cluster

```bash
./deployment/local-test/create-cluster.sh
```

If the script reports an unreachable old cluster, explicitly recreate it:

```bash
kind delete cluster --name train-ticket-dev
./deployment/local-test/create-cluster.sh
```

## Run the pipeline manually

```bash
export IMAGE="ts-travel-service:$(git rev-parse --short=12 HEAD)"

docker run --rm \
  -v "$PWD:/workspace" \
  -v train-ticket-m2-cache:/root/.m2 \
  -w /workspace \
  maven:3.9.9-eclipse-temurin-8 \
  mvn --batch-mode -pl ts-travel-service -am clean verify

docker build --pull -t "$IMAGE" ts-travel-service

export TRAVEL_MYSQL_USER=ts
export TRAVEL_MYSQL_PASSWORD='<test password>'
export TRAVEL_MYSQL_ROOT_PASSWORD='<test root password>'
export JWT_SECRET='<test secret containing at least 32 random bytes>'
IMAGE="$IMAGE" ./deployment/local-test/deploy.sh
./deployment/local-test/smoke-test.sh
```

The kind NodePort is exposed on `http://127.0.0.1:12347`, avoiding the
`12346` port commonly used by a Compose or manually started Travel container.

Use test-only credentials. The deploy script creates or updates the Kubernetes Secret without writing its values to a repository file.
The local JDBC URL permits MySQL public-key retrieval because this isolated test
cluster disables database TLS. Do not copy that setting into production.

## Jenkins credentials

Create these credentials before using `jenkins-ci/Jenkinsfile.local`:

- `travel-mysql-test`: username/password credential
- `travel-mysql-root-test`: secret-text credential
- `travel-jwt-test`: secret-text credential containing at least 32 random bytes

The Jenkins agent must use the same kind kubeconfig and Docker daemon as the cluster.

## Bootstrap Route service dependencies

Jenkins can update Deployments but deliberately cannot manage Secrets, Services,
or StatefulSets. Before the first Route pipeline run, create the test-only database
Secret and apply the admin-owned resources (plus the initial Deployment):

```bash
kubectl -n train-ticket-test create secret generic ts-route-mysql \
  --from-literal=username='<test user>' \
  --from-literal=password='<test password>' \
  --from-literal=root-password='<test root password>'
kubectl apply -f deployment/local-test/route-mysql.yaml
kubectl apply -f deployment/local-test/route-service.yaml
kubectl apply -f deployment/local-test/route.yaml
kubectl -n train-ticket-test rollout status statefulset/ts-route-mysql --timeout=300s
```

The Route workload reads its JWT from the existing `ts-travel-runtime` Secret.
Do not commit the database Secret.

## Inspect or remove the environment

```bash
kubectl -n train-ticket-test get all,pvc
kubectl -n train-ticket-test logs deployment/ts-travel-service
kind delete cluster --name train-ticket-dev
```
