#!/usr/bin/env python3

import aws_cdk as cdk

from appflow_solution.appflow_solution_stack_foundation import AppflowSolutionStackFoundation
from appflow_solution.appflow_solution_stack_optional import AppflowSolutionStackOptional


app = cdk.App()
# AppflowSolutionStack(app, "appflow-solution")
AppflowSolutionStackFoundation(app,  "appflow-solution-foundation")
AppflowSolutionStackOptional(app,  "appflow-solution-optional")
app.synth()
