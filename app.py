import aws_cdk as cdk
from config_loader import Config
from infrastructure.iam.ecs_task_role_stack import ECSTaskRoleStack
from infrastructure.iam.ecs_execution_role_stack import ECSExecutionRoleStack
from infrastructure.iam.eks_execution_role_stack import EKSExecutionRoleStack
from infrastructure.iam.eks_node_group_role_stack import EKSNodeGroupRoleStack
from infrastructure.iam.eks_load_balancer_controller_role_stack import EKSLoadBalancerControllerRoleStack
from infrastructure.iam.eks_kubectl_role_stack import EKSKubectlRoleStack
from infrastructure.ecs.cluster_stack import ECSClusterStack
from infrastructure.ecs.service_stack import ECSServiceStack
from infrastructure.ecs.task_definition_stack import ECSTaskDefinitionStack
from infrastructure.ecr.ecr_stack import ECRRepository
from infrastructure.eks.cluster_stack import EKSClusterStack
from infrastructure.eks.node_group_stack import EKSNodeGroupStack
from infrastructure.eks.pod_identity_association_stack import EKSPodIdentityAssociationStack
from infrastructure.eks.application_stack import EKSApplicationStack
from infrastructure.logs.ecs_log_group_stack import ECSLogGroupStack
from infrastructure.networking.ecs_security_group_stack import ECSSecurityGroupStack
from infrastructure.networking.eks_security_group_stack import EKSSecurityGroupStack
from infrastructure.networking.alb_security_group_stack import ALBSecurityGroupStack
from infrastructure.alb.alb_stack import ALBStack


config = Config("./config/sbx.yaml")

app = cdk.App()
project_prefix = config.get_env("project_prefix")
vpc_id = config.get_env("vpc_id")
subnet_ids = config.get_env("subnet_ids")
domain_name = config.get_env("domain_name")

print(f"Environment: {config.environment}")
print(f"Project prefix: {project_prefix}")

ecs_execution_role_stack = None
ecs_task_role_stack = None
ecs_logs_stack = None
ecr_repository_stack = None
ecs_cluster_stack = None
ecs_task_definition_stack = None
ecs_security_group_stack = None
alb_stack = None
ecs_service_stack = None
eks_node_group_stack = None
eks_node_group_role_stack = None
eks_cluster_stack = None
eks_application_stack = None

print(config.is_enabled("iam", "ecs_execution_role_stack"), config.is_enabled("ecr", "ecr_repository_stack"))

if config.is_enabled("iam", "ecs_execution_role_stack"):
    ecs_execution_role_stack = ECSExecutionRoleStack(
        app,
        "ECSExecutionRoleStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-ecs-execution-role"
    )

if config.is_enabled("iam", "ecs_task_role_stack"):
    ecs_task_role_stack = ECSTaskRoleStack(
        app,
        "ECSTaskRoleStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-ecs-task-role"
    )

if config.is_enabled("logs", "ecs_logs_stack"):
    ecs_logs_stack = ECSLogGroupStack(
        app,
        "ECSLogGroupStack",
        stack_name=f"{project_prefix}-cw-log-group",
        project_prefix=project_prefix
    )

if config.is_enabled("ecr", "ecr_repository_stack"):
    ecr_repository_stack = ECRRepository(
        app,
        "ECRRepositoryStack",
        stack_name=f"{project_prefix}-ecr-repo",
        project_prefix=project_prefix
    )

if config.is_enabled("ecs", "ecs_cluster_stack"):
    ecs_cluster_stack = ECSClusterStack(
        app, 
        "ECSClusterStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-ecs-cluster",
        )

if config.is_enabled("ecs", "ecs_task_definition_stack"):
    ecs_task_definition_stack = ECSTaskDefinitionStack(
        app,
        "ECSTaskDefinitionStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-ecs-task-definition"
    )
    if ecr_repository_stack:
        ecs_task_definition_stack.add_dependency(ecr_repository_stack)

if config.is_enabled("networking", "alb_security_group_stack"):
    alb_security_group_stack = ALBSecurityGroupStack(
        app,
        "ALBSecurityGroupStack",
        project_prefix=project_prefix,
        vpc_id=vpc_id,
        stack_name=f"{project_prefix}-alb-security-group"
    )

if config.is_enabled("networking", "ecs_security_group_stack"):
    ecs_security_group_stack = ECSSecurityGroupStack(
        app,
        "ECSSecurityGroupStack",
        project_prefix=project_prefix,
        alb_security_group=alb_security_group_stack.alb_security_group,
        vpc_id=vpc_id,
        stack_name=f"{project_prefix}-ecs-security-group"
    )

