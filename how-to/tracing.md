---
title: Distributed tracing
nav_order: 12
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-11-02
review_in: 6 months
---

# Distributed tracing

A trace follows one request through every service it touches: which services were called, in which order, how long each step took and where it failed. Logs tell you what one service did; a trace shows you the whole path.

The platform gives every cluster an endpoint for OpenTelemetry traces. Your application sends spans to it, the platform stores them centrally, and you query them in your cluster's Grafana next to your logs. You instrument your application; you do not run any tracing backend yourself.

This guide covers how to send traces, how to keep a trace connected across services, how to link traces and logs, and what limits and costs to keep in mind.

## Table of contents

**[How it works](#how-it-works)**

**[Sending traces from your application](#sending-traces-from-your-application)**
- [Configure the exporter](#configure-the-exporter)
- [Instrument your application](#instrument-your-application)

**[Keeping a trace connected](#keeping-a-trace-connected)**

**[Linking traces and logs](#linking-traces-and-logs)**

**[Viewing traces in Grafana](#viewing-traces-in-grafana)**

**[What belongs in a trace and what stays in your logs](#what-belongs-in-a-trace-and-what-stays-in-your-logs)**

**[Limits, cost and sampling](#limits-cost-and-sampling)**

**[Questions we get asked](#questions-we-get-asked)**

[Getting help](#getting-help)

# How it works

1. Your application sends spans with **OTLP** (the OpenTelemetry protocol) to an endpoint inside your cluster.
2. The platform adds Kubernetes information to every span: `k8s.namespace.name`, `k8s.pod.name` and the name of your deployment. You do not have to set these yourself.
3. The spans are forwarded to a **central trace store** (Grafana Tempo), one for test clusters and one for production clusters, and stored in S3.
4. Your cluster's Grafana reads back only your own cluster's traces.

Traces are **best effort**. If the platform is overloaded, the trace store is down, or your cluster is over its limit, spans are dropped rather than queued. Your application is not slowed down or affected when that happens, but the trace will have gaps. This is a deliberate trade-off and it decides what you should put in a trace and what must stay in a log line; see [What belongs in a trace and what stays in your logs](#what-belongs-in-a-trace-and-what-stays-in-your-logs).

Traces are kept for **7 days on test clusters** and **14 days on production clusters**.

# Sending traces from your application

## Configure the exporter

### With idp-advanced

If your app is deployed with the idp-advanced chart (version 3.14.0 or later), turn tracing on in your `values.yaml`:

```yaml
tracing:
  enabled: true
```

That sets the environment variables the OpenTelemetry SDK needs: where to send spans, compression, your service name and version, and that only traces are sent. The examples in this guide use a namespace called `my-namespace` with an app called `checkout`; with the setting above its spans show up in Grafana as service `checkout`.

| Setting | Default | |
|---|---|---|
| `tracing.serviceName` | Your app's name (the release name without the namespace), `checkout` in the example | The name your service shows up under in Grafana |
| `tracing.sampleRate` | `1` (every request) | Share of requests to record, see [Sampling](#sampling) |

If you set any of the `OTEL_*` variables yourself in `env`, your value is used instead of the chart's.

### Without idp-advanced

All OpenTelemetry SDKs read the same standard environment variables, so the configuration is the same whatever language you use. Set these on your container:

```yaml
env:
  # Where to send spans. The SDK adds /v1/traces itself.
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: http://alloy-aggregator.monitoring.svc.cluster.local:4318
  - name: OTEL_EXPORTER_OTLP_PROTOCOL
    value: http/protobuf
  # Compress spans before sending. Not the SDK default, see "Limits, cost and sampling".
  - name: OTEL_EXPORTER_OTLP_COMPRESSION
    value: gzip
  # The name your service shows up under in Grafana.
  - name: OTEL_SERVICE_NAME
    value: checkout
  # The endpoint only accepts traces. Turn off OTLP metrics and logs,
  # otherwise the SDK tries to send them to the same endpoint and logs errors.
  - name: OTEL_METRICS_EXPORTER
    value: none
  - name: OTEL_LOGS_EXPORTER
    value: none
```

| Setting | Value |
|---|---|
| OTLP over HTTP | `http://alloy-aggregator.monitoring.svc.cluster.local:4318` |
| OTLP over gRPC | `http://alloy-aggregator.monitoring.svc.cluster.local:4317` (set `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`) |
| Authentication | None. The endpoint is only reachable from inside the cluster. |

Set `OTEL_EXPORTER_OTLP_PROTOCOL` explicitly. The SDKs do not agree on a default: some use HTTP, others gRPC, and a mismatch between protocol and port fails silently.

### Either way

Your logs keep going to stdout as before; see [Application logging](/how-to/application-logs.html). Only traces go to this endpoint.

## Instrument your application

The quickest start is OpenTelemetry's automatic instrumentation for your language. It creates spans for incoming HTTP requests, outgoing HTTP calls, database calls and common messaging clients without code changes, and it reads the environment variables above.

| Stack | Where to start |
|---|---|
| Java | The OpenTelemetry Java agent (`-javaagent:opentelemetry-javaagent.jar`) |
| .NET | OpenTelemetry .NET automatic instrumentation, or the `OpenTelemetry.Extensions.Hosting` packages with the ASP.NET Core and HttpClient instrumentations |
| Node.js | `@opentelemetry/auto-instrumentations-node` |
| Python | `opentelemetry-distro` and `opentelemetry-instrument` |
| Go | The OpenTelemetry Go SDK with the `otelhttp` and `otelgrpc` instrumentations (Go has no agent; you add a few lines of code) |

The language guides on [opentelemetry.io](https://opentelemetry.io/docs/languages/) show the setup for each.

Once automatic instrumentation works, add your own spans around the work that matters to your service, for example "calculate price" or "render page", and give them attributes that help you find a trace later, such as an order ID.

A pod that sends spans within its first second or two may get them without the Kubernetes attributes, because the platform has not seen the pod yet. Long-running services are not affected. For short-lived jobs, avoid sending spans before the job has started its real work.

# Keeping a trace connected

A trace is only useful if every service adds its spans to the same trace. That happens through a **trace context**: the trace ID and the ID of the calling span, carried along with every call. OpenTelemetry uses the W3C `traceparent` header for this.

**HTTP and gRPC.** Automatic instrumentation reads `traceparent` on incoming requests and adds it to outgoing calls. If you use an HTTP client the instrumentation does not know, add the header yourself through the SDK's propagator API. A trace breaks at the first service in the chain that is not instrumented.

**Queues and event streams.** The context has to travel inside the message, normally as a message header. The OpenTelemetry instrumentations for Kafka and most other messaging clients do this on both producer and consumer side. If you write your own producer or consumer, inject the context into the message headers when you send, and extract it when you receive.

**Background jobs and scheduled jobs.** A job that is not triggered by a request starts its own trace. If a request hands work off to a background worker, store the trace context with the work item and continue the trace from it in the worker.

**Calls from outside the cluster.** The ingress passes an incoming trace context on to your service, so a trace started by a caller outside the cluster continues in your service.

# Linking traces and logs

Grafana can jump from a span to the log lines written during it, and from a log line to its trace. Both directions only work if your log lines carry the trace ID.

Write the trace ID as a field in every log line. In JSON:

```json
{"level":"info","msg":"order created","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","span_id":"00f067aa0ba902b7"}
```

Grafana recognises `trace_id`, `traceId`, `traceID` and `TraceId` followed by `:` or `=` and the 32-character hexadecimal trace ID, in JSON, logfmt or plain text.

| Stack | How to get the trace ID into your logs |
|---|---|
| Java | The Java agent adds `trace_id` and `span_id` to the logging context (MDC) for Logback and Log4j. Include them in your JSON layout. |
| .NET | Add `Activity.Current?.TraceId` to your log scope or as a Serilog/NLog enricher, written as `trace_id` or `TraceId`. |
| Node.js | The Pino and Winston instrumentations add `trace_id` and `span_id` to every log record. |
| Python | `opentelemetry-instrumentation-logging` adds `otelTraceID` to each log record; include it in your formatter. |
| Go | Read `trace.SpanContextFromContext(ctx).TraceID().String()` and add it as a field in your logger. |

To check it works: find a log line from a request in Grafana Explore (Loki). It should show a **View trace** link next to the trace ID.

# Viewing traces in Grafana

1. Open your cluster's Grafana and go to **Explore**
2. Pick the **Tempo** datasource
3. Use **Search** to filter by service name, span name, status or duration, or paste a trace ID

For precise searches, switch to **TraceQL**. Some examples:

All failed requests in your namespace:

```
{ resource.k8s.namespace.name = "my-namespace" && status = error }
```

Slow requests to one service:

```
{ resource.service.name = "checkout" && kind = server && duration > 2s }
```

A trace by one of your own attributes:

```
{ span.order.id = "4711" }
```

In a trace, open a span and pick **Related logs** to see the log lines from the same pod with that trace ID, five minutes either side of the span. From a log line in Loki, the **View trace** link goes the other way.

Searches without a time range only cover the last few minutes. Set the time range in the top right when you look for older traces.

# What belongs in a trace and what stays in your logs

Because traces are best effort, anything you must be able to find later stays a log line, with the trace ID in it:

- errors and exceptions
- business events, such as an order placed or a payment captured
- state changes
- security-relevant actions, such as logins and permission changes

Traces are good at replacing the log lines you only write to follow a request's path: "received request", "calling inventory", "got response after 120 ms". Those lines cost log storage on every request and are hard to read across services. A span says the same thing with timing and context.

**Rule of thumb:** if losing it would matter, log it. If it only helps you see the path, trace it.

# Limits, cost and sampling

## Limits

| Limit | Value | What happens above it |
|---|---|---|
| Span data per cluster | About 5 MB per second, shared by every namespace in the cluster | Spans are dropped in the platform. Your application is not affected. |
| Size of one attribute value | 2048 bytes | The value is cut off at 2048 bytes. |
| Size of one trace | 5 MB | Further spans for that trace are dropped. |

The per-cluster limit is shared. One service sending far more than it needs can push the whole cluster over it and cause gaps in other teams' traces too.

Bytes per span come mostly from attributes, so a few large attributes cost more than many small spans. **Do not put request or response bodies, payloads or large documents in span attributes.**

## Cost

Span traffic from your application to the platform endpoint counts as network traffic in your cluster's AWS account, and the OpenTelemetry SDKs send it uncompressed by default. Compressing with gzip cuts that traffic to roughly a fifth. `tracing.enabled` in idp-advanced does this for you; without idp-advanced, always set `OTEL_EXPORTER_OTLP_COMPRESSION=gzip`.

## Sampling

Sampling means recording only a share of requests. It is the main lever for high-traffic services: a service with 30 spans per request sampled at 10 % costs about a tenth of the same service at 100 %.

With idp-advanced:

```yaml
tracing:
  enabled: true
  sampleRate: 0.1   # record 10 % of requests
```

Without idp-advanced:

```yaml
env:
  - name: OTEL_TRACES_SAMPLER
    value: parentbased_traceidratio
  - name: OTEL_TRACES_SAMPLER_ARG
    value: "0.1"   # record 10 % of requests
```

Both use `parentbased_traceidratio`, which makes the decision once, in the service where the trace starts, and every service further down follows it. That keeps sampled traces complete instead of missing random services.

A reasonable start:

- Test clusters: 100 % (the SDK default, no sampler settings needed).
- Production, low or moderate traffic: 100 %.
- Production, a service handling many requests per second or creating many spans per request: start at 10 % and adjust.

Sampling is decided when a request starts, before anyone knows whether it will fail. At 10 %, nine out of ten failing requests have no trace. Your error log lines are still there, which is one more reason errors stay in your logs.

## Sensitive data

Treat span attributes like log lines. Do not put passwords, tokens, API keys or personal data in span names or attributes. Automatic instrumentation records URLs and SQL statements; check what your instrumentation captures before you turn it on in production, and use its settings to leave out query strings or parameters that may hold personal data.

# Questions we get asked

**Do I have to use OpenTelemetry?** Yes, the endpoint accepts OTLP only. Older formats such as Zipkin or Jaeger clients are not supported; the OpenTelemetry SDKs replace them.

**Can I send metrics or logs through the same endpoint?** No. The endpoint accepts traces only. Logs are collected from stdout automatically, and metrics are scraped with Prometheus; see [Prometheus scraping](/how-to/prometheus-scraping.html).

**Can I see traces from another team's cluster?** No. Like logs, traces are isolated per cluster. A trace that crosses into another cluster shows up in two parts, one in each cluster's Grafana.

**My service shows up as `unknown_service`.** `OTEL_SERVICE_NAME` is not set, or not set in the container that sends the spans. With idp-advanced, check that `tracing.enabled` is `true`.

**I see my spans, but each service is its own trace.** The trace context is lost between the services. See [Keeping a trace connected](#keeping-a-trace-connected).

**I see no traces at all.** Check that your image actually contains the OpenTelemetry SDK or agent: `tracing.enabled` only configures it. Without idp-advanced, check that `OTEL_EXPORTER_OTLP_PROTOCOL` matches the port (4318 for `http/protobuf`, 4317 for `grpc`), and look for exporter errors in your application's log at startup. Then search in Grafana with a time range of the last hour, not the default.

# Getting help

Write to the IDP team in your team's onboarding channel on Slack.
