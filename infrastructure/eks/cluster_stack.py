from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ssm as ssm
)
from constructs import Construct

class EKSClusterStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        subnets_ids: list[str],
        eks_role_arn: str,
        **kwargs
    ) -> None:

        super().__init__(
            scope,
            construct_id,
            **kwargs
        )

        self.cluster = eks.CfnCluster(
            self,
            "EKSCluster",
            name=f"{project_prefix}-eks-cluster",
            version="1.33",
            role_arn=eks_role_arn,
            resources_vpc_config=eks.CfnCluster.ResourcesVpcConfigProperty(
                subnet_ids=subnets_ids,
                endpoint_public_access=True,
                endpoint_private_access=True
            ),
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-eks-cluster"
                }
            ]
        )

        self.pod_identity_agent = eks.CfnAddon(
            self,
            "EKSClusterPodIdentityAgent",
            addon_name="eks-pod-identity-agent",
            cluster_name=self.cluster.ref,
            resolve_conflicts="OVERWRITE"
        )

        self.pod_identity_agent.add_dependency(self.cluster)

        ssm.StringParameter(
            self,
            "EKSClusterNameParameter",
            parameter_name=f"/{project_prefix}/eks/cluster-name",
            string_value=self.cluster.ref
        )

        ssm.StringParameter(
            self,
            "EKSClusterArnParameter",
            parameter_name=f"/{project_prefix}/eks/cluster-arn",
            string_value=self.cluster.attr_arn
        )

        ssm.StringParameter(
            self,
            "EKSClusterEndpointParameter",
            parameter_name=f"/{project_prefix}/eks/cluster-endpoint",
            string_value=self.cluster.attr_endpoint
        )