from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class ECSSecurityGroupStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        project_prefix: str,
        alb_security_group,
        vpc_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a security group for the ECS service
        self.ecs_security_group = ec2.CfnSecurityGroup(
            self,
            "ECSSecurityGroup",
            group_name=f"{project_prefix}-ecs-sg",
            vpc_id=vpc_id,
            tags=[{
                "key": "Name",
                "value": f"{project_prefix}-ecs-sg"
            }],
            group_description="Security group for ECS Fargate service",
        )

        # Allow inbound traffic on port 8000 (FastAPI)
        self.ecs_security_group_rule = ec2.CfnSecurityGroupIngress(
            self,
            "ECSSecurityGroupRule",
            group_id=self.ecs_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=8000,
            to_port=8000,
            source_security_group_id=alb_security_group.attr_group_id,
            description="Temporary public access to FastAPI"
        )