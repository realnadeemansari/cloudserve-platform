from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct

class ECSExecutionRoleStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            project_prefix: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an IAM role for ECS task execution
        self.ecs_execution_role = iam.CfnRole(
            self,
            "ECSExecutionRole",
            role_name=f"{project_prefix}-ecs-execution-role",
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

        iam.CfnPolicy(
            self,
            "ECSECRPolicy",
            policy_name=f"{project_prefix}-ecs-ecr-policy",
            roles=[self.ecs_execution_role.ref],
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ecr:GetAuthorizationToken",
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:GetDownloadUrlForLayer",
                            "ecr:BatchGetImage"
                        ],
                        "Resource": "*"
                    },
                ]
            }
        )
        iam.CfnPolicy(
            self,
            "ECSLogsPolicy",
            policy_name=f"{project_prefix}-ecs-logs-policy",
            roles=[self.ecs_execution_role.ref],
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "*"
                    }
                ]
            }
        )

        # Store the role ARN in SSM Parameter Store
        ssm.StringParameter(
            self,
            "ECSExecutionRoleArnParameter",
            parameter_name=f"/{project_prefix}/ecs/execution-role-arn",
            string_value=self.ecs_execution_role.attr_arn
        )
