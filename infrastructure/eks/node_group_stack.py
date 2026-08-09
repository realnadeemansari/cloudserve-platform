from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct

class EKSNodeGroupStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        cluster_name: str,
        node_role_arn: str,
        subnet_ids: list[str],
        **kwargs
    ) -> None:

        super().__init__(
            scope,
            construct_id,
            **kwargs
        )

        self.node_group = eks.CfnNodegroup(
            self,
            "EKSNodeGroup",
            cluster_name=cluster_name,
            nodegroup_name=(
                f"{project_prefix}-eks-node-group"
            ),
            node_role=node_role_arn,
            subnets=subnet_ids,
            scaling_config=(
                eks.CfnNodegroup.ScalingConfigProperty(
                    min_size=0,
                    desired_size=0,
                    max_size=2
                )
            ),
            instance_types=[
                "t3.medium"
            ],
            capacity_type="ON_DEMAND",
            disk_size=20,
            ami_type="AL2023_x86_64_STANDARD",
            update_config=(
                eks.CfnNodegroup.UpdateConfigProperty(
                    max_unavailable=1
                )
            )
        )

        ssm.StringParameter(
            self,
            "EKSNodeGroupNameParameter",
            parameter_name=f"/{project_prefix}/eks/node-group-name",
            string_value=self.node_group.ref
        )