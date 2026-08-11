from aws_cdk import (
    Stack,
    aws_eks as eks,
)
from constructs import Construct

class EKSApplicationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        cluster: eks.ICluster,
        ecr_image_uri: str,
        **kwargs
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            **kwargs
        )

        # Create an EKS application stack
        self.eks_application_stack = eks.KubernetesManifest(
            self,
            "EKSApplicationManifest",
            cluster=cluster,
            manifest=[
                {
                    "apiVersion": "apps/v1",
                    "kind": "Namespace",
                    "metadata": {
                        "name": f"{project_prefix}-eks-namespace",
                    }
                },
                {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {
                        "name": f"{project_prefix}-eks-deployment",
                        "namespace": f"{project_prefix}-eks-namespace"
                    },
                    "spec": {
                        "replicas": 2,
                        "selector": {
                            "matchLabels": {
                                "app": f"{project_prefix}-eks-app"
                            }
                        },
                        "template": {
                            "metadata": {
                                "labels": {
                                    "app": f"{project_prefix}-eks-app"
                                }
                            },
                            "spec": {
                                "containers": [
                                    {
                                        "name": f"{project_prefix}-container",
                                        "image": ecr_image_uri,
                                        "ports": [
                                            {
                                                "containerPort": 8000
                                            }
                                        ],
                                        "resources": {
                                            "requests": {
                                                "cpu": "250m",
                                                "memory": "256Mi"
                                            },
                                            "limits": {
                                                "cpu": "500m",
                                                "memory": "512Mi"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": f"{project_prefix}-eks-service",
                        "namespace": f"{project_prefix}-eks-namespace"
                    },
                    "spec": {
                        "type": "ClusterIP",
                        "selector": {
                            "app": f"{project_prefix}-eks-app"
                        },
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 80,
                                "targetPort": 8000
                            }
                        ]
                    }
                },
                {
                    "apiVersion": "networking.k8s.io/v1",
                    "kind": "Ingress",
                    "metadata": {
                        "name": f"{project_prefix}-eks-ingress",
                        "namespace": f"{project_prefix}-eks-namespace",
                        "annotations": {
                            "alb.ingress.kubernetes.io/scheme": "internet-facing",
                            "alb.ingress.kubernetes.io/listen-ports": '[{"HTTP":80}]',
                            "alb.ingress.kubernetes.io/target-type": "ip"
                        }
                    },
                    "spec": {
                        "ingressClassName": "alb",
                        "rules": [
                            {
                                "http": {
                                    "paths": [
                                        {
                                            "path": "/",
                                            "pathType": "Prefix",
                                            "backend": {
                                                "service": {
                                                    "name": f"{project_prefix}-eks-service",
                                                    "port": {
                                                        "number": 80
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        )