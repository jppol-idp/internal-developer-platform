---
title: KEDA Autoscaling
nav_order: 6
parent: How to...
domain: public
permalink: /keda-autoscaling
last_reviewed_on: 2026-01-07
review_in: 6 months
---

# KEDA Autoscaling

## Background

KEDA (Kubernetes Event Driven Autoscaler) enables pod-level autoscaling based on custom metrics, complementing our existing Karpenter node-level scaling.

Standard Kubernetes HPA (Horizontal Pod Autoscaler) only supports CPU and memory metrics. KEDA extends this with:

- **Custom Prometheus metrics**: Scale based on any metric in your monitoring stack
- **Scale-to-zero**: Reduce costs by scaling idle workloads to zero replicas
- **Event-driven scaling**: React to queue lengths, request rates, or custom application metrics

This is particularly useful for:
- GPU workloads that should scale based on inference queue length
- Batch processing jobs that scale with pending work
- Cost optimization by scaling down unused resources

## Important Limitations

{: .warning }
> **KEDA is currently NOT supported by `helm-idp-advanced`**. You can only use KEDA with your own managed Helm charts where you define the ScaledObject resources yourself.

## How It Works

1. **Define a ScaledObject** that references your Deployment and specifies scaling triggers
2. **KEDA queries your metrics source** (e.g., Prometheus) at regular intervals
3. **KEDA creates and manages an HPA** based on the ScaledObject configuration
4. **Pods scale up/down** based on the metric values and thresholds you define

## Basic Example

Here's a simple ScaledObject that scales a deployment based on a Prometheus metric:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: my-app-scaler
  namespace: my-namespace
spec:
  scaleTargetRef:
    name: my-deployment          # Name of the Deployment to scale
  minReplicaCount: 0             # Enable scale-to-zero
  maxReplicaCount: 10
  cooldownPeriod: 60             # Seconds to wait before scaling down
  pollingInterval: 15            # How often to check metrics
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://kube-prometheus-stack-prometheus.monitoring:9090
      query: sum(my_app_queue_length{namespace="my-namespace"})
      threshold: "5"             # Scale up when metric >= threshold
```

## Prometheus Configuration

{: .note }
> KEDA does not auto-discover Prometheus. You must specify the server address in each ScaledObject.

Use this Prometheus URL in your ScaledObjects:
```
http://kube-prometheus-stack-prometheus.monitoring:9090
```

## Scaling Behavior

The number of replicas is calculated as:

```
replicas = ceil(metric_value / threshold)
```

For example, with `threshold: "5"`:
- Metric value 0 → 0 replicas (if minReplicaCount is 0)
- Metric value 4 → 1 replica
- Metric value 12 → 3 replicas
- Metric value 50 → 10 replicas (capped at maxReplicaCount)

## GPU Workload Example

For AI/ML workloads with GPU, you might scale based on inference queue length:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: inference-scaler
  namespace: ai-prod
spec:
  scaleTargetRef:
    name: inference-server
  minReplicaCount: 0
  maxReplicaCount: 5
  cooldownPeriod: 300            # 5 min cooldown for expensive GPU pods
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://kube-prometheus-stack-prometheus.monitoring:9090
      query: sum(inference_queue_pending_requests{namespace="ai-prod"})
      threshold: "10"
```

## Available Triggers

KEDA supports many trigger types beyond Prometheus:

| Trigger | Use Case |
|---------|----------|
| prometheus | Scale on any Prometheus metric |
| aws-sqs-queue | Scale based on SQS queue length |
| kafka | Scale based on Kafka consumer lag |
| cron | Scheduled scaling |
| cpu/memory | Standard resource metrics |

See [KEDA Scalers Documentation](https://keda.sh/docs/latest/scalers/) for the full list.

## Troubleshooting

### Check ScaledObject status in ArgoCD

Open your application in ArgoCD and look for the ScaledObject resource. A healthy ScaledObject shows a green status.

You can also check the HPA that KEDA creates automatically - it will be named `keda-hpa-<scaledobject-name>`.

### Check KEDA logs in Grafana

In Grafana, go to the Explore view and query Loki for KEDA operator logs:

```
{namespace="keda", app="keda-operator"}
```

Look for scaling events like:
```json
{"level":"info","logger":"scaleexecutor","msg":"Successfully set ScaleTarget replicas count","New Replicas Count":3}
```

### Common issues

**ScaledObject shows error status in ArgoCD**
- Verify Prometheus URL is correct
- Check that your PromQL query is valid in Grafana
- Ensure the metric exists in Prometheus

**Pods not scaling to zero**
- Verify `minReplicaCount: 0` is set
- Check `cooldownPeriod` hasn't been reached yet
- Ensure metric value is actually 0

**HPA conflict**
- Don't create both a ScaledObject and manual HPA for the same Deployment
- KEDA manages the HPA automatically

## Additional Information

- [KEDA Documentation](https://keda.sh/docs/latest/)
- [KEDA Prometheus Scaler](https://keda.sh/docs/latest/scalers/prometheus/)
- [JIRA: IDP-767](https://jira-jppol.atlassian.net/browse/IDP-767)

For questions or issues, contact the platform team via:
- **Slack**: Your onboarding channel or #idp-team
