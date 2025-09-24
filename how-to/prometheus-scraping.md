---
title: Prometheus metrics scraping
nav_order: 3 
parent: How to...
domain: public
permalink: /prometheus-metrics
last_reviewed_on: 2025-09-23
review_in: 3 months
---
# Prometheus Metrics Scraping

## Table of Contents
- [Introduction](#introduction)
- [Best Practice for Exposing Your Metrics](#best-practice-for-exposing-your-metrics)
- [Configuration Options](#configuration-options)
  - [Option 1: Using idp-advanced Helm Chart](#option-1-using-idp-advanced-helm-chart)
  - [Option 2: Using Custom Chart with ServiceMonitor](#option-2-using-custom-chart-with-servicemonitor)
  - [Option 3: Using PodMonitor](#option-3-using-podmonitor)
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
- Minimum version 1.5.0 of the idp-advanced helm chart

**Important Note:**
The idp-advanced helm chart currently only supports setting up ServiceMonitor (not PodMonitor). This is significant when running multiple replicas of an application behind a single service:

- When using ServiceMonitor, Prometheus scrapes metrics through the service, which load balances requests across all pods
- This means metrics from different pods may be intermixed across scrape intervals
- For cumulative metrics (counters) or gauges representing the system state, this is typically fine
- For metrics that need to be tracked per-instance (like individual pod resource usage or pod-specific metrics), the service abstraction may obscure which pod generated which metric

Consider these implications when designing your metrics exposure strategy with the idp-advanced chart. If you need pod-level metrics granularity, you may need to:
- Add pod identification labels to your metrics
- Bug the IDP team to get podMonitor functionality implemented in chart

**Configuration Steps:**

1. Add the following to the service section:

```yaml
service:
  ...existing content...
  metrics:
    enabled: true
```

2. Add or enable the serviceMonitor section:

```yaml
serviceMonitor:
  enabled: true
```

3. If using non-standard ports or paths, refer to:
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

### Option 3: Using PodMonitor
A PodMonitor allows Prometheus to directly target pods instead of going through a service. This is useful in scenarios where:

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

### PodMonitor Behavior (Requires custom implementation)
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

- Consider custom PodMonitor implementation when:
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