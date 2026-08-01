# GitHub to AWS Deployment Guide

This file documents the GitHub Actions + AWS OIDC setup for deploying the CloudServe Platform without storing long-lived AWS access keys in GitHub.

## 1. Create GitHub OIDC Identity Provider

Go to:

IAM → Identity providers → Add provider

Choose:

- Provider type: OpenID Connect
- Provider URL: https://token.actions.githubusercontent.com
- Audience: sts.amazonaws.com

Click Add Provider.

## 2. Create IAM Role

Go to:

IAM → Roles → Create role

Select:

- Trusted entity: Web Identity
- Identity Provider: token.actions.githubusercontent.com
- Audience: sts.amazonaws.com

Click Next.

Role name:

- cloudserve-platform-github-actions-role

## 3. Replace the Trust Policy

After creating the role, open Trust Relationships and replace the policy with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": [
            "repo:<GITHUB_USERNAME>/<REPOSITORY>:ref:refs/heads/main"
          ]
        }
      }
    }
  ]
}
```

Replace:

- <ACCOUNT_ID> with 1234567890
- <GITHUB_USERNAME> with your GitHub username
- <REPOSITORY></repository> with cloudserve-platform

Example:

```json
"repo:mohdnadeem/cloudserve-platform:ref:refs/heads/main"
```

Only the main branch will be allowed to assume this role.

## 4. Attach Permissions

For learning and initial setup, attach:

- AdministratorAccess

Later, this should be replaced with least-privilege permissions.

## 5. Save the Role ARN

Example:

```text
arn:aws:iam::1234567890:role/cloudserve-platform-github-actions-role
```

## 6. Create GitHub Secret

In GitHub:

Repository → Settings → Secrets and variables → Actions → New repository secret

Name:

- AWS_ROLE_ARN

Value:

- arn:aws:iam::123456789:role/cloudserve-platform-github-actions-role

Do not store AWS access keys or secret keys.

## 7. Grant GitHub Permission to Request OIDC Tokens

Add this to the top of your workflow:

```yaml
permissions:
  id-token: write
  contents: read
```

Without this, GitHub cannot request an OIDC token.

## 8. Configure AWS Credentials

Use the official GitHub Action:

```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: us-east-1
```

This action will:

1. Ask GitHub for an OIDC token
2. Exchange it with AWS STS
3. Assume the IAM role
4. Export temporary AWS credentials

## 9. Verify Authentication

Add:

```yaml
- name: Verify AWS Identity
  run: aws sts get-caller-identity
```

Expected output includes an AWS account ID and a role ARN similar to:

```json
{
  "Account": "1234567890",
  "Arn": "arn:aws:sts::1234567890:assumed-role/cloudserve-platform-github-actions-role/GitHubActions",
  "UserId": "..."
}
```

## 10. Example GitHub Actions Workflow

```yaml
name: Deploy

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - run: aws sts get-caller-identity

      - run: pip install -r requirements.txt

      - run: cdk deploy --all --require-approval never
```

This is the standard production approach for CI/CD because it avoids storing permanent AWS credentials in GitHub.
