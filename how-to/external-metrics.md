---
title: Collecting metrics from services outside the cluster
nav_order: 7
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-11-04
review_in: 6 months
---

# Collecting metrics from services outside the cluster

Some of the services your apps depend on run outside the cluster but still expose metrics in the Prometheus format, for example an Amazon MSK (Managed Streaming for Apache Kafka) cluster. With the `idp-external-metrics` chart, the Prometheus in your cluster collects those metrics too, so you can put them in the same Grafana dashboards and alerts as your app metrics.

The chart has a ready-made setup, a preset, for Amazon MSK. Other endpoints work as well, as long as you list which metrics to keep.

## Table of contents

- [Before you start](#before-you-start)
- [Collecting metrics from Amazon MSK](#collecting-metrics-from-amazon-msk)
- [What you get from MSK](#what-you-get-from-msk)
- [Keeping more metrics](#keeping-more-metrics)
- [Collecting metrics from other endpoints](#collecting-metrics-from-other-endpoints)
- [Checking that it works](#checking-that-it-works)
- [Troubleshooting](#troubleshooting)
- [Where to go next](#where-to-go-next)

## Before you start

The chart is deployed to your namespace, but the requests do not come from your namespace. The cluster's own Prometheus fetches the metrics directly from the endpoints, so they must be reachable from the cluster network. For services in another AWS account, that usually means a security group rule that allows traffic from the cluster's network on the metrics ports. A rule that only allows your own app's security group or IP addresses is not enough.

Only the metrics you ask for are stored. Managed services often expose tens of thousands of series per host, and storing all of them would slow down Prometheus for everyone on the cluster. The chart therefore always works from a list of metrics to keep, and stops collecting from a host that returns more than a set number of series.

## Collecting metrics from Amazon MSK

MSK can expose Prometheus metrics from every broker through [Open Monitoring](https://docs.aws.amazon.com/msk/latest/developerguide/open-monitoring.html): a JMX exporter on port 11001 with Kafka metrics, and a node exporter on port 11002 with CPU usage. Turn on both exporters for your MSK cluster, and allow the cluster to reach ports 11001 and 11002 in the MSK security group.

Then give the metrics their own folder alongside your other apps, in each environment where you want them:

```yaml
# application.yaml
apiVersion: v2
name: msk-metrics
description: Metrics from our MSK cluster
version: 0.1.0
helm:
  chart: helm/idp-external-metrics
  chartVersion: "1.0.1"  # check latest at github.com/jppol-idp/helm-idp/releases
```

```yaml
# values.yaml
# yaml-language-server: $schema=https://public.docs.idp.jppol.dk/schemas/idp-external-metrics/latest.json
targets:
  - name: my-cluster
    preset: msk
    hosts:
      - b-1.my-cluster.abc123.c1.kafka.eu-west-1.amazonaws.com
      - b-2.my-cluster.abc123.c1.kafka.eu-west-1.amazonaws.com
      - b-3.my-cluster.abc123.c1.kafka.eu-west-1.amazonaws.com
```

`name` is your own name for the cluster. It appears on every metric, so use the MSK cluster name if you can. It must be lowercase letters, digits and dashes.

`hosts` lists every broker, without a port. The broker hostnames are your bootstrap hostnames with the first part, `boot-xxx`, replaced by `b-1`, `b-2` and so on, one per broker. You can also list them with the AWS CLI:

```bash
aws kafka list-nodes --cluster-arn <your-cluster-arn> \
  --query 'NodeInfoList[].BrokerNodeInfo.Endpoints[]'
```

If you add brokers to the MSK cluster later, add them to `hosts` too.

## What you get from MSK

Every metric gets these labels:

| Label | Value |
|-------|-------|
| `namespace` | The namespace the folder is deployed to |
| `external_target` and `msk_cluster` | The `name` you gave the cluster |
| `broker` | `b-1`, `b-2` and so on |
| `job` | `msk-jmx` for Kafka metrics, `msk-node` for CPU |

The preset keeps about 55 metrics per broker, all at broker level:

| Area | Metric | Values of the `name` label |
|------|--------|----------------------------|
| Controller | `kafka_controller_KafkaController_Value` | `ActiveControllerCount`, `ActiveBrokerCount`, `FencedBrokerCount`, `OfflinePartitionsCount`, `GlobalPartitionCount`, `GlobalTopicCount`, `PreferredReplicaImbalanceCount` |
| Leader elections | `kafka_controller_ControllerStats_Count` | `LeaderElectionRateAndTimeMs`, `UncleanLeaderElectionsPerSec` |
| Replication | `kafka_server_ReplicaManager_Value` | `LeaderCount`, `PartitionCount`, `OfflineReplicaCount`, `AtMinIsrPartitionCount`, `LeaderPartitionsTotalSize`, `ReassigningPartitions` |
| Replication | `kafka_server_ReplicaManager_Count` | `IsrShrinksPerSec`, `IsrExpandsPerSec`, `FailedIsrUpdatesPerSec` |
| Throughput | `kafka_server_BrokerTopicMetrics_Count` | `BytesInPerSec`, `BytesOutPerSec`, `MessagesInPerSec`, `BytesRejectedPerSec`, `TotalProduceRequestsPerSec`, `TotalFetchRequestsPerSec`, `FailedProduceRequestsPerSec`, `FailedFetchRequestsPerSec`, `ReplicationBytesInPerSec`, `ReplicationBytesOutPerSec` |
| Request latency | `kafka_network_RequestMetrics_Mean`, `_99thPercentile`, `_Count` | `TotalTimeMs`, for the `request` values `Produce`, `FetchConsumer` and `FetchFollower` |
| Load | `kafka_server_KafkaRequestHandlerPool_OneMinuteRate`, `kafka_network_SocketServer_Value`, `kafka_network_RequestChannel_Value` | `RequestHandlerAvgIdlePercent`, `NetworkProcessorAvgIdlePercent`, `RequestQueueSize` |
| Disk | `kafka_log_LogManager_Value`, `kafka_log_LogFlushStats_Count`, `_99thPercentile`, `kafka_server_KafkaServer_Value` | `OfflineLogDirectoryCount`, `LogFlushRateAndTimeMs`, `linux-disk-read-bytes`, `linux-disk-write-bytes`, `BrokerState` |
| Consumer groups | `kafka_coordinator_group_GroupMetadataManager_Value` | `NumGroups`, `NumGroupsStable`, `NumGroupsPreparingRebalance`, `NumGroupsCompletingRebalance`, `NumGroupsEmpty`, `NumGroupsDead`, `NumOffsets` |
| Memory | `java_lang_Memory_HeapMemoryUsage_used`, `_max` | |
| CPU | `node_cpu_seconds_total` | |

`OfflinePartitionsCount` is only reported by the broker that is the active controller.

Metrics ending in `_Count` are counters that only go up. Use `rate()` to get a per-second value, for example the bytes coming into each broker:

```
rate(kafka_server_BrokerTopicMetrics_Count{name="BytesInPerSec", msk_cluster="my-cluster"}[5m])
```

Some things are not in the list, because MSK does not expose them at broker level through Open Monitoring:

- **Under-replicated partitions.** MSK only reports these per partition. `IsrShrinksPerSec`, `OfflineReplicaCount` and `AtMinIsrPartitionCount` are good broker-level signals for the same problem, or you can add the per-partition metric as shown in [Keeping more metrics](#keeping-more-metrics).
- **Disk usage.** The node exporter only reports CPU. Disk usage is available in CloudWatch as `KafkaDataLogsDiskUsed`.
- **Consumer lag.** Open Monitoring does not report it. It is available in CloudWatch.

## Keeping more metrics

Add metrics to the list with `keepMetrics`. `metric` is the full metric name, and `labels` the label values the series must have. Both are regular expressions:

```yaml
targets:
  - name: my-cluster
    preset: msk
    hosts:
      - b-1.my-cluster.abc123.c1.kafka.eu-west-1.amazonaws.com
      - b-2.my-cluster.abc123.c1.kafka.eu-west-1.amazonaws.com
      - b-3.my-cluster.abc123.c1.kafka.eu-west-1.amazonaws.com
    keepMetrics:
      - metric: kafka_cluster_Partition_Value
        labels:
          name: UnderReplicated
```

Most MSK metrics also exist per topic and per partition. The preset only keeps the broker-level series, but metrics you add with `keepMetrics` keep all of theirs. The example above gives one series per partition on each broker, which can be a few thousand. Narrow it down with a `topic` label if you only need some topics:

```yaml
    keepMetrics:
      - metric: kafka_server_BrokerTopicMetrics_Count
        labels:
          name: BytesInPerSec|MessagesInPerSec
          topic: orders|payments
```

Each broker may return at most 3,000 series after filtering. If you need more, raise it with `sampleLimit` on the target, up to 20,000. Keep it as low as you can: the series count is per broker, so it adds up across a cluster.

To see which metrics a broker exposes, open `http://<broker>:11001/metrics` from somewhere that can reach it. Expect a few megabytes of text.

## Collecting metrics from other endpoints

Leave out `preset` to collect from any other endpoint in the Prometheus format. List each host with its port, and the metrics to keep. Nothing else is kept, so `keepMetrics` is required:

```yaml
targets:
  - name: my-exporter
    hosts:
      - my-exporter.example.com:9100
    path: /metrics   # the default
    scheme: http     # or https
    keepMetrics:
      - metric: node_cpu_seconds_total
      - metric: node_filesystem_avail_bytes
        labels:
          mountpoint: /
```

Hosts must be public DNS names, ending in for example `.com` or `.dk`. IP addresses and names inside the cluster are rejected. Every metric gets the labels `namespace`, `external_target` (the `name`) and `job` (also the `name`). Endpoints that need a login or a client certificate are not supported.

You can list several targets in one folder, with or without a preset:

```yaml
targets:
  - name: my-cluster
    preset: msk
    hosts: [...]
  - name: my-exporter
    hosts: [...]
    keepMetrics: [...]
```

The names must be unique within the namespace. To tell environments or other groupings apart, add your own labels with `labels`:

```yaml
targets:
  - name: my-cluster
    preset: msk
    labels:
      environment: prod
    hosts: [...]
```

## Checking that it works

1. Open your app folder in ArgoCD and check that it is synced. Mistakes in `values.yaml`, such as a broker with a port or a missing `keepMetrics`, are shown as a sync error.
2. Open your cluster's Grafana (for example `https://grafana.<cluster-name>.idp.jppol.dk`) and go to **Explore**.
3. Select **Prometheus** as the data source and run this query, with your own target name:
   ```
   up{external_target="my-cluster"}
   ```
   There is one series per host and exporter. `1` means the last collection worked, `0` that it failed. It can take a couple of minutes after the sync before the first values appear.

## Troubleshooting

| Problem | What to check |
|---------|---------------|
| `up` is `0` for every host | Prometheus cannot reach the endpoint. For MSK, check that Open Monitoring is turned on and that the security group allows the cluster on ports 11001 and 11002 |
| `up` is `0` for some hosts | Check the hostnames in `hosts`. Brokers that have been replaced or removed must be updated |
| `up` is `0` after adding `keepMetrics` | The host returned more series than `sampleLimit`. The query `scrape_samples_post_metric_relabeling{external_target="my-cluster"}` shows how many series each host returned. Narrow the new entry, or raise `sampleLimit` |
| `up` is `1` but a metric is missing | The metric is not in the list. Check the exact metric name and `name` label against the endpoint, and add it with `keepMetrics` |
| No `up` series at all | The folder is not synced. Check ArgoCD |

If you get stuck, write to the IDP team in your team's onboarding channel on Slack.

## Where to go next

- [IDE autocomplete and validation for values.yaml](./values-yaml-ide-schema): what the `yaml-language-server` line above does, and how to set it up in your editor.
- The full set of `idp-external-metrics` options is documented in the [idp-external-metrics schema reference](https://public.docs.idp.jppol.dk/schemas/idp-external-metrics/latest.json).
