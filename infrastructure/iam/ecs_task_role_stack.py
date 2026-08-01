from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct

class ECSTaskRoleStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            project_prefix: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an IAM role for ECS tasks
        self.ecs_task_role = iam.CfnRole(
            self,
            "ECSTaskRole",
            role_name=f"{project_prefix}-ecs-task-role",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ecs-tasks.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
        )

        # Store the role ARN in SSM Parameter Store
        ssm.StringParameter(
            self,
            "ECSTaskRoleArnParameter",
            parameter_name=f"/{project_prefix}/ecs/task-role-arn",
            string_value=self.ecs_task_role.attr_arn
        )