---
title: Helm chart values
nav_order: 0 
parent: Onboarding
domain: public
---


# idp-advanced

![Version: 0.1.29](https://img.shields.io/badge/Version-0.1.29-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.0](https://img.shields.io/badge/AppVersion-0.1.0-informational?style=flat-square)

IDP Advanced Chart

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| lynetk | <kasper.kn.nielsen@jppol.dk> |  |
| faester | <morten.faester@jppol.dk> |  |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Affinity |
| autoscaling | object | `{"enabled":false,"maxReplicas":10,"minReplicas":1,"targetCPUUtilizationPercentage":80}` | Autoscaling configuration |
| autoscaling.enabled | bool | `false` | Enable or disable autoscaling |
| autoscaling.maxReplicas | int | `10` | Maximum number of pods. Only relevant if autoscaling is enabled |
| autoscaling.minReplicas | int | `1` | Minimum number of pods. Only relevant if autoscaling is enabled |
| autoscaling.targetCPUUtilizationPercentage | int | `80` | Target CPU utilization percentage. Only relevant if autoscaling is enabled |
| compute.arch | string | `"amd64"` | Specify architecture for the deployment. Valid options are 'amd64' and 'arm64'. Default is amd64 |
| compute.gpu.count | int | `1` | Number of GPUs to request |
| compute.gpu.enabled | bool | `false` | Enable or disable GPU support |
| compute.spot | bool | `false` | Allow the deployment to run on spot instances. This is valid for all architectures and GPU deployments. |
| env | list | `[{"name":"FOO","value":"bar"}]` | Environment variables to be passed to the container |
| forceSync | string | `"1"` | Change value of this to enforce a relaod of secrets and a pod restart. |
| fullnameOverride | string | `""` |  |
| idp_aws_account | string | `""` | This value are set by ArgoCD automatically, but can be overridden here for local testing |
| idp_oidc_provider_url | string | `""` | This value are set by ArgoCD automatically, but can be overridden here for local testing |
| image.pullPolicy | string | `"IfNotPresent"` | This is the image pull policy. The options are Always, Never, and IfNotPresent. 'IfNotPresent' is the default. |
| image.repository | string | `"nginx"` | This is the image repository to pull from. 'nginx' is the default and only needed for automated chart-testing |
| image.tag | string | `"stable-alpine"` | This is the image tag to pull. 'stable-alpine' is the default and only needed for automated chart-testing |
| ingress | object | Ingress configuration | Ingress configuration |
| ingress.alb | object | `{"annotations":{},"certificate":{"useWildCardCertificate":false},"group":"","groupOrder":""}` | alb specific configuration |
| ingress.alb.annotations | object | `{}` | alb annotations |
| ingress.alb.certificate | object | `{"useWildCardCertificate":false}` | alb certificate settings |
| ingress.alb.certificate.useWildCardCertificate | bool | `false` | whether to use a wildcard certificate. this certificate is not created by the chart |
| ingress.alb.group | string | `""` | alb group. This is used when you want to use a shared ALB |
| ingress.alb.groupOrder | string | `""` | alb group order. This is used when you want to use a shared ALB |
| ingress.enabled | bool | `false` | Enable or disable ingress |
| ingress.fqdn | list | `[]` | Fully qualified domain name for the ingress. These records will be created in Route53. |
| ingress.nginx | object | `{"private":{"annotations":{},"enabled":false},"public":{"annotations":{},"enabled":true}}` | nginx specific configuration |
| ingress.nginx.private | object | `{"annotations":{},"enabled":false}` | settings for the private nginx ingress controller |
| ingress.nginx.private.annotations | object | `{}` | annotations to add to the private nginx ingress controller |
| ingress.nginx.private.enabled | bool | `false` | whether to enable the private nginx ingress controller |
| ingress.nginx.public | object | `{"annotations":{},"enabled":true}` | settings for the public nginx ingress controller |
| ingress.nginx.public.annotations | object | `{}` | annotations to add to the public nginx ingress controller |
| ingress.nginx.public.enabled | bool | `true` | whether to enable the public nginx ingress controller |
| ingress.type | string | `"nginx"` | Choose ingress type. Supported values are 'nginx' or 'alb'. nginx are preferred. |
| livenessProbe | object | `{"httpGet":{"path":"/","port":"http"},"periodSeconds":10}` | Health checks |
| livenessProbe.periodSeconds | int | `10` | periodSeconds: The time (in seconds) that Kubernetes should wait before reprobing a container if the preceding probe failed (or if you configured a probe to require multiple successful connection attempts). The default interval between probes is 10 seconds |
| nameOverride | string | `""` | This is to override the chart name. |
| nodeSelector | object | `{}` | Node selector |
| podAnnotations | object | `{}` | podAnnotations is a map of key-value pairs to add to the pods |
| podLabels | object | `{}` | podLabels is a map of key-value pairs to add to the pods |
| podSecurityContext | object | `{}` |  |
| readinessProbe.httpGet.path | string | `"/"` |  |
| readinessProbe.httpGet.port | string | `"http"` |  |
| readinessProbe.periodSeconds | int | `10` |  |
| replicaCount | int | `1` | Set the number of replicas for the deployment |
| resources | object | `{"limits":{"memory":"128Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}` | Resource limits and requests. This is a map of key-value pairs to add to the pods. |
| resources.limits.memory | string | `"128Mi"` | Memory resource limits |
| resources.requests.cpu | string | `"100m"` | CPU resource requests |
| resources.requests.memory | string | `"128Mi"` | Memory resource requests |
| securityContext | object | `{}` |  |
| service | object | `{"port":80,"type":"ClusterIP"}` | Servicetype and port for the service |
| serviceAccount.create | bool | `false` | Specifies whether a service account should be created |
| serviceAccount.irsa.enabled | bool | `false` | Specifies whether to use IRSA for the service account |
| serviceAccount.irsa.iamPolicyStatements | list | `[{"Action":["secretsmanager:GetResourcePolicy"],"Effect":"Allow","Resource":"arn:aws:secretsmanager:aws-region:aws-account-id:secret:example/*"}]` | Specifies the IAM policy to attach to the service account |
| startupProbe | object | `{}` |  |
| storage | object | `{}` | Storage configuration. |
| tolerations | list | `[]` | Tolerations |
| vpa.enabled | bool | `false` | Enable or disable VPA |
| vpa.updatePolicy | string | `"Off"` | VPA update policy. Valid options are 'Auto', 'Initial', and 'Off'. Default is 'Off' |

----------------------------------------------
Indholdet er manuelt kopieret fra [helm-docs v1.14.2](https://github.com/jppol-idp/helm-idp-advanced/blob/main/README.md)
