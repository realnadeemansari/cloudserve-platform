# EKS IAM Access Entry and AWS Load Balancer Controller Setup

This guide shows how to grant an AWS IAM user access to your EKS cluster and the prerequisites for installing the AWS Load Balancer Controller.

## 1. Confirm AWS CLI access

Verify your AWS credentials are valid and point to the correct account:

```bash
aws sts get-caller-identity
```

Expected output should include your IAM user ARN:

```json
{
  "UserId": "AIDAVYEOLY5EFDSJKNCJK",
  "Account": "1234567890",
  "Arn": "arn:aws:iam::1234567890:user/nadeem_iam_user"
}
```

## 2. Update kubeconfig for the EKS cluster

Create or refresh the kubeconfig entry for the cluster:

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name csp-sbx-eks-cluster
```

This adds a new context to `~/.kube/config`.

## 3. Grant user access to the EKS cluster

If your cluster is using `CONFIG_MAP` authentication mode, you need to create an EKS access entry for your IAM user and then associate the admin access policy.

### 3.1 Create an EKS access entry

```bash
aws eks create-access-entry \
  --cluster-name csp-sbx-eks-cluster \
  --region us-east-1 \
  --principal-arn arn:aws:iam::1234567890:user/nadeem_iam_user \
  --type STANDARD
```

This creates a cluster access entry for the IAM user.

### 3.2 Associate admin policy with the user

```bash
aws eks associate-access-policy \
  --cluster-name csp-sbx-eks-cluster \
  --region us-east-1 \
  --principal-arn arn:aws:iam::1234567890:user/nadeem_iam_user \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --access-scope type=cluster
```

This associates the cluster admin policy with your user for this EKS cluster.

## 4. Verify cluster access

After creating the access entry and associating the policy, refresh kubeconfig again:

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name csp-sbx-eks-cluster
```

Then check cluster nodes:

```bash
kubectl get nodes
```

If no nodes appear, confirm your EKS node group is active and has worker nodes:

```bash
kubectl get pods -n kube-system
```

If `coredns` or other system pods are pending, that usually means nodes are not ready yet or the node group has not joined the cluster.

## 5. Prerequisites for AWS Load Balancer Controller

Before installing the AWS Load Balancer Controller, confirm the following:

- `kubectl` is installed and configured for the EKS cluster.
- `helm` is installed on your local machine.
- Your cluster has OIDC provider enabled and the controller service account has the proper IAM role.
- Your cluster is ready and the node group is available.

### 5.1 Install or verify Helm

```bash
helm version
```

### 5.2 Add the EKS charts repo

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
```

### 5.3 Create the controller service account

Create the Kubernetes service account before installing the Helm chart:

```bash
kubectl create serviceaccount aws-load-balancer-controller \
  -n kube-system
```

### 5.4 Install the AWS Load Balancer Controller

If you already created a service account and IAM role for the controller, install it with:

```bash
helm install aws-load-balancer-controller \
  eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=csp-sbx-eks-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

If you have not created the service account yet, use the AWS documentation flow to create the IAM role for service account (IRSA) first.

## 6. Common troubleshooting

- If `kubectl get nodes` returns `No resources found`, the cluster is active but the node group has not registered nodes yet.
- If `kubectl` returns `the server has asked for the client to provide credentials`, your kubeconfig may not be using the correct AWS credentials or the IAM user is not properly authorized.
- If `coredns` pods remain `Pending`, there are either no ready nodes or the worker nodes cannot join due to networking or IAM configuration.

## 7. Recommended next steps

1. Confirm the EKS node group desired count is greater than `0`.
2. Confirm the node group is healthy in the EKS console.
3. Confirm the IAM user has cluster access entry and admin policy association.
4. Re-run `aws eks update-kubeconfig` and retry `kubectl get nodes`.
5. Install the AWS Load Balancer Controller after the cluster and node group are healthy.
