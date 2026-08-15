# CloudServe Platform

CloudServe Platform is a Python + AWS CDK project for provisioning AWS infrastructure and deploying a lightweight FastAPI application to either ECS or EKS. The repository is configured for a sandbox environment (`sbx`) and uses a YAML-driven stack selector to enable or disable infrastructure modules.

## Overview

This project combines:

- AWS CDK application code for creating AWS infrastructure
- ECR image repository support
- ECS deployment support for the app container
- Optional EKS cluster and related IAM / networking support
- Kubernetes ingress and AWS Load Balancer Controller setup
- GitHub Actions workflows for AWS OIDC-based deployment automation
- A simple FastAPI service that exposes health and prediction endpoints

## Repository structure

```text
.
├── app.py                              # CDK app entry point
├── config_loader.py                    # YAML config loader
├── config/
│   └── sbx.yaml                       # Environment-specific stack configuration
├── infrastructure/
│   ├── alb/
│   ├── ecr/
│   ├── ecs/
│   ├── eks/
│   ├── iam/
│   ├── logs/
│   └── networking/
├── application/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── .github/
│   └── workflows/
│       ├── deploy-infra.yaml
│       ├── deploy-app-ecs.yaml
│       └── deploy-app-eks.yaml
├── EKS_IAM_ACCESS_AND_CONTROLLER_SETUP.md
├── GITHUB_AWS_DEPLOYMENT_GUIDE.md
├── iam_policy.json
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
├── source.bat
├── tests/
│   └── unit/
├── cdk.json
├── cdk.out/
└── README.md
```

## Application behavior

The runtime application is a FastAPI service defined in `application/main.py`.

It currently provides:

- `/` -> health check returning service status
- `/predict` -> simple prediction response

This app is small and intentionally lightweight, making it suitable for containerized deployment to ECS or EKS.

## Deployment model

The project is structured around a central CDK app that reads configuration from `config/sbx.yaml` and conditionally creates enabled stacks.

The app loads values such as:

- `project_prefix`
- `vpc_id`
- `subnet_ids`
- `domain_name`
- `github_actions_role_name`
- `user_name`

Then it decides which stacks to synthesize and deploy depending on the YAML flags for categories such as:

- `ecs`
- `ecr`
- `eks`
- `iam`
- `logs`
- `networking`
- `alb`

## Current sandbox configuration

The repository is currently configured for a sandbox environment with these major settings in `config/sbx.yaml`:

```yaml
environment: sbx

env_vars:
  domain_name: cspnbx.online
  project_prefix: csp-sbx
  vpc_id: vpc-0c0b8a4337a2c13c4
  github_actions_role_name: cloudserve-platform-github-action-role
  user_name: nadeem_iam_user
  subnet_ids:
    - subnet-03b8b454d582028e6
    - subnet-00a906a5aa180e1e4
```

The active stack flags in the current config show:

- `ecr` enabled
- `eks` enabled
- `iam` enabled
- `networking` enabled
- `ecs` mostly off, with `ecs_service_stack`, `ecs_cluster_stack`, and `ecs_task_definition_stack` enabled
- `alb` currently off in the config file and the app checks for it before creating ECS service dependencies

This configuration means the project is designed to support both container and Kubernetes deployment patterns depending on which stacks are enabled.

## Prerequisites

Before deploying this project, make sure you have the following installed and configured:

- Python 3.11+
- pip
- Node.js and npm for AWS CDK
- AWS CLI
- Docker
- AWS credentials with permission to create IAM, ECR, ECS, EKS, and VPC-related resources
- AWS CDK CLI

Install Python dependencies with:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r application/requirements.txt
```

If you are using the CDK workflow in GitHub Actions, ensure your GitHub OIDC setup is complete and the AWS role ARN is stored as the `AWS_ROLE_ARN` secret.

## CDK deployment

The AWS infrastructure is created by running the CDK app from `app.py`.

### Synthesize and deploy

```bash
cd /Users/mohdnadeem/projects/cloudserve-platform
cdk synth
cdk diff
cdk deploy --all --require-approval never
```

### How the app decides what to deploy

In `app.py`, each stack is created only if the corresponding config entry is enabled. For example:

```python
if config.is_enabled("ecr", "ecr_repository_stack"):
    ecr_repository_stack = ECRRepository(...)
