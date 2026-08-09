from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ssm as ssm
)
from constructs import Construct

class EKSPodIdentityAssociationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        cluster_name: str,
        eks_load_balancer_controller_role_arn: str,
        **kwargs
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            **kwargs
        )

        self.pod_identity_association = eks.CfnPodIdentityAssociation(
            self,
            "AWSLoadBalancerControllerPodIdentity",
            cluster_name=cluster_name,
            namespace="kube-system",
            role_arn=eks_load_balancer_controller_role_arn,
            service_account="aws-load-balancer-controller",
        )

        ssm.StringParameter(
            self,
            "EKSPodIdentityAssociationNameParameter",
            parameter_name=f"/{project_prefix}/eks/load-balancer-controller-pod-identity-arn",
            string_value=self.pod_identity_association.attr_association_arn
        )