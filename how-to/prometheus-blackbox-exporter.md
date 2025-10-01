---
title: Prometheus Blackbox Exporter Probes
nav_order: 4.5
parent: How to...
domain: public
permalink: /prometheus-blackbox-probes
last_reviewed_on: 2025-10-01
review_in: 6 months
---
# Setting up Prometheus Blackbox Exporter Probes

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Setting up Blackbox Probes](#setting-up-blackbox-probes)
  - [Creating the Required Files](#creating-the-required-files)
  - [Configuring Probes](#configuring-probes)
- [Probe Types](#probe-types)
- [Viewing Probe Results](#viewing-probe-results)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

## Introduction

Prometheus Blackbox Exporter allows you to monitor external endpoints by probing them from your Kubernetes cluster. This guide will help you set up blackbox probes for HTTP endpoints, TCP services, and more.

## Prerequisites

- Access to an ArgoCD deployment
- Permissions to create applications in your ArgoCD project
- Basic understanding of Helm charts and Kubernetes

## Setting up Blackbox Probes

### Creating the Required Files

To set up blackbox probes, you need to create two key files in your ArgoCD deployment directory:

1. `application.yaml` - Defines the Helm chart to use
2. `values.yaml` - Configures the probes

#### application.yaml

Create this file in your deployment directory:

```yaml
apiVersion: v2
name: prometheus-blackbox-probes
description: Prometheus blackbox probes
version: 0.1.0

helm:
  chart: helm/idp-blackbox-probe
  chartVersion: "0.1.13"
```

#### values.yaml

Create this file in the same directory:

```yaml
probes:
  # -- The name of the probe. Multiple probes can be defined.
  # @default -- N/A
  - name: guide-example-probes
    # -- jobName is optional, if not set it will default to the name of the probe.
    # The jobname is used to group the probes in the prometheus metrics
    jobName: "guide-example-probes"
    # -- type is optional, if not set it will default to http_2xx
    #  - http_2xx will check if the response code is in the 200-299 range
    #  - http_403_as_ok will check if the response code is 403 and treat it as a success
    #  - tcp_connect will check if it can connect to the specified port using tcp
    type: http_2xx
    # -- interval is optional and defines how long between probing in seconds, if not set it will default to 60s
    interval: 60s
    # -- urls is a list of URLs to probe
    urls:
      - 'https://example.com/app/'
      - 'https://api.example.com/health'
      - 'https://status.example.com/'
```

### Configuring Probes

You can define multiple probe configurations in the same `values.yaml` file. Each probe configuration should include:

- **name**: A unique identifier for the probe group
- **jobName** (optional): Groups metrics in Prometheus; defaults to the probe name if not specified
- **type**: The type of probe to perform (see [Probe Types](#probe-types))
- **interval** (optional): How frequently to run the probe in seconds; defaults to 60s if not specified
- **urls**: A list of endpoints to probe

Example of multiple probe configurations:

```yaml
probes:
  - name: production-websites
    jobName: "production-website-probes"
    type: http_2xx
    interval: 30s
    urls:
      - 'https://example.com'
      - 'https://blog.example.com'
      
  - name: api-endpoints
    jobName: "api-health-probes"
    type: http_2xx
    interval: 15s
    urls:
      - 'https://api.example.com/health'
      - 'https://api.example.com/status'
      
  - name: database-connectivity
    jobName: "db-connection-probes"
    type: tcp_connect
    urls:
      - 'tcp://db.example.com:5432'
```

## Probe Types

The Blackbox Exporter supports various probe types for different monitoring needs:

| Type | Description |
|------|-------------|
| `http_2xx` | Verifies that HTTP endpoints return a status code in the 200-299 range |
| `http_403_as_ok` | Same as `http_2xx`, but also accepts 403 (Forbidden) as a successful response |
| `tcp_connect` | Checks if a TCP connection can be established to the specified host and port |

For HTTP probes, simply provide the full URL. For TCP probes, use the format `tcp://host:port`.

> **Note:** Need additional probe types? If you require custom probe configurations (such as treating HTTP 404 as a success indicator or other specific validation logic), please contact the IDP team directly. The IDP team can implement and support custom probe modules tailored to your specific monitoring requirements.

## Viewing Probe Results

After setting up your probes, you can view the results in Grafana:

1. Access your cluster's Grafana instance (e.g., `https://grafana.<cluster-name>.idp.jppol.dk`)
2. Navigate to the "Blackbox Exporter (HTTP prober)" dashboard
3. Filter by job name to see your specific probe results

The dashboard provides information about:
- Probe success/failure rates
- Response times
- Status code distributions
- SSL/TLS certificate expiration (for HTTPS endpoints)

## Troubleshooting

### Common Issues

| Issue | Possible Solution |
|-------|-------------------|
| Probes failing with timeout errors | Check network connectivity between cluster and target, or increase timeout settings |
| SSL certificate validation failures | Ensure certificates are valid and trusted, or configure probe to skip verification (not recommended for production) |
| Inconsistent results | Check for load balancers or CDNs that might route requests differently |
| No data appearing in Grafana | Verify the probe configuration is correct and that Prometheus is properly scraping the exporter |

### Checking Probe Configuration

To verify your probe configuration has been applied:

1. Access your cluster's Grafana instance (e.g., `https://grafana.<cluster-name>.idp.jppol.dk`)
2. Navigate to the "Explore" section (compass icon in the left sidebar)
3. Select "Loki" as the data source
4. Enter the following query to view Blackbox Exporter logs:
   ```
   {namespace="monitoring", container="blackbox-exporter"}
   ```
5. Click "Run query" to see logs and check for any configuration errors

## Additional Resources

- [Prometheus Blackbox Exporter Documentation](https://github.com/prometheus/blackbox_exporter)
- [Prometheus Query Language (PromQL) Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