```

This makes the infrastructure modular and environment-specific.

## Infrastructure components

### ECR

The repository supports building and storing the container image used by the application.

### ECS

The project includes stack definitions for:

- ECS cluster
- Task definition
- Security groups
- ALB security group integration
- ECS service

These components are primarily wired together by `app.py` and the networking / IAM stack dependencies.

### EKS

The EKS side includes:

- EKS cluster creation
- Node group
- IAM execution and node roles
- kubectl role
- Load balancer controller role
- pod identity association
- application stack for Kubernetes deployment

### Networking and ALB

The project includes networking stacks for both ECS and EKS, plus an ALB stack used for the load balancer path.

## GitHub Actions workflows

The repository includes three deployment workflows under `.github/workflows/`:

### 1. Infrastructure deployment

File: `.github/workflows/deploy-infra.yaml`

This workflow installs CDK, configures AWS credentials using OIDC, and runs:

```bash
cdk diff
cdk deploy --all --require-approval never
```

### 2. ECS application deployment

File: `.github/workflows/deploy-app-ecs.yaml`

This workflow:

1. Checks out the `sbx` branch
2. Authenticates with AWS using OIDC
3. Logs into ECR
4. Checks whether the image exists by commit SHA
5. Builds and pushes the image if needed
6. Downloads the ECS task definition
7. Updates the task definition with the new image
8. Deploys the updated task definition to ECS
9. Ensures the ECS service is stable

### 3. EKS application deployment

File: `.github/workflows/deploy-app-eks.yaml`

This workflow:

1. Authenticates to AWS
2. Logs into ECR
3. Builds and pushes the app image
4. Configures `kubectl`
5. Runs `aws eks update-kubeconfig`
6. Updates the Kubernetes deployment image
7. Verifies the rollout status

## Application container build

The Docker image is built from `application/Dockerfile` using the app directory as the build context.

To build it locally:

```bash
cd application
docker build -t cloudserve-platform:local .
```

## EKS IAM and load balancer setup

For Kubernetes and ALB installation details, see:

- `EKS_IAM_ACCESS_AND_CONTROLLER_SETUP.md`
- `GITHUB_AWS_DEPLOYMENT_GUIDE.md`

The repository includes the AWS Load Balancer Controller steps needed for EKS, including:

- downloading the controller IAM policy
- creating the managed IAM policy
- attaching it to the controller role
- detaching the broad AWS-managed ELB policy if required during cleanup
- installing the AWS Load Balancer Controller Helm chart

## Recommended deployment flow

1. Verify AWS credentials and account access.
2. Review `config/sbx.yaml` to confirm the correct environment and enabled stacks.
3. Install project Python dependencies.
4. Run the infrastructure CDK workflow to create AWS resources.
5. Build and push the image to ECR.
6. Deploy the app to ECS or EKS depending on the active environment.
7. Validate the service by checking health endpoints and Kubernetes resources.

## Useful commands

### AWS identity validation

```bash
aws sts get-caller-identity
```

### EKS kubeconfig refresh

```bash
aws eks update-kubeconfig --region us-east-1 --name csp-sbx-eks-cluster
```

### Kubernetes node check

```bash
kubectl get nodes
kubectl get pods -n kube-system
```

### Load balancer controller check

```bash
kubectl get pods -n kube-system
kubectl get deployment -n kube-system
```

## Troubleshooting

- If the cluster does not show nodes, confirm the EKS node group is active and the EC2 workers have joined the cluster.
- If `kubectl` shows credentials errors, refresh kubeconfig and confirm the correct AWS identity is active.
- If the controller is not reconciling ingress resources, verify the service account, IAM trust, and ALB controller pod health.
- If the app cannot start in ECS, confirm the image exists in ECR and the task definition points to the correct image tag.

## Notes

- The project uses YAML-driven configuration rather than hardcoded environment logic.
- The sandbox environment is named `sbx`, and many examples and workflow values are aligned to that naming convention.
- EKS and ECS paths are both supported, but only the stacks enabled in `config/sbx.yaml` are created.
- For production workloads, review IAM scoping, security groups, VPC routing, and Secrets/SSM usage before broad deployment.

## License

This project is licensed under the terms of the LICENSE file.
