from aws_cdk import (
    Stack,
    aws_logs as logs,
    aws_ssm as ssm
)
from constructs import Construct

class ECSLogGroupStack(Stack):
    def __init__(
        self, 
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.log_group = logs.CfnLogGroup(
            self,
            "ECSLogGroup",
            log_group_name=f"/ecs/{project_prefix}-app",
            retention_in_days=7
        )