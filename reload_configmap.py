import os
import time
import argparse
from kubernetes import client, config, watch
from subprocess import call

def reload_prometheus(namespace, prometheus_labels):
    v1 = client.CoreV1Api()

    # Get the Prometheus pod name
    pod_list = v1.list_namespaced_pod(namespace, label_selector=prometheus_labels)
    pod_name = pod_list.items[0].metadata.name

    # Trigger Prometheus configuration reload
    call(["kubectl", "-n", namespace, "exec", pod_name, "--", "/bin/kill", "-HUP", "1"])

def main():
    parser = argparse.ArgumentParser(description="Watch a ConfigMap for changes and trigger Prometheus reload.")
    parser.add_argument("namespace", help="Kubernetes namespace")
    parser.add_argument("configmap", help="ConfigMap name")
    parser.add_argument("labels", help="Prometheus pod labels in 'key=value' format")

    args = parser.parse_args()

    # Load Kubernetes configuration
    config.load_incluster_config()

    # Watch for changes in the ConfigMap
    v1 = client.CoreV1Api()
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_config_map, args.namespace):
        config_map = event["object"]
        if config_map.metadata.name == args.configmap:
            print("Detected ConfigMap change. Reloading Prometheus configuration...")
            reload_prometheus(args.namespace, args.labels)
        time.sleep(1)

if __name__ == "__main__":
    main()
