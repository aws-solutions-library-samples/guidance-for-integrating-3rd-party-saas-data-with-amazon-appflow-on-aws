#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks, NagSuppressions

from appflow_solution.appflow_solution_stack_eventdriven import AppflowSolutionStackEventDriven
from appflow_solution.appflow_solution_stack_foundation import AppflowSolutionStackFoundation

app = cdk.App()
Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
appflow_solution_foundation = AppflowSolutionStackFoundation(app, "appflow-solution-foundation")
appflow_solution_eventdriven = AppflowSolutionStackEventDriven(app, "appflow-solution-eventdriven")

NagSuppressions.add_stack_suppressions(appflow_solution_foundation,
                                       [
                                           {"id": 'AwsSolutions-S1',
                                            "reason": 'provides read only access to Raw Bucket'},
                                           {"id": 'AwsSolutions-IAM5',
                                            "reason": 'Tables created by AppFlow'},
                                           {"id": 'AwsSolutions-IAM4',
                                            "reason": 'Using AWS managed policies'},
                                           {"id": 'AwsSolutions-ATH1',
                                            "reason": 'Athena is configured with SSE_S3 encryption'}
                                       ]
                                       )

NagSuppressions.add_stack_suppressions(appflow_solution_eventdriven,
                                       [
                                           {"id": 'AwsSolutions-IAM4',
                                            "reason": 'provides read only access to Raw Bucket'},
                                       ]
                                       )

app.synth()
