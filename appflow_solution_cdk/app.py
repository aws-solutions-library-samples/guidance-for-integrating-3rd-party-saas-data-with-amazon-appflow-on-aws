#!/usr/bin/env python3

import aws_cdk as cdk

from appflow_solution.appflow_solution_stack_foundation import AppflowSolutionStackFoundation
from appflow_solution.appflow_solution_stack_optional import AppflowSolutionStackOptional
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks,  NagSuppressions


app = cdk.App()
Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
appflow_solution_foundation = AppflowSolutionStackFoundation(app,"appflow-solution-foundation")
appflow_solution_optional=AppflowSolutionStackOptional(app,  "appflow-solution-optional")

NagSuppressions.add_stack_suppressions(appflow_solution_foundation, [{"id": 'AwsSolutions-IAM5',
                                                                     "appliesTo": ["Resource::<RawBucket0C3EE094.Arn>/*"],
                                                                      "reason": 'provides read only access to Raw Bucket'},
                                                                     {"id": 'AwsSolutions-IAM5',
                                                                      "appliesTo": ["Resource::arn:aws:glue:<AWS::Region>:<AWS::AccountId>:table/<GlueDatabaseName>/*"],
                                                                      "reason": 'Tables created by AppFlow'},
                                                                     {"id": 'AwsSolutions-IAM5',
                                                                      "appliesTo": ["Resource::<CuratedBucket6A59C97E.Arn>/*"],
                                                                      "reason": 'Ability to write to new bucket'},
                                                                     ])
NagSuppressions.add_stack_suppressions(appflow_solution_optional, [{"id": 'AwsSolutions-IAM4',
                                                                      "reason": 'provides read only access to Raw Bucket'},
                                                                     ])

app.synth()
