---
title: EBS Disaster Recovery
parent: Dokumentation
---

# EBS Disaster Recovery

This guide details how to take an existing EBS volume in AWS and connect it to
our cluster, allowing applications to recover in a disaster scenario, so long as
the EBS volume remains (or can be restored).

## About retention

In order for an EBS volume to not be deleted when the `PersistentVolume` is
deleted in Kubernetes, the `persistentVolumeReclaimPolicy` must be set to
`Retain`. On our clusters we provide two `StorageClass`es for the creation of
EBS volumes; `ebs-csi-encrypted-gp3` and `ebs-csi-encrypted-gp3-retain`. As the
name implies, the latter will set the `persistentVolumeReclaimPolicy` to
`Retain`, making sure the EBS volume will not be deleted, even if the cluster
implodes.

## Creating a new EBS volume

Let's imagine we have a setup like this:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: busybox-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: ebs-csi-encrypted-gp3-retain
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: busybox-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: busybox
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
        - name: busybox
          image: busybox:latest
          command: ["/bin/sh"]
          args: ["-c", "while true; do sleep 3600; done"]
          volumeMounts:
            - name: data-volume
              mountPath: /data
      volumes:
        - name: data-volume
          persistentVolumeClaim:
            claimName: busybox-pvc
```

Here are definiting two resources, a `PersistentVolumeClaim` and a `Deployment`.

The `PersistentVolumeClaim` is requesting a volume of size `1Gi` with the
`StorageClass` set to `ebs-csi-encrypted-gp3-retain`. The EBS controller will
read this and dynamically provision a new EBS volume in AWS and a
`PersistentVolume` in EKS. This volume will be attached to the
`busybox-deployment` pod.

The `Deployment` is simply creating a pod with a single container running
`busybox`, which will run indefinitely. Notablely, the pod is mounting the
`busybox-pvc` claim, which means the EBS volume will be mounted at `/data` in
the container.

## Disaster recovery

Now let's imagine this application is completely lost. Maybe it is accidentally
deleted from Argo CD or the cluster is completely lost. In this case, because we
set the `persistentVolumeReclaimPolicy` to `Retain`, the EBS volume will not be
deleted and remains on AWS.

In order to be able to recover the application, we need to now statically define
the volume and pass it a reference to the volume on AWS. Let's take a look at
these manifests that build upon our previous example:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: busybox-pv
spec:
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    # This is the volume ID of the EBS volume in AWS
    volumeID: aws://eu-west-1c/vol-0c00d61fe88d53bbc
  capacity:
    storage: 1Gi
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ebs-csi-encrypted-gp3-retain
  volumeMode: Filesystem
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: busybox-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: ebs-csi-encrypted-gp3-retain
  # Reference to the PV
  volumeName: busybox-pv
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: busybox-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: busybox
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
        - name: busybox
          image: busybox:latest
          command: ["/bin/sh"]
          args: ["-c", "while true; do sleep 3600; done"]
          volumeMounts:
            - name: data-volume
              mountPath: /data
      volumes:
        - name: data-volume
          persistentVolumeClaim:
            claimName: busybox-pvc
```

Now we are statically defining a `PersistentVolume` and by setting the
`awsElasticBlockStore` field with the `volumeID` of the EBS volume in AWS, we
are telling Kubernetes to use this existing volume. Then in the
`PersistentVolumeClaim`, it remains identicaly to how it was before except for
the addition of the `volumeName` field, which references the `PersistentVolume`
we just created. The deployment remains unchanged.
