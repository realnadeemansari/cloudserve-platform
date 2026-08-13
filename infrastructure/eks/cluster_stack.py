from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ssm as ssm,
    aws_iam as iam
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
        eks_kubectl_role,
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

        self.eks_kubectl_access_entry = eks.CfnAccessEntry(
            self,
            "EKSKubectlAccessEntry",
            cluster_name=self.cluster.ref,
            principal_arn=eks_kubectl_role.attr_arn,
            type="STANDARD",
            access_policies=[
                eks.CfnAccessEntry.AccessPolicyProperty(
                    policy_arn="arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy",
                    access_scope=eks.CfnAccessEntry.AccessScopeProperty(
                        type="cluster"
                    )
                )
            ]
        )


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