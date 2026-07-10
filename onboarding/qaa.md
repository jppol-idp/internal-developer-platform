---
title: Q&A
nav_order: 3 
parent: Onboarding
domain: public
layout: last-reviewed
last_reviewed_on: 2026-01-12
review_in: 6 months
---

# Q&A - IDP 🚀
If you or your team have any questions or run into issues, send us a [Slack message](https://jppol.slack.com/archives/C09JUREPVBP). Always ❤️.

---

### 1. 🔑 How do I get access to IDP?
- You need to be granted the correct AD group permissions.
- Requst needs to go via Servicedesk and a ServiceNow form.
- Request access from IDP support and we will request on your behalf.  

Is your team not yet set up in the IDP? Reach out to us – we’ll have a chat.

---

### 2. 🤫 How should we handle config?

We recommend placing configuration as environment variables, which can be defined in the `values.yaml` file:

```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    value: Staging
  - name: UseIDPSecrets
    value: "true"
  - name: Hangfire__Enabled
    value: "false"
  - name: SubscriptionOrderService__apiBasePath
    value: "http://subscription-order-service-koa-test-service.koa-test.svc.cluster.local:8080"
  - name: SaapiService__apiBasePath
    value: "http://saapi-koa-test-service.koa-test.svc.cluster.local:8080/"
  - name: ASPNETCORE_HTTP_PORTS
    value: "8080"
```

---

### 3. 🔗 How do we give our IDP containers access to our managed service outside of IDP?

You can find the IP addresses in the README. For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

The IPs depend on how the service is set up.

If you need external IPs, the NAT gateway is what matters.

Note: It’s not a range, but specific addresses (i.e., a /32 "range").


---

### 4. 🔐 How do we restrict external access to our API endpoints?

If the service should only be accessible internally within the _cluster_, you should disable public Nginx so it’s only available via private Nginx.

If it needs to be public but restricted, you can configure IP whitelisting in the `values.yaml` file:

```yaml
   nginx:
    public:
      enabled: true
      annotations:
        nginx.ingress.kubernetes.io/whitelist-source-range: 91.214.20.0/24,54.220.9.41/32,52.50.24.11/32
        nginx.ingress.kubernetes.io/proxy-buffer-size: "256k"
        nginx.ingress.kubernetes.io/proxy-buffers: "4 256k"
        nginx.ingress.kubernetes.io/large-client-header-buffers: "4 16k"
        nginx.ingress.kubernetes.io/proxy-busy-buffers-size: "256k"
        nginx.ingress.kubernetes.io/proxy-send-timeout: "130s"
    private:
      enabled: true
      annotations: {} 
```
The example above shows how to whitelist IPs.

It also includes a few other settings related to buffer sizes.
The key annotation for whitelisting is:
`nginx.ingress.kubernetes.io/whitelist-source-range: 91.214.20.0/24,54.220.9.41/32,52.50.24.11/32`

> 🚨 In the future, it will also be possible to grant access from other AWS accounts via a transit gateway.


---

> Please [share feedback and improvements with us in Slack](https://jppol.slack.com/archives/C09JUREPVBP). 

---
