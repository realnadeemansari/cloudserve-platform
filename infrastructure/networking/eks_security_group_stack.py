from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class EKSSecurityGroupStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        project_prefix: str,
        vpc_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a security group for the ECS service
        self.eks_security_group = ec2.CfnSecurityGroup(
            self,
            "EKSSecurityGroup",
            group_name=f"{project_prefix}-eks-sg",
            vpc_id=vpc_id,
            tags=[{
                "key": "Name",
                "value": f"{project_prefix}-eks-sg"
            }],
            group_description="Security group for EKS Fargate service",
        )
