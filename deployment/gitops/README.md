# Local GitOps production environment

Argo CD owns the manifests in `deployment/gitops/prod`. Jenkins may change only
the pinned image digest in that directory and push the resulting Git commit.
Argo CD then reconciles that commit into `train-ticket-prod`; Jenkins has no RBAC
permission to modify production workloads directly.

## Bootstrap secrets

Secrets deliberately stay out of Git. For a local WSL environment, store them
in a WSL-native file that is readable only by your account:

```bash
./deployment/gitops/bootstrap-prod-secrets.sh --init
```

The `--init` option creates the file only when it does not already exist. The
script validates its permissions, loads the variables, and sends their values
directly to the Kubernetes API. It writes no Kubernetes Secret manifest to disk
and is safe to rerun when applying existing values. Set
`TRAIN_TICKET_PROD_ENV_FILE` to use a different file. Explicitly exported
variables continue to work when the file does not exist.

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
