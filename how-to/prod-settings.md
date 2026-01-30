---
title: Production settings
nav_order: 2
parent: How to...
domain: public
permalink: /how-to-configure-production
last_reviewed_on: 2026-01-29
review_in: 6 months
---
# Production readiness

While you may have a smoothly running configuration in your test environment, it might still be useful 
to check the configuration for production. 

This is a short checklist with a few remarks about production ready configuration using the 
`helm-idp-advanced` helm chart. 

## Use the latest chart version!
We continuosly improve the `helm-idp-advanced` chart. Please ensure you are running the most recent version before moving 
to product. 

In all apps-repositories you will find the action `update-idp-chart-version`. This chart 
will check if there are references to an idp-maintained helm chart and make pull requests
for each unupdated chart in each namespace. It is safe to run this action as all changes are 
created as pull requests. 

## Set requests and limits
>[!NOTE]
>You should always provide a `resources` block in the values file. This also include development and test 
>namespaces as this allows you to get an idea of reasonable values and ensures cost-efficient use of resources.

A resources block defines the minimum cpu and memory allocated to each running pod. It is also 
possible - and advisible - to define a limit for resource consumption in the resources block. 

An example:
```
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1000m"
    memory: "1024Mi"
```
### CPU
This example instructs Kubernetes to allocate each pod 500 millicores - 0.5 cpu core - and 256 megabyte of memory. 

The pod _can_ use up to 1000m - 1 cpu core - if available at the host. Kubernetes will throttle cpu usage and 
prevent additional usage beyond 1000m. You can say that all pods are guaranteed to have `.resources.requests.cpu` 
cpu available. If additional cpu is available at the host, all pods on the cpu will compete for this unallocatGed
cpu resources until they reach limit. 

### Memory
Again the pod is guaranteed to be allocated the amount of memory from the requests block. (256 mb in the example.)

The pod will be allow to use additional memory available ram until it reaches the memory from the limits block. 

If a pod reaches `limit` it will be _terminated_ by kubernetes, and and OutOfMemory (OOM) error will be recorded. 

That is: Memory limits are enforced by killing the pod. CPU limits are enforced by throttling. 

If the difference between requests and limits are very large, there may arise situations where many pods on the same host 
tries to reserve memory outside their individual allocations. In this case the _host_ may run out of memory. 

The limits should be adjusted to a realistic minium and limits should be used to accomodate very short spikes. 

Use `vpa` (desribed below) to make measurements. 

Specifying carefully crafted values for requests and limits ensures a cost-effective use of the resources while 
also ensuring performance. 

## Redundancy and scaling
>[!WARNING]
>Never go to production without specifying redundancy for your pods. 

Use `.replicaCount` to set a fixed number of pods to be running. The value should be two or greater, if the deployment 
is a website or API where uptime is important. 

Use `.autoscaling` to make the deployment try to adjust the number of pods to some target value. 

>[!NOTE]
>Autoscaling works in conjunction with and relative to `.resources`.

An autoscaling example:
```
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 8
  targetCPUUtilizationPercentage: 40
```
This example instructs the pod scaling to add additional pods, when the average cpu utilization 
compared to the reserved cpu amount exceeds 40%. This target may be too low depending of the 
traffix pattern. 

If a deployment tends to fan out often, it might be preferable to increase both the target and the 
reserved cpu.

For websites a lower cpu target is often desirable, as the cpu consumption is very uneven, but all scaling 
needs to be adjusted to the specific workload. 

As an alternative to autoscaling, it is possible to use (KEDA Autoscaling)[./keda-autoscaling], which reacts to certain Kubernetes 
events.

>[!NOTE]
>`.replicaCount`, `.autoScaling` and KEDA scaling are mutually exclusive. 

## VPA
It is possible to have Kubernetes record memory and cpu consumption for the running pods. 

This helps adjusting `resources` to appropriate levels. 

Specify the block 

```
vpa:
  enabled: true
```

While a pod has been running for some time, it is possible to use the Grafana dashboard "Kubernetes / Autoscaling / Vertical Pod Autoscaler"
with filtering on namespace and "VPA Pod Autoscaler", to see some recommandations. 

The values shouldn't necessarily be entered directly into the resources block. It might be a good idea to round up the upper bound. 

Remember that VPA can also be enabled in test and development. This can give some sensible values for a base configuration, that can later be 
adjusted to fit production better. 
