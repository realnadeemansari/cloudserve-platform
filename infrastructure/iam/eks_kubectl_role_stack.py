from aws_cdk import (
    Stack,
    Aws,
    aws_iam as iam,
)
from constructs import Construct

class EKSKubectlRoleStack(Stack):
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

        self.eks_kubectl_role = iam.CfnRole(
            self,
            "EKSKubectlRole",
            role_name=f"{project_prefix}-eks-kubectl-role",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": f"arn:aws:iam::{Aws.ACCOUNT_ID}:root",
                        },
                        "Action": "sts.AssumeRole"
                    }
                ]
            },
            policies=[
                iam.CfnRole.PolicyProperty(
                    policy_name=f"{project_prefix}-eks-cluster-policy",
                    policy_document={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "eks:DescribeCluster"
                                ],
                                "Resource": "*"
                            }
                        ]
                    }
                )
            ]
        )

        self.eks_kubectl_role.policies.append(
            iam.CfnRole.PolicyProperty(
                policy_name=f"{project_prefix}-eks-log-policy",
                policy_document={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "*",
                        }
                    ],
                },
            )
        )

        self.eks_kubectl_role.managed_policy_arns = [
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        ]