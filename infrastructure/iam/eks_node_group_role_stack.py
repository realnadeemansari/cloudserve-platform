from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct

class EKSNodeGroupRoleStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        **kwargs
    ) -> None:

        super().__init__(
            scope,
            construct_id,
            **kwargs
        )

        self.eks_node_role = iam.CfnRole(
            self,
            "EKSNodeRole",
            role_name=f"{project_prefix}-eks-node-group-role",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly",
                "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
            ],
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-eks-node-group-role"
                }
            ]
        )

        ssm.StringParameter(
            self,
            "EKSNodeGroupRoleArnParameter",
            parameter_name=f"/{project_prefix}/eks/node-group-role-arn",
            string_value=self.eks_node_role.attr_arn
        )