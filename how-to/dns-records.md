---
title: DNS records and custom domains
nav_order: 9
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-10-05
review_in: 6 months
---
# DNS records and custom domains
{: .no_toc }

---

## Table of contents
{: .no_toc }

- TOC
{:toc}

---

## Which DNS domains (zones) can I use?
Each cluster is connected to an AWS account which has got one or more associated 
dns zones or domains. 

Each namespace you control via your team's apps-repository can modify DNS 
records within any zone in that cluster's account. 

Each account only allows binding to a limited set of domains. The available
domains for your namespace are listed in the README file in the apps
repository, under your namespace. For `pol-dev`, see:
[apps-pol/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

The list can be extended for your account. This requires some configuration
on our side, so write to the IDP team in your team's onboarding channel on Slack
if you need an additional domain enabled.

Domains for an account may change. Please act responsibly while working with DNS: 
there may be zones logically belonging to other teams also hosted in the 
same cluster. Please don't experiment with such zones. 

## How to control DNS
The most straightforward way to work with DNS is to use the idp-advanced chart,
where you list the fully qualified domain names (FQDNs) you want for each
service in the `ingress.fqdn` field of your `values.yaml`. When you use this field,
DNS records are created automatically and a certificate is issued for the
domain. DNS and certificate issuance are both handled for you.

Once a domain is available for your account, you can add subdomains under it
in the `ingress.fqdn` field of each application's `values.yaml`.

### Using a domain hosted in another account or by another team
It's also possible to point a domain that isn't on your account's list to
your service, but it's more involved:

1. Contact the owner of the root domain and ask them to create an A record
   pointing to the load balancer addresses listed in your namespace's README.
2. Once that record is in place, add the address in the `ingress.fqdn` field of your
   `values.yaml` and set `ingress.public.httpCertChallenge: true`. Certificate
   issuance will then happen automatically.

### Private hostnames
If you enable the private ingress (`ingress.private.enabled: true`), each name in
`ingress.fqdn` also gets a private hostname with `internal-` in front of it, which
resolves to private IP addresses. To use other hostnames on the private ingress,
list them in `ingress.private.fqdn`. They are then used as they are, without the prefix.

**Example: private hostname with the default prefix**

```yaml
ingress:
  enabled: true
  fqdn:
    - foo.bar.idp.jppol.dk
  private:
    enabled: true
```

| Ingress | Hostname |
|---------|----------|
| Public | `foo.bar.idp.jppol.dk` |
| Private | `internal-foo.bar.idp.jppol.dk` |

**Example: your own private hostname**

```yaml
ingress:
  enabled: true
  fqdn:
    - foo.bar.idp.jppol.dk
  private:
    enabled: true
    fqdn:
      - foo-private.bar.idp.jppol.dk
```

| Ingress | Hostname |
|---------|----------|
| Public | `foo.bar.idp.jppol.dk` |
| Private | `foo-private.bar.idp.jppol.dk` |

**Example: private only, without the prefix**

If the service should only be reachable privately, without the `internal-` prefix, turn
off the public ingress and put the name in `ingress.private.fqdn`:

```yaml
ingress:
  enabled: true
  public:
    enabled: false
  private:
    enabled: true
    fqdn:
      - foo.bar.idp.jppol.dk
```

| Ingress | Hostname |
|---------|----------|
| Public | none |
| Private | `foo.bar.idp.jppol.dk` |

## DNS records not belonging to a specific deployment
It is possible to set arbitrary records in a given dns zone without 
the records being related to web services or other deployments inside the cluster. 

Here you can use the chart [`crossplane-route53-records`](https://github.com/jppol-idp/helm-idp/tree/main/charts/crossplane-route53-records). 

This chart becomes relevant when you
- Want to create validation records of type `TXT`
- Want to prepare a migration by creating CNAMEs to deployments hosted outside IDP. 
- Want to setup MX records

### Where to put your records
Each namespace has a `zones` folder (`apps/<namespace>/zones/`) that the IDP platform creates
and keeps up to date. It makes the zones in the account available to records in the namespace.
Don't edit it, and don't put your own records there.

Put your records in a folder of their own in your namespace, for example
`apps/<namespace>/dns-records/`. You can use one folder for all your records or one folder
per "purpose".

Add an `application.yaml` to the folder that references the chart `helm/crossplane-route53-records`:

```yaml
apiVersion: v2
name: dns-records
description: DNS records for the zones available in the namespace
version: 0.1.0
helm:
  chart: helm/crossplane-route53-records
  chartVersion: "3.0.10"
```

### Records in values.yaml
In the `values.yaml` file you can specify the needed records in the array `records`. 

Each record should reference a zone using the attribute `zoneName`. Simply use 
the fully qualified domain name for any zone hosted in the cluster.

You must also provide a ttl (in seconds), the actual values in the `records` array and 
of course the record type in `type`. 

The `name` field should contain the subdomain part of a CNAME or A record. To create an 
`A` record pointing `foo.bar.idp.jppol.dk` to the ip address `1.2.3.4` you 
should use a record like 
```yaml
records:
  - zoneName: bar.idp.jppol.dk
    name: foo
    records:
      - "1.2.3.4"
    ttl: 120
    type: A
```
To create a record for the zone itself (the apex), set `name` to an empty string.
To create a wildcard record, set `name` to `"*"`:
```yaml
records:
  - zoneName: bar.idp.jppol.dk
    name: ""
    records:
      - "1.2.3.4"
    ttl: 300
    type: A
  - zoneName: bar.idp.jppol.dk
    name: "*"
    records:
      - "1.2.3.4"
    ttl: 300
    type: A
```

The supported record types are `A`, `AAAA`, `CNAME`, `MX`, `TXT`, `SRV`, `NS`, `PTR` and `SOA`.

Each combination of `zoneName`, `name` and `type` can only be used once in a namespace. To give
a record more than one value, list all the values in its `records` array.

A full set of examples below. 
```yaml
records:
  - zoneName: bar.idp.jppol.dk
    name: _0123456789abcdef0123456789abcdef
    records:
      - _fedcba9876543210fedcba9876543210.abcdefghij.acm-validations.aws.
    ttl: 60
    type: CNAME

  - zoneName: bar.idp.jppol.dk
    name: _dmarc
    records:
      - "v=DMARC1; p=none;"
    ttl: 300
    type: TXT

  - zoneName: bar.idp.jppol.dk
    type: MX
    name: mail
    records:
      - "10 feedback-smtp.eu-west-1.amazonses.com"
    ttl: 300

  - zoneName: bar.idp.jppol.dk
    type: TXT
    name: mail
    records:
      - "v=spf1 include:amazonses.com ~all"
    ttl: 300
```

### Crossplane policies for DNS records
The Route53 records chart exposes Crossplane policy controls in values:

```yaml
managementPolicies: Control   # Control = create/update; Observe = adopt existing records
deletionPolicy: Delete         # Delete = allow deletions; Orphan = leave records behind
```

- Records
  - Control => Crossplane creates and updates DNS records.
  - Observe => Crossplane does not create or update records. This can be used to adopt records that already exist.
  - If `deletionPolicy` is Delete, Delete is also included so removing a record from `values.yaml` will delete it in Route53. With Orphan, removals in values do not delete existing records.
  - Delete is included with Observe as well. To adopt existing records without risking that they are deleted, set `deletionPolicy: Orphan` together with `managementPolicies: Observe`.
- Zones are always rendered with `managementPolicies: ["Observe"]` and cannot be created by this chart; the IDP platform manages zones.

### Conflicting records
If you set identical DNS records in both idp-advanced and the route53-chart, the system backing 
idp-advanced will compete with the system supporting route53. There is currently no detection of this.  
