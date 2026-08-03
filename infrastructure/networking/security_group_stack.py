from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class SecurityGroupStack(Stack):
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
        self.alb_security_group = ec2.CfnSecurityGroup(
            self,
            "ALBSecurityGroup",
            group_name=f"{project_prefix}-alb-sg",
            vpc_id=vpc_id,
            tags=[{
                "key": "Name",
                "value": f"{project_prefix}-alb-sg"
            }],
            group_description="Security group for ALB",
        )

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
        self.alb_security_group_rule = ec2.CfnSecurityGroupIngress(
            self,
            "ALBHttpIngress",
            group_id=self.alb_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_ip="0.0.0.0/0",
            description="Allow inbound traffic on port 80 (HTTP)"
        )
        self.alb_security_group_rule = ec2.CfnSecurityGroupIngress(
            self,
            "ALBHttpsIngress",
            group_id=self.alb_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_ip="0.0.0.0/0",
            description="Allow inbound traffic on port 443 (HTTPS)"
        )
        self.ecs_security_group_rule = ec2.CfnSecurityGroupIngress(
            self,
            "ECSSecurityGroupRule",
            group_id=self.ecs_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=8000,
            to_port=8000,
            source_security_group_id=self.alb_security_group.attr_group_id,
            description="Temporary public access to FastAPI"
        )