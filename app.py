import aws_cdk as cdk
from infrastructure.iam.ecs_task_role_stack import ECSTaskRoleStack
from infrastructure.iam.ecs_execution_role_stack import ECSExecutionRoleStack
from infrastructure.ecs.cluster_stack import ECSClusterStack
from infrastructure.ecs.service_stack import ECSServiceStack
from infrastructure.ecs.task_definition_stack import ECSTaskDefinitionStack
from infrastructure.ecs.ecr_stack import ECRRepository
from infrastructure.logs.ecs_log_group_stack import ECSLogGroupStack


app = cdk.App()
project_prefix = "csp-sbx"

ecs_execution_role_stack = ECSExecutionRoleStack(
    app,
    "ECSExecutionRoleStack",
    project_prefix=project_prefix,
    stack_name=f"{project_prefix}-ecs-execution-role"
)

ecs_task_role_stack = ECSTaskRoleStack(
    app,
    "ECSTaskRoleStack",
    project_prefix=project_prefix,
    stack_name=f"{project_prefix}-ecs-task-role"
)

logs_stack = ECSLogGroupStack(
    app,
    "ECSLogGroupStack",
    stack_name=f"{project_prefix}-cw-log-group",
    project_prefix=project_prefix
)

ecr_stack = ECRRepository(
    app,
    "ECRRepositoryStack",
    stack_name=f"{project_prefix}-ecr-repo",
    project_prefix=project_prefix
)

ecs_cluster_stack = ECSClusterStack(
    app, 
    "ECSClusterStack",
    project_prefix=project_prefix,
    stack_name=f"{project_prefix}-ecs-cluster",
    )

ecs_task_definition_stack = ECSTaskDefinitionStack(
    app,
    "ECSTaskDefinitionStack",
    project_prefix=project_prefix,
    stack_name=f"{project_prefix}-ecs-task-definition"
)
ecs_task_definition_stack.add_dependency(ecr_stack)

ecs_service_stack = ECSServiceStack(
    app,
    "ECSServiceStack",
    project_prefix=project_prefix,
    stack_name=f"{project_prefix}-ecs-service"
)
ecs_service_stack.add_dependency(ecs_cluster_stack)
ecs_service_stack.add_dependency(ecs_task_definition_stack)

app.synth()