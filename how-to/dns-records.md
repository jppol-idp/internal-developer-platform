---
title: DNS records and custom domains
nav_order: 6
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2025-10-02
review_in: 6 months
---
# DNS records and custom domains

## Which DNS domains (zones) can I control 
Each cluster is connected to an AWS account which has got one or more associated 
dns zones or domains. 

Each namespace you control via your team's apps-repository can modify DNS 
records within any zone in that cluster's account. 

All available zones are listed in the `README.md` in the namespaces folder 
in the apps repository.

Domains for an account may change. Please act responsibly while working with DNS: 
there may be zones logically belonging to other teams also hosted in the 
same cluster. Please don't experiment with such zones. 

## How to control DNS
The most straightforward way to work with DNS is to use the idp-advanced chart,
where you list the fully qualified domain names (FQDNs) you want for each
service in the `fqdn` field of your `values.yaml`. When you use this field,
DNS records are created automatically and a certificate is issued for the
domain — DNS and certificate issuance are both handled for you.

### Which domains can I use?
Each account only allows binding to a limited set of domains. The available
domains for your namespace are listed in the README file in the apps
repository, under your namespace. For `pol-dev`, see:
[apps-pol/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md)

The default domains are `pol-dev.idp.jppol.dk` and `pol-test.idp.jppol.dk`,
but the list can be extended for your account — this requires some
configuration on our side, so reach out on Slack if you need an additional
domain enabled.

Once a domain is available for your account, you can add subdomains under it
in the `fqdn` field of each application's `values.yaml`.

### Using a domain hosted in another account or by another team
It's also possible to point a domain that isn't on your account's list to
your service, but it's more involved:

1. Contact the owner of the root domain and ask them to create an A record
   pointing to the load balancer addresses listed in your namespace's README.
2. Once that record is in place, add the address in the `fqdn` field of your
   `values.yaml`. Certificate issuance will then happen automatically.

### DNS records not belonging to a specific deployment. 
It is possible to set arbitrary records in a given dns zone without 
the records being related to web services or other deployments inside the cluster. 

Here you can use the chart [`crossplane-route53-records`](https://github.com/jppol-idp/helm-idp/tree/main/charts/crossplane-route53-records). 

This chart becomes relevant when you
- Want to create validation records of type `TXT`
- Want to prepare a migration by creating CNAMEs to deployments hosted outside IDP. 
- Want to setup MX records
- Need to perform actions not anticipated in this documentation :) 

In short: You can maintain DNS records inside IDP hosted zones for whatever purpose you want. 

## Crossplane policies for DNS records
The Route53 records chart exposes Crossplane policy controls in values:

```yaml
managementPolicies: Control   # Control = create/update; Observe = read-only
deletionPolicy: Delete         # Delete = allow deletions; Orphan = leave records behind
```

- Records
  - Control => Crossplane may Create, Update, LateInitialize (and Observe) DNS records.
  - Observe => Crossplane only observes existing records. This can be used to adopt records that already exist.
  - If `deletionPolicy` is Delete, Delete is also included so removing a record from `values.yaml` will delete it in Route53. With Orphan, removals in values do not delete existing records.
- Zones are always rendered with `managementPolicies: ["Observe"]` and cannot be created by this chart; the IDP platform manages zones.

Records can be created in one folder for all zones in the cluster, in one folder per namespace 
or in a folder per "purpose". 

Each file contains a list of records referencing the domain by name and setting values, type 
and ttl per record 

### Examples 

Reference the chart `helm/crossplane-route53-records`

```
apiVersion: v2
name: Route53 zones
description: Crossplane mappings for Route53 zones available in the cluster
version: 0.1.0
slackChannel:
helm:
  chart: helm/crossplane-route53-records
  chartVersion: "1.2.4"
```

In the `values.yaml` file you can specify the needed records in the array `records`. 

Each record should reference a zone using the attribute `zoneName`. Simply use 
the fully qualified domain name for any zone hosted in the cluster.

You must also provide a ttl (in seconds), the actual values in the `records` array and 
of course the record type in `type`. 

The `name` field should contain the subdomain part of a CNAME or A record. To create an 
`A` record pointing `dns-example.idp-test.idp.jppol.dk` to the ip address `1.2.3.4` you 
should use a record like 
```yaml
records:
  - zoneName: idp-test.idp.jppol.dk
    name: dns-example
    records:
      - "1.2.3.4"
    ttl: 120
    type: A
```
A full set of examples below. 
```
records:
  - zoneName: dev.login.jppol.dk
    name: _5c17921fdcbab1ebc28f32646927c36b
    records:
      - _65911f457be5b82b76a8545615fba045.zfyfvmchrl.acm-validations.aws.
    ttl: 60
    type: CNAME

  - zoneName: dev.login.jppol.dk
    name: _dmarc
    records:
      - "v=DMARC1; p=none;"
    ttl: 300
    type: TXT

  - zoneName: dev.login.jppol.dk
    type: MX
    name: mail
    records:
      - "10 unwvzosa6qxvts6hvy67d24cubur5g33.dkim.amazonses.com"
    ttl: 300

  - zoneName: dev.login.jppol.dk
    type: TXT
    name: mail
    records:
      - "v=spf1 include:amazonses.com ~all"
    ttl: 300
```

### Conflicting records
If you set identical DNS records in both idp-advanced and the route53-chart, the system backing 
idp-advanced will compete with the system supporting route53. There is currently no detection of this.  
