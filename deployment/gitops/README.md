# Local GitOps production environment

Argo CD owns the manifests in `deployment/gitops/prod`. Jenkins may change only
the pinned image digest in that directory and push the resulting Git commit.
Argo CD then reconciles that commit into `train-ticket-prod`; Jenkins has no RBAC
permission to modify production workloads directly.

## Bootstrap secrets

Secrets deliberately stay out of Git. Export strong local values, then run:

```bash
export TRAVEL_MYSQL_USER=ts
export TRAVEL_MYSQL_PASSWORD='<generated value>'
export TRAVEL_MYSQL_ROOT_PASSWORD='<different generated value>'
export JWT_SECRET='<at least 32 random bytes>'
./deployment/gitops/bootstrap-prod-secrets.sh
```

The script sends values directly to the Kubernetes API. It writes no secret
manifest to disk and is safe to rerun when rotating values.

## Enable reconciliation

Do this only after the GitOps files and a real image digest are committed and
pushed to `master`:

```bash
kubectl apply -f deployment/gitops/argocd/train-ticket-project.yaml
kubectl apply -f deployment/gitops/argocd/travel-prod-application.yaml
kubectl -n argocd get application travel-prod
```

Do not apply the Application while the production kustomization still contains
the all-zero placeholder digest.
