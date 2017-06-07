## HAProxy+Kontrol pod

### Overview

This project is a [**Docker**](https://www.docker.com) image packaging
[**NATS 0.9.4**](http://www.nats.io/) together with
[**Kontrol**](https://github.com/UnityTech/ads-infra-kontrol). It is meant
to be included in a [**Kubernetes**](https://github.com/GoogleCloudPlatform/kubernetes)
pod.

The container will run its own control-tier which will re-configure the routes anytime
brokers are added or removed. Please note we do not allow for custom configuration
settings at this point.

### Lifecycle

The initial state will render the [**telegraf**](https://github.com/influxdata/telegraf) 
configuration and add the *statsd* input. The local broker logfile will be written under
*/data* and rotated via *logrotate*. The state will then cycle thru one or more configuration
sequences with the broker configuration written as */data/gnatsd.conf*. All other brokers
currently reporting via *kontrol* will be included in the routes. Please note the client
port is TCP 4242 and the internal cluster port is TCP 4244.

Any change detected by *kontrol* will trip the state-machine back to that configuration
state. The broker itself is restarted via *supervisord*.

### Building the image

Pick a distro and build from the top-level directory. For instance:

```
$ docker build -f alpine-3.5/Dockerfile .
```

### Manifest

Simply use this pod in a deployment and assign it to an array with external access using a
node-port service to clamp onto the desired port. For instance:

```
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: haproxy
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: nats
        role: broker
        tier: data
      annotations:
        kontrol.unity3d.com/master: nats.default.svc
        kontrol.unity3d.com/opentsdb: kairosdb.us-east-1.applifier.info

    spec:
      nodeSelector:
        unity3d.com/array: data
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values: 
                    - nats
              topologyKey: "kubernetes.io/hostname"
      containers:
       - image: registry2.applifier.info:5005/ads-infra-nats-alpine-3.5
         name: nats
         imagePullPolicy: Always
         ports:
         - containerPort: 4242
           protocol: TCP
         - containerPort: 4244
           protocol: TCP
         - containerPort: 8000
           protocol: TCP
         env:
          - name: NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
```

### Support

Contact olivierp@unity3d.com for more information about this project.