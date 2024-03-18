#!/usr/bin/env python3

import aws_cdk as cdk

from appflow_solution.appflow_solution_stack_eventdriven import AppflowSolutionStackEventDriven
from appflow_solution.appflow_solution_stack_foundation import AppflowSolutionStackFoundation

app = cdk.App()
AppflowSolutionStackFoundation(app, "appflow-solution-foundation",
                               RawBucketName="appflow-solution-raw-{}".format(cdk.Aws.ACCOUNT_ID), # Bucket names can consist only of lowercase letters, numbers, dots, and hyphens
                               CuratedBucketName="appflow-solution-curated-{}".format(cdk.Aws.ACCOUNT_ID), # Bucket names can consist only of lowercase letters, numbers, dots, and hyphens
                               ResultsBucketName="appflow-solution-results-{}".format(cdk.Aws.ACCOUNT_ID), # Bucket names can consist only of lowercase letters, numbers, dots, and hyphens
                               GlueDatabaseName='appflowsolution_db', # Name of the Glue Database
                               AthenaWGName='appflowsolution_wg', # Name of the Athena Workgroup
                               description="Infrastructure for AppFlow Solution (SO9285)")

AppflowSolutionStackEventDriven(app, "appflow-solution-eventdriven",
                                description="Infrastructure for AppFlow Solution (SO9285)")

app.synth()
