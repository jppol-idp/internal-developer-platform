---
title: Prometheus metrics scraping
nav_order: 17
parent: How to...
domain: public
permalink: /prometheus-metrics
layout: last-reviewed
last_reviewed_on: 2026-06-18
review_in: 6 months
---
# Prometheus Metrics Scraping

## Table of Contents
- [Introduction](#introduction)
- [Best Practice for Exposing Your Metrics](#best-practice-for-exposing-your-metrics)
- [Configuration Options](#configuration-options)
  - [Option 1: Using idp-advanced Helm Chart](#option-1-using-idp-advanced-helm-chart)
  - [Option 2: Using Custom Chart with ServiceMonitor](#option-2-using-custom-chart-with-servicemonitor)
  - [Option 3: Using Custom Chart with PodMonitor](#option-3-using-custom-chart-with-podmonitor)
- [ServiceMonitor vs PodMonitor for Multi-Replica Deployments](#servicemonitor-vs-podmonitor-for-multi-replica-deployments)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)
- [Framework-Specific Metrics Examples](#framework-specific-metrics-examples)
- [Additional Resources](#additional-resources)

## Introduction
This guide provides instructions for setting up Prometheus metrics scraping for your services in our Kubernetes environment. It focuses on configuration rather than which metrics to create.

## Best Practice for Exposing Your Metrics
We recommend exposing Prometheus metrics on port **9090** under the path **/metrics**. Using this standard configuration will minimize additional modifications required for metrics collection.

## Configuration Options

### Option 1: Using idp-advanced Helm Chart
**Requirements:**
- Minimum version 1.5.0 of the idp-advanced helm chart for ServiceMonitor
- Minimum version 3.5.0 of the idp-advanced helm chart for PodMonitor

**Choosing between ServiceMonitor and PodMonitor:**
The idp-advanced chart supports both ServiceMonitor and PodMonitor. The choice matters when running multiple replicas of an application behind a single service:

- With a **ServiceMonitor**, Prometheus scrapes metrics through the service, which load-balances requests across all pods. Metrics from different pods may be intermixed across scrape intervals. For cumulative metrics (counters) or gauges representing the system state, this is typically fine.
- With a **PodMonitor**, Prometheus discovers and scrapes each pod individually, so per-instance metrics (like individual pod resource usage) stay attributable to the pod that produced them.

If you only need service-level metrics, use a ServiceMonitor. If you need pod-level granularity, use a PodMonitor. See [ServiceMonitor vs PodMonitor for Multi-Replica Deployments](#servicemonitor-vs-podmonitor-for-multi-replica-deployments) for details. Enable either `serviceMonitor` or `podMonitor` for a given application — not both, or metrics will be scraped twice.

**Configuration Steps:**

For **ServiceMonitor**, the chart supports two modes. Pick the one that matches where your application exposes metrics. For **PodMonitor**, see [the PodMonitor section below](#podmonitor).

#### Mode A: Metrics on a dedicated port (recommended)

Use this when your application serves `/metrics` on a separate port (e.g. `9090`), distinct from the port serving normal traffic.

```yaml
service:
  ...existing content...
  port: 80          # your application traffic port
  metrics:
    enabled: true
    port: 9090      # the port your app exposes metrics on — MUST differ from service.port
serviceMonitor:
  enabled: true
```

This creates a dedicated service port named `metrics`, and the ServiceMonitor scrapes that port.

**Why a separate port is preferred:** A dedicated metrics port keeps `/metrics` off the port you expose publicly. If your application is reachable through an Ingress, that Ingress routes to your traffic port (e.g. `80`/`3000`) — so if metrics live on that same port, anyone who can reach the public URL can also fetch `/metrics`. Metrics often leak internal details (hostnames, dependency endpoints, queue depths, error counts, request volumes) that should not be world-readable. By serving metrics on a separate port (e.g. `9090`) that the Ingress does not route to, Prometheus can still scrape it in-cluster via the ServiceMonitor, while it stays unreachable from outside. If you must keep metrics on the application port, ensure your application or middleware blocks external access to `/metrics`.

> **Warning:** `service.metrics.port` must not equal `service.port`. If both share the same number, Kubernetes collapses them into a single port (keeping the `http` one), the `metrics` port is never created, and the ServiceMonitor finds no target — so no metrics reach Grafana even though port-forwarding the endpoint works fine.

#### Mode B: Metrics on the application port

Use this when your application serves `/metrics` on the **same** port as normal traffic (a single port for everything).

```yaml
service:
  ...existing content...
  port: 3000        # single port serving both traffic and /metrics
  metrics:
    enabled: false  # do NOT enable a dedicated metrics port
serviceMonitor:
  enabled: true
  portName: http    # scrape the main service port (named "http")
```

When `service.metrics.enabled` is `false`, the ServiceMonitor scrapes the port named by `serviceMonitor.portName` (defaults to `http`), which is the main service port.

#### PodMonitor

To scrape pods directly instead of going through the service, enable a `podMonitor` (chart version 3.5.0 or later). This is the better choice when you need per-pod metrics across multiple replicas — see [the comparison below](#servicemonitor-vs-podmonitor-for-multi-replica-deployments).

The PodMonitor references the **container** port by name, so no extra service port is required. The same two port modes apply.

Metrics on a dedicated port (recommended):

```yaml
service:
  ...existing content...
  port: 80          # your application traffic port
  metrics:
    enabled: true
    port: 9090      # the port your app exposes metrics on — MUST differ from service.port
podMonitor:
  enabled: true
```

Metrics on the application port:

```yaml
service:
  ...existing content...
  port: 3000        # single port serving both traffic and /metrics
  metrics:
    enabled: false  # do NOT enable a dedicated metrics port
podMonitor:
  enabled: true
  portName: http    # scrape the main container port (named "http")
```

Enable either `serviceMonitor` or `podMonitor` for a given application — not both, or metrics will be scraped twice.

If using non-standard ports or paths, refer to:
- The idp-advanced default-values.yaml
- The idp-advanced README.md for additional parameters

### Option 2: Using Custom Chart with ServiceMonitor
Create a serviceMonitor object for your deployment:

**serviceMonitor.yaml**
```yaml
apiVersion: v1
items:
- apiVersion: monitoring.coreos.com/v1
  kind: ServiceMonitor
  metadata:
    name: <service>
  spec:
    endpoints:
    - interval: 30s
      path: /metrics
      port: metrics
      scheme: http
      scrapeTimeout: 10s
    selector:
      matchLabels:
        app.kubernetes.io/instance: <service>
        app.kubernetes.io/name: <service>
kind: List
metadata: {}
```

### Option 3: Using Custom Chart with PodMonitor
If you maintain your own chart (rather than using idp-advanced), you can define a PodMonitor directly. A PodMonitor allows Prometheus to target pods instead of going through a service. This is useful in scenarios where:

- You have pods without a corresponding service
- You want to monitor individual pod metrics separately
- You need to monitor ephemeral or stateless workloads
- You want to bypass service abstractions and target pods directly

**podMonitor.yaml**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: {{ include "your-chart.fullname" . }}
spec:
  selector:
    matchLabels:
      {{- include "your-chart.selectorLabels" . | nindent 6 }}
  podMetricsEndpoints:
  - port: metrics  # The name of the port in the pod spec, not the port number
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
```

**When to use PodMonitor vs ServiceMonitor:**
- Use **ServiceMonitor** when you already have a service exposing your metrics (most common case)
- Use **PodMonitor** when you want to scrape metrics directly from pods without a service

## ServiceMonitor vs PodMonitor for Multi-Replica Deployments

### ServiceMonitor Behavior (Available in idp-advanced chart)
When using a ServiceMonitor with multiple replicas:

- Prometheus scrapes the service endpoint, which load-balances requests across all available pods
- Each scrape may hit a different pod, depending on your service's load balancing algorithm
- Metrics will be an aggregation or sampling from different pods over time
- Pod-specific metrics will be mixed, making it difficult to track individual pod behavior
- Example: If you have 3 replicas and Prometheus scrapes every 30s, it might scrape Pod A, then Pod C, then Pod B in consecutive scrapes

### PodMonitor Behavior (Available in idp-advanced chart)
When using a PodMonitor with multiple replicas:

- Prometheus discovers and scrapes each pod individually
- Each pod's metrics are collected and stored separately
- You can query and analyze metrics on a per-pod basis
- Uses more resources as the number of scrape targets increases with pod count
- Example: If you have 3 replicas and Prometheus scrapes every 30s, it will scrape Pod A, Pod B, and Pod C every 30s

### Choosing the Right Approach
Consider your specific metric requirements:

- Use ServiceMonitor (idp-advanced default) when:
  - You need overall service-level metrics
  - Individual pod identity doesn't matter
  - You want simpler configuration

- Use PodMonitor when:
  - You need to track metrics from specific pods
  - You're troubleshooting issues with specific replicas
  - You need to monitor individual pod behavior

## Validation
To verify your metrics are being properly collected and available:

### Initial Metric Endpoint Verification
Before checking in Grafana, you can verify that your application is exposing metrics correctly:

#### For ServiceMonitor:
1. Port-forward to your service: `kubectl port-forward service/<service-name> 9090:9090`
2. Access metrics directly: `curl http://localhost:9090/metrics`

#### For PodMonitor:
1. Find the specific pod name: `kubectl get pods | grep <application-name>`
2. Port-forward directly to the pod: `kubectl port-forward pod/<pod-name> 9090:9090`
3. Access metrics directly: `curl http://localhost:9090/metrics`

### Using Grafana to Verify Metrics
Once metrics are being scraped by Prometheus, you can verify them in Grafana:

1. Log in to your Grafana instance
2. Navigate to the Explore view (compass icon in the left sidebar)
3. Select "Prometheus" as the data source in the dropdown at the top
4. Use the metrics browser or enter a PromQL query to find your metrics:
   - Simple query example: `{app="{{ include "your-chart.name" . }}"}`
   - Or search for a specific metric: `your_metric_name{app="{{ include "your-chart.name" . }}"}`
5. Click "Run query" to verify your metrics are being collected

## Troubleshooting
Common issues:

### ServiceMonitor Issues:
- **Metrics not appearing in Grafana (but port-forward to /metrics works):** The ServiceMonitor references a service port *by name* that does not exist. With the idp-advanced chart this usually means `service.metrics.enabled: true` was set while `service.metrics.port` equals `service.port` — the duplicate port collapses and the `metrics` port is never created. Either give the metrics port a distinct number (Mode A) or disable `service.metrics` and set `serviceMonitor.portName: http` (Mode B). Verify with `kubectl get svc <name> -o yaml` and `kubectl get servicemonitor <name> -o yaml` that the ServiceMonitor's `endpoints[].port` name matches an existing service port name.
- **Metrics not appearing in Grafana:** Verify serviceMonitor labels match your service labels
- **Connection refused when port-forwarding:** Check if the metrics port is correctly specified in your service

### PodMonitor Issues:
- **Metrics not appearing in Grafana:** Verify podMonitor selector matches your pod labels
- **Failed to connect to pods:** Check if pods expose the correct port name in their spec
- **Cross-namespace monitoring:** For monitoring pods across namespaces, consider adding appropriate Prometheus RBAC permissions

### Grafana-Specific Issues:
- **Can't find your metrics in Explore:** Try using the metric browser or label filters like `{namespace="your-namespace"}`
- **"No data" error in Grafana:** Check time range selection or try increasing the time range
- **Metric exists but shows no data points:** Verify that the application is actively generating metrics

### General Issues:
- **Empty metrics endpoint:** Ensure your application is properly exposing metrics on the configured endpoint
- **Scrape timeout in Prometheus logs:** Consider increasing scrapeTimeout value in your ServiceMonitor/PodMonitor
- **Label mismatches:** Compare labels in your queries with actual metric labels using Grafana's label browser

## Additional Resources

### Official Documentation
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [ServiceMonitor API](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#servicemonitor)
- [PodMonitor API](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#podmonitor)
- [Grafana Prometheus Data Source](https://grafana.com/docs/grafana/latest/datasources/prometheus/)

### Best Practices
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Kubernetes Monitoring Architecture](https://github.com/kubernetes/community/blob/master/contributors/design-proposals/instrumentation/monitoring_architecture.md)
- [Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/#xref_monitoring_golden-signals)

### Client Libraries
- [Python Client](https://github.com/prometheus/client_python)
- [.NET Client](https://github.com/prometheus-net/prometheus-net)
- [Go Client](https://github.com/prometheus/client_golang)
- [Java Client](https://github.com/prometheus/client_java)
- [Spring Boot Actuator with Prometheus](https://docs.spring.io/spring-boot/docs/current/reference/html/production-ready-features.html#production-ready-metrics-export-prometheus)
