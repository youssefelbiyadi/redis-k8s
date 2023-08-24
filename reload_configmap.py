import os
import time
from kubernetes import client, config, watch
from subprocess import call

def reload_prometheus():
    # Replace with your Kubernetes namespace and Prometheus pod labels
    namespace = "your-namespace"
    prometheus_labels = "app=prometheus"

    # Get the Prometheus pod name
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace, label_selector=prometheus_labels)
    pod_name = pod_list.items[0].metadata.name

    # Trigger Prometheus configuration reload
    call(["kubectl", "-n", namespace, "exec", pod_name, "--", "/bin/kill", "-HUP", "1"])

def main():
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Replace with your ConfigMap name and namespace
    config_map_name = "prometheus-config"
    namespace = "your-namespace"

    # Watch for changes in the ConfigMap
    v1 = client.CoreV1Api()
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_config_map, namespace):
        config_map = event["object"]
        if config_map.metadata.name == config_map_name:
            print("Detected ConfigMap change. Reloading Prometheus configuration...")
            reload_prometheus()
        time.sleep(1)

if __name__ == "__main__":
    main()
