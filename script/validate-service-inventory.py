#!/usr/bin/env python3
"""Validate that source, build, routing, and active deployment inventories agree."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVICE_NAME = re.compile(r"ts-[a-z0-9-]+(?:-service|-dashboard)")


def names(path: Path, pattern: str) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(pattern, text, flags=re.MULTILINE))


def compare(label: str, actual: set[str], expected: set[str]) -> list[str]:
    errors = []
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{label}: missing {', '.join(missing)}")
    if extra:
        errors.append(f"{label}: unexpected {', '.join(extra)}")
    return errors


source_apps = {
    path.name
    for path in ROOT.glob("ts-*")
    if path.is_dir() and path.name != "ts-common"
}
java_modules = {
    path.name for path in ROOT.glob("ts-*") if (path / "pom.xml").is_file()
}
maven_modules = names(ROOT / "pom.xml", r"<module>([^<]+)</module>")

compose_pattern = r"^  (ts-[a-z0-9-]+(?:-service|-dashboard)):\s*$"
k8s_pattern = r"^  name: (ts-[a-z0-9-]+(?:-service|-dashboard))\s*$"
gateway_pattern = (
    r"(?:lb://\$\{[^:]+:|http://\$\{[^:]+:)"
    r"(ts-[a-z0-9-]+(?:-service|-dashboard))"
)

root_compose = names(ROOT / "docker-compose.yml", compose_pattern)
quick_compose = names(
    ROOT / "deployment/docker-compose-manifests/quickstart-docker-compose.yml",
    compose_pattern,
)
k8s_services = names(
    ROOT / "deployment/kubernetes-manifests/quickstart-k8s/yamls/svc.yaml",
    k8s_pattern,
)
k8s_deployments = names(
    ROOT / "deployment/kubernetes-manifests/quickstart-k8s/yamls/deploy.yaml.sample",
    k8s_pattern,
)
gateway_targets = names(
    ROOT / "ts-gateway-service/src/main/resources/application.yml",
    gateway_pattern,
)

# The gateway and UI are entry points. Delivery is a RabbitMQ consumer with no HTTP controller.
expected_gateway_targets = source_apps - {
    "ts-delivery-service",
    "ts-gateway-service",
    "ts-ui-dashboard",
}

errors = []
errors += compare("Maven modules", maven_modules, java_modules)
errors += compare("root Docker Compose", root_compose, source_apps)
errors += compare("quick-start Docker Compose", quick_compose, source_apps)
errors += compare("Kubernetes Services", k8s_services, source_apps)
errors += compare("Kubernetes Deployments", k8s_deployments, source_apps)
errors += compare("gateway targets", gateway_targets, expected_gateway_targets)

active_files = [
    ROOT / "pom.xml",
    ROOT / "docker-compose.yml",
    ROOT / "ts-gateway-service/src/main/resources/application.yml",
    ROOT / "deployment/docker-compose-manifests/quickstart-docker-compose.yml",
    ROOT / "deployment/kubernetes-manifests/quickstart-k8s/yamls/svc.yaml",
    ROOT / "deployment/kubernetes-manifests/quickstart-k8s/yamls/deploy.yaml.sample",
]
for path in active_files:
    text = path.read_text(encoding="utf-8")
    for stale in ("ts-ticketinfo-service", "ts-food-map-service", "servicee"):
        if stale in text:
            errors.append(f"{path.relative_to(ROOT)}: stale reference {stale}")

if errors:
    print("Service inventory validation failed:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"Service inventory is consistent: {len(source_apps)} applications, "
    f"{len(java_modules)} Maven modules, {len(gateway_targets)} gateway targets."
)
