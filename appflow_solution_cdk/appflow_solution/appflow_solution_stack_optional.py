from constructs import Construct
import aws_cdk
from aws_cdk import (
    Stack,
    CfnParameter,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_
)
import os
class AppflowSolutionStackOptional(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create a lambda function with a python runtime
        cfn_parameter_glue_job_name = CfnParameter(self, "glue_job_name",
                                                   type="String",
                                                   description="Glue Job Name")
        cfn_parameter_flow_name = CfnParameter(self, "flow_name",
                                               type="String",
                                               description="flow name")
        invokeGlue = lambda_.Function(self, "appflow_lambda_function",
                                      # function_name="InvokeGlue",
                                      runtime=lambda_.Runtime.PYTHON_3_9,
                                      handler="invokeGlue.lambda_handler",
                                      code=lambda_.Code.from_asset(os.path.abspath(
                                          os.path.join(os.curdir, 'lambda_function'))),
                                      environment={"glue_job_name": cfn_parameter_glue_job_name.value_as_string})
        # create a rule to trigger lambda function on
        eventbridge_rule = events.Rule(self, "appflow_eventbridge_rule",
                                       rule_name='test',
                                       event_pattern=events.EventPattern(source=["aws.appflow"],
                                                                         detail_type=[
                                                                             "AppFlow End Flow Run Report"],
                                                                         detail={"flow-name": [cfn_parameter_flow_name.value_as_string],
                                                                                 "num-of-records-processed": [{"anything-but": ["0"]}],
                                                                                 "status": ["Execution Successful"]
                                                                                 }
                                                                         )
                                       )
        invokeGlue.add_to_role_policy(iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                                          actions=[
                                                              "glue:StartJobRun"
                                                          ],
                                                          resources=[
                                                              f"arn:aws:glue:{aws_cdk.Aws.REGION}:{aws_cdk.Aws.ACCOUNT_ID}:job/{cfn_parameter_glue_job_name.value_as_string}"],
                                                          conditions=None))
        eventbridge_rule.add_target(targets.LambdaFunction(invokeGlue))