if config.is_enabled("networking", "eks_security_group_stack"):
    eks_security_group_stack = EKSSecurityGroupStack(
        app,
        "EKSSecurityGroupStack",
        project_prefix=project_prefix,
        alb_security_group=alb_security_group_stack.alb_security_group,
        vpc_id=vpc_id,
        stack_name=f"{project_prefix}-eks-security-group"
    )

if config.is_enabled("alb", "alb_stack"):
    alb_stack = ALBStack(
        app,
        "ALBStack",
        project_prefix=project_prefix,
        vpc_id=vpc_id,
        subnet_ids=subnet_ids,
        alb_security_group=alb_security_group_stack.alb_security_group,
        stack_name=f"{project_prefix}-alb"
    )

if config.is_enabled("ecs", "ecs_service_stack"):
    if not ecs_cluster_stack:
        raise ValueError(
            "ecs_service_stack requires ecs_cluster_stack to be enabled"
        )

    if not ecs_task_definition_stack:
        raise ValueError(
            "ecs_service_stack requires ecs_task_definition_stack to be enabled"
        )

    if not alb_stack:
        raise ValueError(
            "ecs_service_stack requires alb_stack to be enabled"
        )

    if not ecs_security_group_stack:
        raise ValueError(
            "ecs_service_stack requires ecs_security_group_stack to be enabled"
        )
    ecs_service_stack = ECSServiceStack(
        app,
        "ECSServiceStack",
        project_prefix=project_prefix,
        ecs_security_group=ecs_security_group_stack.ecs_security_group,
        subnet_ids=subnet_ids,
        target_group=alb_stack.target_group,
        stack_name=f"{project_prefix}-ecs-service"
    )
    ecs_service_stack.add_dependency(ecs_cluster_stack)
    ecs_service_stack.add_dependency(ecs_task_definition_stack)
    ecs_service_stack.add_dependency(alb_stack)

if config.is_enabled("iam", "eks_execution_role_stack"):
    eks_execution_role_stack = EKSExecutionRoleStack(
        app,
        "EKSExecutionRoleStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-execution-role"
    )

if config.is_enabled("iam", "eks_node_group_role_stack"):
    eks_node_group_role_stack = EKSNodeGroupRoleStack(
        app,
        "EKSNodeGroupRoleStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-node-group-role"
    )

if config.is_enabled("iam", "eks_load_balancer_controller_role_stack"):
    eks_load_balancer_controller_role_stack = EKSLoadBalancerControllerRoleStack(
        app,
        "EKSLoadBalancerControllerRoleStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-load-balancer-controller-role"
    )

if config.is_enabled("iam", "eks_kubectl_role_stack"):
    eks_kubectl_role_stack = EKSKubectlRoleStack(
            app,
            "EKSKubectlRoleStack",
            project_prefix=project_prefix,
            stack_name=f"{project_prefix}-eks-kubectl-role",
        )

if config.is_enabled("eks", "eks_cluster_stack"):
    eks_cluster_stack = EKSClusterStack(
        app,
        "EKSClusterStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-cluster",
        subnets_ids=subnet_ids,
        eks_role_arn=eks_execution_role_stack.eks_role.attr_arn,
        eks_kubectl_role=eks_kubectl_role_stack.eks_kubectl_role
    )
    eks_cluster_stack.add_dependency(eks_kubectl_role_stack)

if config.is_enabled("eks", "eks_node_group_stack"):
    eks_node_group_stack = EKSNodeGroupStack(
        app,
        "EKSNodeGroupStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-node-group",
        cluster_name=eks_cluster_stack.cluster.ref,
        subnet_ids=subnet_ids,
        node_role_arn=eks_node_group_role_stack.eks_node_role.attr_arn
    )

if config.is_enabled("eks", "eks_pod_identity_association_stack"):
    eks_pod_identity_association_stack = EKSPodIdentityAssociationStack(
        app,
        "EKSPodIdentityAssociationStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-pod-identity-association",
        cluster_name=eks_cluster_stack.cluster.ref,
        eks_load_balancer_controller_role_arn=eks_load_balancer_controller_role_stack.eks_lb_controller_role.attr_arn
    )

    
if config.is_enabled("eks", "eks_application_stack"):
    eks_application_stack = EKSApplicationStack(
        app,
        "EKSApplicationStack",
        project_prefix=project_prefix,
        stack_name=f"{project_prefix}-eks-application",
        cluster=eks_cluster_stack.cluster,
        ecr_image_uri=f"{ecr_repository_stack.repository.attr_repository_uri}:latest",
        eks_kubectl_role=eks_kubectl_role_stack.eks_kubectl_role
    )
    eks_application_stack.add_dependency(eks_cluster_stack)
    eks_application_stack.add_dependency(eks_kubectl_role_stack)

app.synth()