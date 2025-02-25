# IDP Documentation

## Accessing the EKS cluster

### Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed locally
- [AWS](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  CLI installed locally
- A Github account which is a member of the GitHub organization **jppol-idp**
- An AWS SSO account with access to the relevant AWS account containing the idp
  eks cluster

### Recommended but optional tools

- [kubectx](https://github.com/ahmetb/kubectx) - which provides easy switching
  between kubernetes contexts and namespaces.
- [kubecolor](https://github.com/kubecolor/kubecolor) - adds color to your
  kubectl output.
- [K9s](https://k9scli.io/) - an interactive terminal-based UI for Kubernetes
  clusters.
- [aws-vault](https://github.com/99designs/aws-vault) - A tool to securely
  manage temporary AWS credentials

### Step 1: Configure AWS CLI

[Detailed instructions on how to do this are defined here.](https://github.com/jppol-idp/internal-developer-platform/wiki/How-to-authorize-the-aws-cli)

Once you finish configuring the AWS CLI, you can verify that you have access by
running the following command:

```
aws sts get-caller-identity
```

### Step 2: Setup your EKS credentials

We will be using the AWS CLI to interact with our EKS cluster. First, we need to
get the kubeconfig file for our EKS cluster. Run the following command to
download the kubeconfig file. Make sure to replace <cluster-name> with the
actual name of your EKS cluster.

```
aws eks update-kubeconfig --name <cluster-name> --region eu-west-1
```

This will add the EKS cluster's credentials to your local kubeconfig file. You
can verify this by running the following command

```
kubectl config get-contexts
```

You should see the EKS cluster's context listed as the current context.

> **_NOTE:_** If you want to switch between different contexts, you can use the
> following command or use the recommended tool kubectx:
> `kubectl config use-context <context-name>`

Beware that the access you have in this cluster is limited to certain api groups
and namespaces. The level of restrictions are subject to change based on a
need-to basis.

### Step 3: Deploy your application

Instructions for how to deploy your application can be found in your team's app
repository which was provided together with the IDP Kubernetes cluster.

### Step 4. Logging and metrics

#### Logs

All stdout and stderr of the pods are sent to a centralized logging system,
which in our case is Grafana Loki. You can access these logs by going to
`grafana.<cluster-name>.idp.jppol.dk` and logging in. Once logged in, you should
be able to see all the logs for the application by going to **Explore** and
selecting the appropriate log stream.

You also have the option to use kubectl for logs.

```
kubectl get pods --all-namespaces
kubectl logs -n <namespace> <pod-name>
```

#### Metrics

All metrics are sent to a centralized monitoring system, which in our case is
Prometheus. You can access these metrics the same way you access logs by going
to `grafana.<cluster-name>.idp.jppol.dk` and logging in. Once logged in, you
should be able to see all the metrics for the application by going to
**Explore** and choose **Prometheus** as datasource and then select the metric
you want.
