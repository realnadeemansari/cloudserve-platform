from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct

class EKSLoadBalancerControllerRoleStack(Stack):
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

        self.eks_lb_controller_role = iam.CfnRole(
            self,
            "EKSLoadBalancerControllerRole",
            role_name=f"{project_prefix}-eks-lb-controller-role",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "pods.eks.amazonaws.com"
                        },
                        "Action": [
                            "sts:AssumeRole",
                            "sts:TagSession"
                        ]
                    }
                ]
            },
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess"
            ],
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-eks-lb-controller-role"
                }
            ]
        )

        ssm.StringParameter(
            self,
            "EKSLoadBalancerControllerRoleArnParameter",
            parameter_name=f"/{project_prefix}/eks/lb-controller-role-arn",
            string_value=self.eks_lb_controller_role.attr_arn
        )