from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ssm as ssm,
)
from constructs import Construct



class ECSServiceStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            project_prefix: str,
            ecs_security_group: ec2.CfnSecurityGroup,
            subnet_ids: list[str],
            target_group,
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
        desired_count = 0

        # Create an ECS service
        self.ecs_service = ecs.CfnService(
            self,
            "ECSService",
            cluster=self.cluster_arn,
            service_name=f"{project_prefix}-ecs-service",
            task_definition=self.task_definition_arn,
            desired_count=desired_count,
            launch_type="FARGATE",
            load_balancers=[
                ecs.CfnService.LoadBalancerProperty(
                    container_name=f"{project_prefix}-container",
                    container_port=8000,
                    target_group_arn=target_group.ref
                )
            ],
            network_configuration=ecs.CfnService.NetworkConfigurationProperty(
                awsvpc_configuration=ecs.CfnService.AwsVpcConfigurationProperty(
                    subnets=subnet_ids,  # Replace with your subnet IDs
                    assign_public_ip="ENABLED",
                    security_groups=[ecs_security_group.ref]
                )
            )
        )
        ssm.StringParameter(
            self,
            "ECSServiceArnParameter",
            parameter_name=f"/{project_prefix}/ecs/service-arn",
            string_value=self.ecs_service.attr_service_arn
        )