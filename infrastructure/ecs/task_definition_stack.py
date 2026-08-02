from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ssm as ssm
)
from constructs import Construct

class ECSTaskDefinitionStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            project_prefix: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference the repository URI from SSM without forcing a synth-time lookup.
        # Using `from_string_parameter_name(...).string_value` returns a token that
        # will be resolved at deploy time. This avoids synth-time failures when the
        # parameter does not yet exist (for initial infra deployment).
        image_param = ssm.StringParameter.from_string_parameter_name(
            self,
            "ECRRepositoryUriParameter",
            string_parameter_name=f"/{project_prefix}/ecr/repository-uri"
        )
        self.image_uri = image_param.string_value

        self.container_definitions = ecs.CfnTaskDefinition.ContainerDefinitionProperty(
            name=f"{project_prefix}-container",
            image=self.image_uri,
            essential=True,
            port_mappings=[
                ecs.CfnTaskDefinition.PortMappingProperty(
                    container_port=8000,
                    host_port=8000,
                    protocol="tcp"
                )
            ],
            log_configuration=ecs.CfnTaskDefinition.LogConfigurationProperty(
                log_driver="awslogs",
                options={
                    "awslogs-group": f"/ecs/{project_prefix}-app",
                    "awslogs-region": self.region,
                    "awslogs-stream-prefix": "ecs"
                }
            )
        )

        # Create an ECS task definition
        self.task_definition = ecs.CfnTaskDefinition(
            self,
            "ECSTaskDefinition",
            family=f"{project_prefix}-ecs-task-definition",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            cpu="1024",
            memory="2048",
            execution_role_arn=f"arn:aws:iam::{self.account}:role/{project_prefix}-ecs-execution-role",
            task_role_arn=f"arn:aws:iam::{self.account}:role/{project_prefix}-ecs-task-role",
            container_definitions=[self.container_definitions]
        )

        ssm.StringParameter(
            self,
            "ECSTaskDefinitionArnParameter",
            parameter_name=f"/{project_prefix}/ecs/task-definition-arn",
            string_value=self.task_definition.attr_task_definition_arn
        )