---
title: IDP ready checklist
nav_order: 2
domain: public
last_reviewed_on: 2025-01-06
review_in: 6 months
parent: Onboarding
---

# IDP Ready Checklist

> Formáìet med denne tjekliste er at sikre, at du og dine dine containers fár maksimalt udbytte af IDP-platformen 

---

## ✅ Grundlæggende container best practices

- [ ] **Minimal base image**  
  Brug Alpine, Distroless eller lignende for at reducere angrebsflade og image-størrelse.

- [ ] **Multi-stage builds**  
  Udnyt `multi-stage Dockerfiles` for rene runtime images.

- [ ] **Versionsstyring**  
  Brug semantiske versioner og tag images med `git sha`, `semver` og `latest` (kun til test).

- [ ] **Healthchecks**  
  Angiv `HEALTHCHECK` for bedre container lifecycle management.

---

## 🔐 Sikkerhed & Compliance (Falco, Kyverno, SPIRE)

- [ ] **Kør som non-root**  
  Konfigurer bruger i Dockerfile – kræves af Falco og Kyverno policies.

- [ ] **Security scanning**  
  Brug f.eks. `Trivy`, `Grype` i CI – kritiske CVEs skal blokere builds.

- [ ] **SPIRE/SPIFFE integration (valgfri)**  
  Understøt SPIFFE ID'er for secure workload identity via SPIRE-agent.

- [ ] **Overhold Kyverno policies**  
  Undgå brug af `:latest`, kræv ressourcegrænser, sikre mounts osv.

---

## 🔍 Observability & Tracing (Grafana, Loki, Mimir, Tempo, Prometheus)

- [ ] **Structured logging (Loki)**  
  Log i JSON-format med kontekstfelter som `service`, `env`, `trace_id`, `request_id`.

- [ ] **Brug stdout/stderr til logs**  
  Undgå logfiler – logs samles automatisk op og sendes til Loki.

- [ ] **Metrics med Prometheus SDK**  
  Eksponér relevante metrics via `/metrics` endpoint i Prometheus-format.

- [ ] **Tracing via OpenTelemetry SDK**  
  Instrumentér appen med spans og traces via OpenTelemetry – auto-instrumentering foretrækkes.

- [ ] **Trace eksport til Tempo**  
  Konfigurer eksport til Tempo via OpenTelemetry Collector.

- [ ] **Dashboards & alerts (Grafana + Mimir)**  
  Sørg for at app-metrics vises i eksisterende dashboards eller medfølger som JSON-konfig.

---

## 🤖 GitOps & Continuous Deployment (ArgoCD)

- [ ] **Helm charts eller K8s manifests**  
  Versionér alt i Git og hold konfig adskilt fra kode.

- [ ] **ArgoCD compatible**  
  Manifests skal være deklarative, idempotente og fri for `kubectl apply` afhængigheder.

- [ ] **Sync hooks og health checks**  
  Brug ArgoCD hooks til migreringer og definer health i `status:` blocks.

---

## ⚙️ Workflow Support (Argo Workflows)

- [ ] **CLI-kompatibel container**  
  Containere skal kunne køre som command-line tools i workflows.

- [ ] **Init containers & volume mounts**  
  Understøt midlertidig storage og init-processer, hvis nødvendigt.

- [ ] **Exit codes og fejlhåndtering**  
  Returnér korrekte `exit codes` – Argo bruger dem til status.

---

## 📦 CI/CD Integration

- [ ] **Immutable tagging**  
  Brug `git SHA` eller `build number` i image-tags.

- [ ] **CI pipeline med image scan og push**  
  Inkluder linting, tests, security scan og image push til registry.

- [ ] **PRs til GitOps repo**  
  Automatisk opdatering af manifests ved nyt image – gerne med bot eller CI-step.

---

## 🧪 Testing & Quality Gates

- [ ] **Unit og integrationstests i CI**  
  Tests skal dække kritiske path og fejle pipeline ved fejl.

- [ ] **Statisk analyse & linting**  
  Brug `hadolint`, `yamllint`, `shellcheck`, osv.

- [ ] **End-to-end tests (valgfrit)**  
  Kan køres som separate workflows eller jobs i Argo Workflows.

---

## 📖 Metadata & Dokumentation

- [ ] **OCI standard labels i image**  
  Brug labels som `org.opencontainers.image.source`, `version`, `maintainer`.

- [ ] **README med brug og konfig**  
  Beskriv image-brug, CLI-argumenter, miljøvariabler og evt. konfig-struktur.

- [ ] **Changelog**  
  Beskriv ændringer mellem versions – nyttigt for review og debug.

---

## ✅ Klar til Onboard?

Når alle relevante punkter er opfyldt:

1. Gennemgå checklisten sammen med IDP-teamet.
2. Opret en PR til GitOps repo med Helm/manifests.
3. Koordinér onboarding til dashboards, tracing, metrics og policies.

---

*Sidst opdateret: {{ dato }}*

