#!/usr/bin/env bash
set -eu

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_dir"' EXIT

source "$repo_root/hack/deploy/gen-mysql-secret.sh"
secret_yaml="$temp_dir/secret.yaml"

export JWT_SECRET="unit-test-jwt-secret-32-characters-minimum"
export EMAIL_PASSWORD="unit-test-email-password"

gen_secret_for_services "test-user" "test-password" "test-database" "shared-mysql-leader"
grep -Fq 'TRAVEL_MYSQL_HOST: "shared-mysql-leader"' "$secret_yaml"
grep -Fq 'ORDER_MYSQL_HOST: "shared-mysql-leader"' "$secret_yaml"
test "$(grep -Fc 'name: ts-jwt' "$secret_yaml")" -eq 1

gen_secret_for_services "test-user" "test-password" "test-database"
grep -Fq 'TRAVEL_MYSQL_HOST: "ts-travel-mysql-leader"' "$secret_yaml"
grep -Fq 'ORDER_MYSQL_HOST: "ts-order-mysql-leader"' "$secret_yaml"

if (unset JWT_SECRET; gen_secret_for_services "test-user" "test-password" "test-database"); then
  echo "generator accepted a missing JWT_SECRET" >&2
  exit 1
fi

echo "MySQL Secret generator tests passed."
