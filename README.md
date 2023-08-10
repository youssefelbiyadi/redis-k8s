# Deploy Redis on k8s


In this study, we will compare two ways of deploying Redis on Kubernetes: Redis Sentinels and Redis Cluster. Both approaches have their own advantages and disadvantages, and choosing the right one will depend on the specific needs and requirements of your application.

## Redis Sentinels

Redis Sentinels is a high-availability solution for Redis. It uses a master-slave architecture with automatic failover. The Sentinel nodes are responsible for monitoring the Redis instances and promoting a slave to a master if the current master fails.

### Pros:

- Automatic failover: Redis Sentinels provides automatic failover, which means that if the master node fails, a new master node will be promoted automatically.
- Easy to set up: Redis Sentinels is easy to set up and does not require any additional configuration beyond the standard Redis setup.
- Scalability: Redis Sentinels can be scaled horizontally by adding more Sentinel nodes.

### Cons:

- Limited fault tolerance: Redis Sentinels has limited fault tolerance because all the Sentinel nodes share the same view of the Redis instances. If a network partition occurs, the Sentinels can become split-brain and promote different slaves to masters, resulting in data loss.
- Single point of failure: Redis Sentinels has a single point of failure, which is the Sentinel leader node. If the Sentinel leader fails, a new leader needs to be elected, which can cause service interruption.

### Setting up Redis Sentinels on Kubernetes:

1. Create a Redis master deployment with a single replica.  
2. Create a Redis slave deployment with multiple replicas.  
3. Create a Sentinel deployment with multiple replicas.  
4. Configure the Sentinel nodes to monitor the Redis master and slave nodes.  
5. Configure the Sentinel nodes to promote a slave to a master if the current master fails.  

## Redis Cluster

Redis Cluster is a distributed solution for Redis. It uses a sharding mechanism to split the data across multiple Redis nodes. Each node in the cluster stores only a subset of the data, and a Redis client can connect to any node to read or write data.

### Pros:

- High scalability: Redis Cluster can scale horizontally by adding more Redis nodes to the cluster. It can also distribute the data evenly across the nodes, providing high scalability.
- Fault tolerance: Redis Cluster is fault-tolerant because it uses a sharding mechanism to split the data across multiple nodes. If a node fails, the data can be automatically redistributed to the remaining nodes.
- No single point of failure: Redis Cluster has no single point of failure because the data is distributed across multiple nodes.

### Cons:

- Complex setup: Redis Cluster requires more setup and configuration than Redis Sentinels. It requires setting up a cluster of Redis nodes, and a Redis client needs to be aware of the cluster topology to connect to the right node.
- No cross-node transactions: Redis Cluster does not support cross-node transactions, which means that a transaction cannot involve keys that belong to different nodes.

### Setting up Redis Cluster on Kubernetes:

1. Create a Redis cluster deployment with multiple replicas.  
2. Configure the Redis nodes to form a cluster by joining each other.  
3. Configure the Redis client to connect to the Redis cluster using the correct topology.  

## Conclusion
In conclusion, both Redis Sentinels and Redis Cluster are viable options for deploying Redis on Kubernetes for business applications.  
Redis Sentinels provides automatic failover and easy setup, while Redis Cluster provides high scalability and fault tolerance.  
The choice between the two approaches will depend on the specific needs and requirements of your application. When setting up either Redis Sentinels or Redis Cluster on Kubernetes, it's important to follow the appropriate steps and configurations to ensure a successful deployment.
----

apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
      - job_name: 'blackbox'
        metrics_path: /probe
        params:
          module: [http_2xx]
        static_configs:
          - targets:
            - http://your-app-service-name.namespace.svc.cluster.local/blackbox-exporter/probe
          relabel_configs:
            - source_labels: [__address__]
              target_label: __param_target
            - source_labels: [__param_target]
              target_label: instance
            - target_label: __address__
              replacement: blackbox-exporter.namespace.svc.cluster.local:9115

      - job_name: 'rabbitmq'
        static_configs:
          - targets:
            - your-rmq-service-name.namespace.svc.cluster.local:15692  # Adjust port

      - job_name: 'postgres'
        static_configs:
          - targets:
            - your-postgres-service-name.namespace.svc.cluster.local:9187  # Adjust port

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:v2.34.0
          args:
            - "--config.file=/etc/prometheus/prometheus.yml"
            - "--storage.tsdb.path=/prometheus"
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: prometheus-config
              mountPath: /etc/prometheus
            - name: prometheus-storage
              mountPath: /prometheus
      volumes:
        - name: prometheus-config
          configMap:
            name: prometheus-config
        - name: prometheus-storage
          emptyDir: {}

----

apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  selector:
    app: prometheus
  ports:
    - protocol: TCP
      port: 9090

----

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prometheus-ingress
  namespace: monitoring
spec:
  rules:
    - host: prometheus.example.com  # Adjust the hostname
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: prometheus
                port:
                  number: 9090

---



