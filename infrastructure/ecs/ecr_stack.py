from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_ecr as ecr,
    aws_ssm as ssm
)
from constructs import Construct

class ECRRepository(Stack):
    def __init__(
        self, 
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        **kwargs
    ):
        super().__init__(
            scope, 
            construct_id,
            **kwargs 
        )
        self.repository = ecr.CfnRepository(
            self,
            "ECRRepository",
            repository_name=f"{project_prefix}-repository",
            image_scanning_configuration=ecr.CfnRepository.ImageScanningConfigurationProperty(
                scan_on_push=True
            ),
            image_tag_mutability="IMMUTABLE"
        )
        self.repository.apply_removal_policy(RemovalPolicy.DESTROY)

        ssm.StringParameter(
            self,
            "RepositoryArn",
            parameter_name=f"/{project_prefix}/ecr/repository-arn",
            string_value=self.repository.attr_arn
        )
        ssm.StringParameter(
            self,
            "RepositryUri",
            parameter_name=f"/{project_prefix}/ecr/repository-uri",
            string_value=self.repository.attr_repository_uri
        )
        ssm.StringParameter(
            self,
            "RepositoryName",
            parameter_name=f"/{project_prefix}/ecr/repository-name",
            string_value=f"{project_prefix}-repository"
        )