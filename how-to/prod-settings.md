---
title: Production settings
nav_order: 25
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-11-26
review_in: 6 months
---
# Production settings

While you may have a smoothly running configuration in your test environment, it might still be useful 
to check the configuration for production. 

This is a short checklist with a few remarks about production ready configuration using the 
`idp-advanced` Helm chart. 

## Use the latest chart version!
We continuously improve the `idp-advanced` chart. Please ensure you are running the most recent version before moving 
to production. 

In all apps-repositories you will find the action `update-idp-chart-version`. This action 
will check if there are references to an idp-maintained helm chart and make pull requests
for each outdated chart in each namespace. It is safe to run this action as all changes are 
created as pull requests. 

## Set requests and limits
> *You should always provide a `resources` block in the values file. This also includes development and test*
> *namespaces as this allows you to get an idea of reasonable values and ensures cost-efficient use of resources.*

A resources block defines the minimum cpu and memory allocated to each running pod. You should also 
define a memory limit in the resources block. We recommend not setting a cpu limit, see [CPU](#cpu) below. 

If you leave out the block, the chart default applies: a request of 100m cpu and 128Mi memory, and a memory limit of 128Mi. 

An example:
```
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    memory: "1024Mi"
```
### CPU
This example instructs Kubernetes to allocate each pod 500 millicores - 0.5 cpu core - and 256Mi of memory. 

All pods are guaranteed to have `.resources.requests.cpu` cpu available. Without a cpu limit, the pod _can_ use 
additional cpu when it is available on the host. All pods on the host share the unallocated cpu in proportion to their requests. 

A cpu limit makes Kubernetes throttle the container when it reaches the limit, even when the host has idle cpu. 
This typically shows up as slow responses during startup and traffic spikes, so we recommend setting only the request. 

### Memory
Again the pod is guaranteed to be allocated the amount of memory from the requests block. (256Mi in the example.)

The pod is allowed to use additional memory, if available on the host, until it reaches the memory from the limits block. 

If a container reaches its memory limit, it is _killed_ by Kubernetes and restarted. The container status shows `OOMKilled`. 

That is: Memory limits are enforced by killing the container. 

If the difference between requests and limits is very large, there may arise situations where many pods on the same host 
try to reserve memory outside their individual allocations. In this case the _host_ may run out of memory. 

The requests should be adjusted to a realistic minimum and limits should be used to accommodate very short spikes. 

Use `vpa` ([described below](#vpa---to-see-recommendations)) to make measurements. 

Specifying carefully crafted values for requests and limits ensures a cost-effective use of the resources while 
also ensuring performance. 

## Set redundancy and scaling
> *Never go to production without specifying redundancy for your pods.*
> You can use _either_ `.replicaCount` for a fixed size deployment _or_ `.autoscaling` to 
> scale on cpu or memory utilization. 
> *When `.autoscaling` is enabled, `.replicaCount` is ignored, so you do not need to set it. `.autoscaling.minReplicas` sets the lower bound instead.*

While static sizes are simpler, they don't provide any adaptation to change in load or other fluctuations 
in resource requirements. 

Static sizes or autoscaling will likely fit most users.

### Using replicaCount - for a static size
Use `.replicaCount` to set a fixed number of pods to be running. The value should be two or greater, if the deployment 
is a website or API where uptime is important. 

A replicaCount example:
```
replicaCount: 2
```

With two or more replicas, or with autoscaling enabled, the chart also creates a PodDisruptionBudget. It makes sure only one pod is 
taken down at a time when nodes are drained or replaced. With a single replica no PodDisruptionBudget is created, and the pod 
is stopped before a replacement is ready, so your app is unavailable for a while. 


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
[KEDA](./keda-autoscaling) (Kubernetes Event-Driven Autoscaling) can scale on custom metrics and events, such as queue lengths. 
KEDA is not supported by the `idp-advanced` chart. It requires your own Helm chart where you define the `ScaledObject` yourself.

### Spread pods across nodes
The chart sets no topology spread constraints by default. Kubernetes spreads pods a little on its own, but two replicas can 
still end up on the same node, and a single node failure then takes down both. 

Add `topologySpreadConstraints` to make the scheduler place the pods on different nodes:
```
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app.kubernetes.io/name: my-app
```

Replace `my-app` with the name of your Deployment, which you can see in Argo CD or with `kubectl get deployments`. 
`ScheduleAnyway` lets a pod start on a node that already runs a replica if there is no other option. With `DoNotSchedule` the 
pod waits until it can be placed on another node. 

## Set health checks
The chart adds a `livenessProbe` and a `readinessProbe` by default. Both send `GET /` to the `http` port. 
This rarely fits a production app: if `/` returns an error such as `404`, the pod never becomes ready, and if `/` always returns 
`200`, the pod receives traffic even when the app cannot serve it. 

Point the probes at a health endpoint in your app:
```
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: http
  periodSeconds: 10
```

The `readinessProbe` decides whether the pod receives traffic. It may check that the app can reach the services it depends on. 
The `livenessProbe` decides whether the container is restarted. Keep it to a check that the process itself responds, 
so a database outage does not restart all your pods. 

Use a `startupProbe` if your app takes a long time to start. Liveness and readiness checks wait until the startup probe succeeds. 

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

Once a pod has been running for some time, it is possible to use the Grafana dashboard "Kubernetes / Autoscaling / Vertical Pod Autoscaler"
with filtering on namespace and "VPA Pod Autoscaler", to see some recommendations. 

The values shouldn't necessarily be entered directly into the resources block. It might be a good idea to round up the upper bound. 

Remember that VPA can also be enabled in test and development. This can give some sensible values for a base configuration, that can later be 
adjusted to fit production better. 
