# Local Travel-service CI/CD test environment

This is the first deployable vertical slice: MySQL plus `ts-travel-service` on a local kind cluster. The same Git-SHA-tagged image is tested and deployed; Kubernetes does not rebuild it.
Nacos discovery is disabled in this minimal slice because no discovery server is
deployed. Add Nacos when cross-service discovery is introduced.

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

## Inspect or remove the environment

```bash
kubectl -n train-ticket-test get all,pvc
kubectl -n train-ticket-test logs deployment/ts-travel-service
kind delete cluster --name train-ticket-dev
```
