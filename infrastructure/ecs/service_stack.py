from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ssm as ssm,
)
from constructs import Construct

class ECSServiceStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            project_prefix: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cluster_arn = ssm.StringParameter.value_for_string_parameter(
            self,
            f"/{project_prefix}/ecs/cluster-arn"
        )
        self.task_definition_arn = ssm.StringParameter.value_for_string_parameter(
            self,
            f"/{project_prefix}/ecs/task-definition-arn"
        )

        # Create an ECS service
        self.ecs_service = ecs.CfnService(
            self,
            "ECSService",
            cluster=self.cluster_arn,
            service_name=f"{project_prefix}-ecs-service",
            task_definition=self.task_definition_arn,
            desired_count=1,
            launch_type="FARGATE",
            network_configuration=ecs.CfnService.NetworkConfigurationProperty(
                awsvpc_configuration=ecs.CfnService.AwsVpcConfigurationProperty(
                    subnets=["subnet-03b8b454d582028e6", "subnet-00a906a5aa180e1e4"],  # Replace with your subnet IDs
                    assign_public_ip="ENABLED"
                )
            )
        )
        ssm.StringParameter(
            self,
            "ECSServiceArnParameter",
            parameter_name=f"/{project_prefix}/ecs/service-arn",
            string_value=self.ecs_service.attr_service_arn
        )