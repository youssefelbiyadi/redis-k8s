ˋˋˋ yaml
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
ˋˋˋ