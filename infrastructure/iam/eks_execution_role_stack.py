from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct

class EKSExecutionRoleStack(Stack):
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

        self.eks_role = iam.CfnRole(
            self,
            "EKSExecutionRole",
            role_name=f"{project_prefix}-eks-execution-role",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "eks.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            managed_policy_arns=["arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"],
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-eks-execution-role"
                }
            ]
        )
        ssm.StringParameter(
            self,
            "EKSExecutionRoleArnParameter",
            parameter_name=f"/{project_prefix}/eks/execution-role-arn",
            string_value=self.eks_role.attr_arn
        )