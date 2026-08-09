from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct

class ALBStack(Stack):
    def __init__(
        self, 
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        vpc_id: str,
        subnet_ids: list[str],
        alb_security_group: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.alb = elbv2.CfnLoadBalancer(
            self,
            "ALB",
            name=f"{project_prefix}-alb",
            subnets=subnet_ids,
            security_groups=[alb_security_group.ref],
            scheme="internet-facing",
            type="application",
            ip_address_type="ipv4"
        )

        self.target_group = elbv2.CfnTargetGroup(
            self,
            "ALBTargetGroup",
            name=f"{project_prefix}-alb-tg",
            port=8000,
            protocol="HTTP",
            vpc_id=vpc_id,
            target_type="ip",
            health_check_protocol="HTTP",
            health_check_path="/",
            health_check_port="8000",
            health_check_interval_seconds=30,
            health_check_timeout_seconds=5,
            healthy_threshold_count=2,
            unhealthy_threshold_count=3,
            matcher=elbv2.CfnTargetGroup.MatcherProperty(
                http_code="200"
            )
        )

        self.listener = elbv2.CfnListener(
            self,
            "ALBHTTPListener",
            load_balancer_arn=self.alb.ref,
            port=80,
            protocol="HTTP",
            default_actions=[elbv2.CfnListener.ActionProperty(
                type="forward",
                forward_config=elbv2.CfnListener.ForwardConfigProperty(
                    target_groups=[elbv2.CfnListener.TargetGroupTupleProperty(
                        target_group_arn=self.target_group.ref,
                        weight=1
                    )]
                )
            )]
        )

        # self.https_listener = elbv2.CfnListener(
        #     self,
        #     "ALBHTTPSListener",
        #     load_balancer_arn=self.alb.ref,
        #     port=443,
        #     protocol="HTTPS",
        #     certificates=[
        #         elbv2.CfnListener.CertificateProperty(
        #             certificate_arn=ssm.StringParameter.value_for_string_parameter(
        #                 self,
        #                 f"/{project_prefix}/acm/certificate-arn"
        #             )
        #         )
        #     ],
        #     default_actions=[
        #         elbv2.CfnListener.ActionProperty(
        #             type="forward",
        #             forward_config=elbv2.CfnListener.ForwardConfigProperty(
        #                 target_groups=[
        #                     elbv2.CfnListener.TargetGroupTupleProperty(
        #                         target_group_arn=self.target_group.ref,
        #                         weight=1
        #                     )
        #                 ]
        #             )
        #         )
        #     ]
        # )

        # -----------------------------
        # SSM Parameters
        # -----------------------------
        ssm.StringParameter(
            self,
            "ALBArnParameter",
            parameter_name=f"/{project_prefix}/alb/arn",
            string_value=self.alb.ref,
        )

        ssm.StringParameter(
            self,
            "TargetGroupArnParameter",
            parameter_name=f"/{project_prefix}/alb/target-group-arn",
            string_value=self.target_group.ref,
        )

        ssm.StringParameter(
            self,
            "ALBDnsNameParameter",
            parameter_name=f"/{project_prefix}/alb/dns-name",
            string_value=self.alb.attr_dns_name,
        )
        