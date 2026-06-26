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
### 2. 🧩 What values can I set in my Helm chart?

You can find the [list of configurable variables](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-advanced) (login required - it's auto-generated in our internal docs). 
Scroll to the right to see the comments for each value and its variables:

You can also [see examples of them in use](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-advanced/values.yaml) (login required) 

---

### 3. 🤫 How should we handle config and secrets?

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

Secrets should be stored in Secrets Manager.

You should set secrets via actions in your app repository and expose the values to the application as environment parameters by adding a block like this to your values.yaml file:

```yaml
external_secrets:
  - env_name: VALUE_FOR_ENVIRONMENT1
    secretsmanager_name: NAME_IN_SSM1
  - env_name: MEDIELOGIN_CLIENT_SECRET
    secretsmanager_name: medielogin_client_secret
```

The application will then have the following environment variables available: VALUE_FOR_ENVIRONMENT1 and MEDIELOGIN_CLIENT_SECRET.

Kubernetes fetches the values from Secrets Manager, so the application code does not need to perform the lookup itself.

For more details on how to implement secrets, please refer to the application's repository under each respective namespace.

For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/secrets.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/secrets.md)

---

### 4. 🔗 How do we give our IDP containers access to our managed service outside of IDP?

You can find the IP addresses in the README. For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

The IPs depend on how the service is set up.

If you need external IPs, the NAT gateway is what matters.

Note: It’s not a range, but specific addresses (i.e., a /32 "range").

---

### 5. 🌐 How do we set up custom domains?

You bind domains using the `fqdn` field in your `values.yaml` file.

However, there are limitations regarding which domains are available in each account.  
You can find them listed in the README file in the apps repository (under each namespace).

For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

The default domains are pol-dev.idp.jppol.dk and pol-test.idp.jppol.dk, but they can be extended.  
This requires some configuration on our side.

Once a domain is available, you can define subdomains under it in the `fqdn` field for each application.  
When elements are added, DNS records are created automatically, and a certificate is issued for the specific domain.

If you want records on other domains than those available in the account, that’s also possible – but significantly more complex.

If the domain is hosted in another account, you need to contact the owner of the root domain and create an A-record pointing to the load balancer addresses listed in the README.  
Once that’s in place, you can add the address in the `values.yaml` file, and certificate issuance will then work automatically.


---

### 6. 🔐 How do we restrict external access to our API endpoints?

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
