from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ssm as ssm,
)
from constructs import Construct

class ECSClusterStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            project_prefix: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an ECS cluster
        self.cluster = ecs.CfnCluster(
            self,
            "ECSCluster",
            cluster_name=f"{project_prefix}-ecs-cluster"
        )

        # Store the cluster name in SSM Parameter Store
        ssm.StringParameter(
            self,
            "ECSClusterArnParameter",
            parameter_name=f"/{project_prefix}/ecs/cluster-arn",
            string_value=self.cluster.attr_arn
        )