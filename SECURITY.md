# Security policy

## Secrets

Never commit passwords, API keys, signing keys, private keys, access tokens, or
generated Kubernetes Secret manifests. Copy `.env.example` to an ignored local
file and replace every placeholder with a development-only value.

Production secrets must be generated uniquely per environment and delivered by
a secrets manager. The current deployment generator accepts secrets through
environment variables for compatibility, but this is an interim mechanism;
production deployments should use External Secrets Operator (or an equivalent
cloud-native integration) so plaintext values are not written to disk.

Required shared values:

- `JWT_SECRET`: at least 32 random characters; shared only by Java services that
  issue or validate Train Ticket JWTs.
- `EMAIL_PASSWORD`: the notification provider's application password.
- `NACOS_DB_PASSWORD`: Nacos database password.
- `TS_MYSQL_PASSWORD`: database password used by the deployment generator.

Generate development values with a cryptographically secure generator. For
example:

```bash
openssl rand -base64 48
```

Do not reuse development values in staging or production.

## Rotation

The historical repository contained database, email, and JWT credentials.
Removing those literals from the current tree does not remove them from Git
history. Treat every historical value as compromised and rotate it before any
deployment. JWT rotation invalidates existing tokens unless overlapping keys
are implemented.

## Checks

Run before committing:

```bash
make security-check
make validate-inventory
```

Security checks also run on pushes to `master` and on pull requests.
