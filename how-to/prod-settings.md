---
title: Production settings
nav_order: 25
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-01-29
review_in: 6 months
---
# Production readiness

While you may have a smoothly running configuration in your test environment, it might still be useful 
to check the configuration for production. 

This is a short checklist with a few remarks about production ready configuration using the 
`helm-idp-advanced` helm chart. 

## Use the latest chart version!
We continuously improve the `helm-idp-advanced` chart. Please ensure you are running the most recent version before moving 
to production. 

In all apps-repositories you will find the action `update-idp-chart-version`. This action 
will check if there are references to an idp-maintained helm chart and make pull requests
for each unupdated chart in each namespace. It is safe to run this action as all changes are 
created as pull requests. 

## Set requests and limits
> *You should always provide a `resources` block in the values file. This also include development and test*
> *namespaces as this allows you to get an idea of reasonable values and ensures cost-efficient use of resources.*

A resources block defines the minimum cpu and memory allocated to each running pod. It is also 
possible - and advisable - to define a limit for resource consumption in the resources block. 

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
cpu available. If additional cpu is available at the host, all pods on the cpu will compete for these unallocated
cpu resources until they reach limit. 

### Memory
Again the pod is guaranteed to be allocated the amount of memory from the requests block. (256 mb in the example.)

The pod will be allow to use additional memory available ram until it reaches the memory from the limits block. 

If a pod reaches `limit` it will be _terminated_ by kubernetes, and OutOfMemory (OOM) error will be recorded. 

That is: Memory limits are enforced by killing the pod. CPU limits are enforced by throttling. 

If the difference between requests and limits is very large, there may arise situations where many pods on the same host 
try to reserve memory outside their individual allocations. In this case the _host_ may run out of memory. 

The limits should be adjusted to a realistic minimum and limits should be used to accommodate very short spikes. 

Use `vpa` ([described below](#vpa---to-see-recommendations)) to make measurements. 

Specifying carefully crafted values for requests and limits ensures a cost-effective use of the resources while 
also ensuring performance. 

## Set redundancy and scaling
> *Never go to production without specifying redundancy for your pods.*
> You can use _either_ replicaCount for a fixed size deployment,  autoscaling to 
> scale on various targets _or_ KEDA scaling to scale on Kubernetes events. 
> *`.replicaCount`, `.autoScaling` and KEDA scaling are mutually exclusive.*

While static sizes are simpler, they don't provide any adaptation to change in load or other fluctuations 
in resource requirements. KEDA requires in-depth knowledge of Kubernetes and is very configurable. 

Static sizes or autoscaling will likely fit most users.

### Using replicaCount - for a static size
Use `.replicaCount` to set a fixed number of pods to be running. The value should be two or greater, if the deployment 
is a website or API where uptime is important. 

A replicaCount example:
```
replicaCount: 2
```


### Using autoscaling - scaling by resource utilization
Use `.autoscaling` to make the deployment try to adjust the number of pods to some target value. 

{: .note }
> Autoscaling works in conjunction with and relative to `.resources`.

An autoscaling example:
```
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 8
  targetCPUUtilizationPercentage: 40
```
This example instructs the pod scaling to add additional pods, when the average cpu utilization 
compared to the reserved cpu amount exceeds 40%. This target may be too low depending on the 
traffic pattern. 

If a deployment tends to fan out often, it might be preferable to increase both the target and the 
reserved cpu.

For websites a lower cpu target is often desirable, as the cpu consumption is very uneven, but all scaling 
needs to be adjusted to the specific workload. 

### Using KEDA - scaling by system events
As an alternative to autoscaling, it is possible to use [KEDA](./keda-autoscaling) (Kubernetes Event-Driven Autoscaling), which reacts to certain Kubernetes 
events.

## Shut down gracefully
> *If callers see `502` responses during deployments or scale-downs, your pods are stopping before traffic stops reaching them.*

When Kubernetes stops a pod, it sends `SIGTERM` to the container and removes the pod from the service endpoints at the same time.
It takes a few seconds before the ingress and other services calling your app notice the removal. Requests sent in that window hit a container that is already shutting down.

Add a `preStop` hook that waits before the container receives `SIGTERM`, so routing is updated while the pod still serves requests:

```
lifecycle:
  preStop:
    sleep:
      seconds: 10
terminationGracePeriodSeconds: 40
```

Both keys go at the top level of your `values.yaml`, next to `image` and `resources`.

Use the built-in `sleep` action rather than `exec` with a `sleep` command. It does not need a `sleep` binary in the image, which distroless and scratch images do not have.

`terminationGracePeriodSeconds` covers both the `preStop` hook and your app's own shutdown. With the values above, the app has 30 seconds to finish in-flight requests after the sleep before it is killed. The Kubernetes default is 30 seconds, which is enough if your app shuts down quickly.

Your app should still handle `SIGTERM` by finishing in-flight requests before it exits.

See [Pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination) in the Kubernetes documentation for details.

## VPA - to see recommendations
VPA (Vertical Pod Autoscaler) makes it possible to have Kubernetes record memory and cpu consumption for the running pods. 

This helps adjusting `resources` to appropriate levels. 

Specify the block 

```
vpa:
  enabled: true
```

While a pod has been running for some time, it is possible to use the Grafana dashboard "Kubernetes / Autoscaling / Vertical Pod Autoscaler"
with filtering on namespace and "VPA Pod Autoscaler", to see some recommendations. 

The values shouldn't necessarily be entered directly into the resources block. It might be a good idea to round up the upper bound. 

Remember that VPA can also be enabled in test and development. This can give some sensible values for a base configuration, that can later be 
adjusted to fit production better. 
