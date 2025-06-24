---
title: FAQ
nav_order: 2 
parent: Onboarding
domain: public
permalink: /faq

---

# FAQ - IDP 🚀

---



### 1. 🔑 How do I get access to IDP?
To gain access, your team lead needs to do the following:  
- Add you via your ServiceNow form so you are granted the correct AD group permissions.  
- Grant you access to your GitHub Enterprise repository under our `jppol-idp` organization.

If you or your team have any questions or run into issues, feel free to send us a [Slack message](https://ekstrabladet.slack.com/archives/C07TZPBHFUL). 

Is your team not yet set up in the IDP? Reach out to us – we’ll have a chat.

---

### 2. 🛠️ What tools do I get with the IDP?
- Github Enterprise
- ArgoCD
- Argo Workflows
- Grafana (data via Prometheus and Loki)
- PagerDuty

---
### 3. 🛠️ What values can I set in my Helm chart?

You can find the [list of configurable variables](https://github.com/jppol-idp/helm-idp-advanced/blob/main/README.md) (login required - it's auto-generated in our internal docs) 
Scroll to the right to see the comments for each value and its variables:

---
### 4. 🪣 How do I spin up an S3 bucket?
We have this repository: [https://github.com/jppol-idp/helm-idp-s3-bucket/blob/main/charts/idp-s3-bucket/values.yaml](https://github.com/jppol-idp/helm-idp-s3-bucket/blob/main/charts/idp-s3-bucket/values.yaml)

Create a folder similar with other folders in your app cluster.

In your application.yaml file you need something like:

```yaml
apiVersion: v2
name: ear-service
description: Dev test application
version: 0.1.0
slackChannel: idp-argocd-koa

helm:
  chart: helm/idp-s3-bucket
  chartVersion: "0.1.0"
```
(This is where you reference another chart.)

You can base your values on the examples in the repo.  


```yaml
# -- Default values for helm-idp-s3-bucket.
# -- This is a YAML-formatted file.
# -- Declare variables to be passed into your templates.

buckets:
    # -- (string) The name of the bucket
    # @default -- "none"
  - name: "bucket-name"
    # -- Optional: The region of the bucket. default to 'eu-west-1'
    region: "eu-west-1"
    # -- Optional: The ACL of the bucket. default to 'private'.
    # Valid values: private, public-read, public-read-write, aws-exec-read, authenticated-read, bucket-owner-read, bucket-owner-full-control, log-delivery-write
    acl: "private"
    # -- Optional: The tags of the bucket. default tag 'crossplane: "true"' will always be set.
    tags:
      - key: "Name"
        value: "bucket-name"
#  - name: "jppol-idp-tjallo-tjalde"
```

The most important thing is to change the `bucket-name`.

You can define multiple buckets in the file if needed.

You must grant access via IRSA in the application's `values.yaml` file for each application.


---

### 5. 🤫 How should we handle config and secrets

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

You can find more details in the apps repository under each namespace. 

For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/secrets.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/secrets.md)

---

### 6. 🖇️ How do we give our IDP containers access to our managed service outside of IDP?

You can find the IP addresses in the README. Example:  
For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

The IPs depend on how the service is set up.

If you need external IPs, the NAT gateway is what matters.

Note: It’s not a range, but specific addresses (i.e., a /32 "range").

---

### 7. 🧁 How do we set up custom domains?

You bind domains using the `fqdn` field in your `values.yaml` file.

However, there are limitations regarding which domains are available in each account.  
You can find them listed in the README file in the apps repository (under each namespace).

For `pol-dev`, the list is here:  
[https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

Available domains
pol-test.idp.jppol.dk
pol-dev.idp.jppol.dk

These are the default domains, but they can be extended.  
This requires some configuration on our side.

Once a domain is available, you can choose subdomains under the listed domains in the `fqdn` field for each application.  
When elements are added, DNS records are created automatically, and a certificate is issued for the specific domain.

If you want records on other domains than those available in the account, that’s also possible – but significantly more complex.

If the domain is hosted in another account, you need to contact the owner of the root domain and create an A-record pointing to the load balancer addresses listed in the README.  
Once that’s in place, you can add the address in the `values.yaml` file, and certificate issuance will then work automatically.


---

### 8. 🔐 How do we restrict external access to our API endpoints?

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

You can also set nginx.public.enabled to false if you don’t want the service to be publicly exposed at all.

> 🚨 In the future, it will also be possible to grant access from other AWS accounts via a transit gateway.

---

*Sidst opdateret: 17-juni-2025*
