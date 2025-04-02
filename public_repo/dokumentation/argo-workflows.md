---
title: Argo Workflows
parent: Dokumentation
---

# Argo Workflows

Argo Workflows is supported on all our clusters in order to enable job
orchestration.

This documentation is just to give a rough idea of what is possible In the
future a Helm chart will be made available to scaffold the many configuration
options.

## Deploying a workflow

In order to deploy a workflow a few resources must be defined; a
`WorkflowTemplate`, a `ServiceAccount`, a `Role` and a `RoleBinding`. Optionally
an iam `Role` for Crossplane can be defined if access is needed to AWS
resources, beyond the basic access to S3 artifact storage, which is provided by
default.

The following are three examples of workflows in order of increasing complexity.

### Example 1: Simplest workflow

This first one simply prints a message to the logs, without interacting with
artifacts or custom IAM permissions.

This is the minimum configuration needed to run a workflow.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: example-workflow
spec:
  entrypoint: artifact-example
  serviceAccountName: example-workflow
  templates:
    - name: hello-world
      container:
        image: busybox
        command: [sh, -c]
        args: ["sleep 1; echo hello world"]
    - name: artifact-example
      steps:
        - - name: print-message
            template: hello-world
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: example-workflow
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: example-workflow
rules:
  - apiGroups:
      - argoproj.io
    resources:
      - workflowtaskresults
    verbs:
      - create
      - patch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: example-workflow
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: example-workflow
subjects:
  - kind: ServiceAccount
    name: example-workflow
```

### Example 2: Workflow with artifacts

This example demonstrates how to interact with artifacts. This workflow will
print a message to a file, then read that message out in another job.

For this workflow we don't need any IAM permissions aside from interacting with
the S3 bucket, which is included per default.

We will also set garbage collection to delete the artifacts after the workflow
has completed.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: example-artifact-workflow
spec:
  entrypoint: artifact-example
  serviceAccountName: example-artifact-workflow
  artifactGC:
    strategy: OnWorkflowCompletion
    serviceAccountName: example-artifact-workflow
  templates:
    - name: hello-world-to-file
      container:
        image: busybox
        command: [sh, -c]
        args: ["sleep 1; echo hello world | tee /tmp/hello_world.txt"]
      outputs:
        artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
    - name: print-message-from-file
      container:
        image: alpine:latest
        command: [sh, -c]
        args: ["cat /tmp/message"]
      inputs:
        artifacts:
          - name: message
            path: /tmp/message
    - name: artifact-example
      steps:
        - - name: generate-artifact
            template: hello-world-to-file
        - - name: consume-artifact
            template: print-message-from-file
            arguments:
              artifacts:
                - name: message
                  from:
                    "{{
                    `{{steps.generate-artifact.outputs.artifacts.hello-art}}` }}"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: example-artifact-workflow
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: example-artifact-workflow
rules:
  - apiGroups:
      - argoproj.io
    resources:
      - workflowtaskresults
    verbs:
      - create
      - patch
  - apiGroups:
      - argoproj.io
    resources:
      - workflowartifactgctasks
    verbs:
      - list
      - watch
  - apiGroups:
      - argoproj.io
    resources:
      - workflowartifactgctasks/status
    verbs:
      - patch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: example-artifact-workflow
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: example-artifact-workflow
subjects:
  - kind: ServiceAccount
    name: example-artifact-workflow
```

### Example 3: Workflow with IAM permissions

This example does the same as the previous example, but also adds another step
that makes a call to list sqs queues in AWS. That means the workflow needs
additional IAM permissions, which we are including via the provisioning of an
IAM role and the addition of an annotation.

> **Important:** As in the following example, the IAM role will need permission
> to assume IAM roles, so that it can return to the default role used by
> argo-workflows to interact with the S3 bucket.

Note that this example includes hardcoded AWS account ids and an OIDC provider
identifier, which you would need to replace with your own values.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: example-artifact-iam-workflow
spec:
  entrypoint: artifact-example
  serviceAccountName: example-artifact-iam-workflow
  artifactGC:
    strategy: OnWorkflowCompletion
    serviceAccountName: example-artifact-iam-workflow
  templates:
    - name: list-queues
      container:
        image: amazon/aws-cli
        command: [aws, sqs, list-queues]
    - name: hello-world-to-file
      container:
        image: busybox
        command: [sh, -c]
        args: ["sleep 1; echo hello world | tee /tmp/hello_world.txt"]
      outputs:
        artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
    - name: print-message-from-file
      container:
        image: alpine:latest
        command: [sh, -c]
        args: ["cat /tmp/message"]
      inputs:
        artifacts:
          - name: message
            path: /tmp/message
    - name: artifact-example
      steps:
        - - name: list-queues
            template: list-queues
        - - name: generate-artifact
            template: hello-world-to-file
        - - name: consume-artifact
            template: print-message-from-file
            arguments:
              artifacts:
                - name: message
                  from:
                    "{{
                    `{{steps.generate-artifact.outputs.artifacts.hello-art}}` }}"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: example-artifact-iam-workflow
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::971422674709:role/crossplane/example-artifact-iam-workflow
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: example-artifact-iam-workflow
rules:
  - apiGroups:
      - argoproj.io
    resources:
      - workflowtaskresults
    verbs:
      - create
      - patch
  - apiGroups:
      - argoproj.io
    resources:
      - workflowartifactgctasks
    verbs:
      - list
      - watch
  - apiGroups:
      - argoproj.io
    resources:
      - workflowartifactgctasks/status
    verbs:
      - patch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: example-artifact-iam-workflow
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: example-artifact-iam-workflow
subjects:
  - kind: ServiceAccount
    name: example-artifact-iam-workflow
---
apiVersion: iam.aws.upbound.io/v1beta1
kind: Role
metadata:
  name: example-artifact-iam-workflow
spec:
  forProvider:
    inlinePolicy:
      - name: assume-role
        policy: |
          {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Resource": "*"
                }
            ]
          }
      - name: list-queues
        policy: |
          {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sqs:ListQueues"
                    ],
                    "Resource": "*"
                }
            ]
          }
    assumeRolePolicy: |
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Effect": "Allow",
                  "Principal": {
                      "Federated": "arn:aws:iam::971422674709:oidc-provider/oidc.eks.eu-west-1.amazonaws.com/id/BF3868100CBA6D33DB43E6DE6BABD287"
                  },
                  "Action": "sts:AssumeRoleWithWebIdentity",
                  "Condition": {
                      "StringLike": {
                          "oidc.eks.eu-west-1.amazonaws.com/id/BF3868100CBA6D33DB43E6DE6BABD287:aud": "sts.amazonaws.com",
                          "oidc.eks.eu-west-1.amazonaws.com/id/BF3868100CBA6D33DB43E6DE6BABD287:sub": "system:serviceaccount:*:example-artifact-iam-workflow"
                      }
                  }
              }
          ]
      }
    path: /crossplane/
    permissionsBoundary: arn:aws:iam::971422674709:policy/crossplane-permission-boundaries
  providerConfigRef:
    name: irsa
```
