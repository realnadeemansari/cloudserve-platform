# CloudServe Platform

## Overview

CloudServe Platform is a hybrid AWS deployment repository that includes:

- AWS CDK infrastructure for ECS, ECR, ALB, networking, IAM, and optional EKS resources
- A FastAPI application packaged as a Docker container in `application/`
- GitHub Actions workflow for building, pushing, and deploying the container to ECS
- Configuration-driven stack enablement via `config/sbx.yaml`

## Repository Structure

- `app.py` - CDK application entrypoint that loads config and synthesizes enabled stacks.
- `config/` - environment configuration files for CDK stack enablement and runtime settings.
- `config_loader.py` - YAML config loader used by the CDK app.
- `infrastructure/` - AWS CDK stack modules for ECS, ECR, ALB, networking, IAM, EKS, and logs.
- `application/` - FastAPI app code, Dockerfile, and app dependencies.
- `.github/workflows/deploy-app.yaml` - GitHub Actions workflow for image build, ECR push, task definition update, and ECS deployment.
- `GITHUB_AWS_DEPLOYMENT_GUIDE.md` - detailed GitHub Actions OIDC setup guide.
- `requirements.txt` - Python dependencies for CDK and project tooling.
- `application/requirements.txt` - runtime Python dependencies for the FastAPI service.

## What This Project Deploys

### Infrastructure

The CDK app can deploy the following resources when enabled in `config/sbx.yaml`:

- ECR repository for container images
- ECS cluster, task definition, and Fargate service
- ALB and target group
- Security groups for ECS and ALB
- Optional EKS cluster and node group
- IAM roles for ECS/EKS
- SSM parameters used by cross-stack references

### Application

The FastAPI application defines a simple health endpoint and a `/predict` endpoint.
The container image is built from `application/Dockerfile` and pushed to ECR.

## Prerequisites

- Python 3.11
- AWS CDK v2 installed (`aws-cdk-lib` and `constructs` dependencies)
- AWS credentials or GitHub OIDC role configured for AWS access
- `docker` installed locally for image builds

## Setup

1. Install project dependencies:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -r application/requirements.txt
```

2. Verify the config file `config/sbx.yaml` is correct for your target environment.

3. Confirm AWS region and resource names in `.github/workflows/deploy-app.yaml` if you are using GitHub Actions.

## CDK Infrastructure Deployment

The CDK app is driven from `app.py` and reads `config/sbx.yaml`.
If a stack is enabled, it will be created during `cdk synth` / `cdk deploy`.

### Example deploy command

```bash
cd /Users/mohdnadeem/projects/cloudserve-platform
cdk synth
cdk deploy --all
```

### Notes

- `config/sbx.yaml` controls which stacks are created.
- The ECS service is intentionally created with `desired_count: 0` in the current code to avoid ECS pull/retry deadlocks when the image does not yet exist.
- The ECR repository stack writes repository metadata to SSM parameters.
- The ECS task definition stack resolves the image URI via SSM at deployment time.

## Application Docker Build and Deployment

The app Docker build context is `application/` and the Dockerfile is `application/Dockerfile`.
The GitHub Actions workflow uses these values when building and pushing images.

### FastAPI app

- `application/main.py` contains the FastAPI service implementation.
- `application/requirements.txt` lists runtime dependencies.

## GitHub Actions Deployment Workflow

The workflow `.github/workflows/deploy-app.yaml` performs the following steps:

1. Checkout the `sbx` branch.
2. Authenticate to AWS using `aws-actions/configure-aws-credentials@v4`.
3. Login to ECR.
4. Check whether the image tag already exists in ECR.
5. Build and push the Docker image only if it does not already exist.
6. Download the existing ECS task definition.
7. Update the task definition with the new image.
8. Deploy the updated task definition to ECS.
9. Start the ECS service and wait for stability.

## Configuration

The config file `config/sbx.yaml` defines enabled stacks and environment values such as:

- `project_prefix`
- `vpc_id`
- `subnet_ids`
- `domain_name`
- stack enablement flags for `ecs`, `ecr`, `eks`, `iam`, `logs`, `networking`, and `alb`

## AWS OIDC Setup

For GitHub Actions deployment, use `GITHUB_AWS_DEPLOYMENT_GUIDE.md` to configure OIDC trust and role assumptions.
That guide includes the exact steps to create the IAM role, trust policy, GitHub secret, and workflow permissions.

## How to Use

1. Deploy infrastructure first, especially ECR and ECS foundation stacks.
2. Build and push the app image to ECR.
3. Deploy or update the ECS task definition and service.

## Notes

- The infrastructure code currently supports both ECS and EKS deployments, but only the stacks enabled in `config/sbx.yaml` will be created.
- The project is intended to be configurable, and for production use it should be secured with least-privilege IAM roles and proper subnet/VPC settings.
- The current build pipeline targets `us-east-1` and the `csp-sbx` project prefix.

## License

This project is available under the terms of the LICENSE file.
