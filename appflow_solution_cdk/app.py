#!/usr/bin/env python3

import aws_cdk as cdk

from appflow_solution.appflow_solution_stack_eventdriven import AppflowSolutionStackEventDriven
from appflow_solution.appflow_solution_stack_foundation import AppflowSolutionStackFoundation

app = cdk.App()
AppflowSolutionStackFoundation(app, "appflow-solution-foundation")
AppflowSolutionStackEventDriven(app, "appflow-solution-eventdriven")

app.synth()