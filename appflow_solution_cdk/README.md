# Running the CDK

If you are new to deploying CDK, follow this guide to set up environment [CDK Setup](ConfigureCDKENV.md)
There are 2 CDK deployments in this app. The first is called `appflow-solution-foundation`,
and this is the foundation of what is needed to deploy this solution.  
The second stack is the `appflow-solution-eventdriven`. This stack is optional if you choose to trigger the AWS Glue job to start after there are new records transferred into Amazon S3.

##  Deploy `appflow-solution-foundation` stack
The CDK stack will create the following resources that are needed for creating an AppFlow Flow:
- Amazon S3 Bucket:
  - `RawBucket` bucket where raw data from AppFlow will land.
  - `ResultsBucket` bucket where the athena query will store query results.
  - `CuratedBucket` bucket where transformed data will be stored.
- IAM Policy:
  - `appflow_s3_solutionslibrary_policy` is based off this guide: [Amazon S3 Bucket Policies for Amazon AppFlow](https://docs.aws.amazon.com/appflow/latest/userguide/s3-policies-management.html)
  - `appflow_glue_solutionslibrary_policy` is based on this guide: [Allow Amazon AppFlow to access the AWS Glue Data Catalog](https://docs.aws.amazon.com/appflow/latest/userguide/security_iam_id-based-policy-examples.html#security_iam_id-based-policy-examples-access-gdc)
- Glue Database:
  - `GlueAppFlowDB` database will serve as the
- IAM Role:
  - `appflow_solutionslibrary_role` is an AppFlow service role that attaches `appflow_s3_solutionslibrary_policy` and `appflow_glue_solutionslibrary_policy` and includes a trust policy based on this guide: [Service role policies for Amazon AppFlow](https://docs.aws.amazon.com/appflow/latest/userguide/security_iam_service-role-policies.html#access-gdc)
- Athena Workgroup:
  -  `appflow_workgroup` workgroup is configured to write results into `ResultsBucket`

Here is a sample command to deploy this stack with all the default parameters:
```Shell
cdk deploy appflow-solution-foundation
```
***If you want to customize the parameters, you can change the default parameters in the [app.py](app.py) file in the `AppflowSolutionStackFoundation` class inputs.***

Outputs will be displayed in [CloudFormation](https://console.aws.amazon.com/cloudformation/home). This stack will be named `appflow-solution-foundation`. Click on outputs, and this will provide you the names that were generated for the AppFlow Role.

<img src="imgs/cf_outputs_foundation.png" alt="image" width="800" height="auto">

##  Deploy `appflow-solution-eventdriven` stack *Optional*
This is an optional stack to deploy an EventBridge Rule that will trigger an
AWS Lambda function to run the AWS Glue Job whenever the AppFlow finishes running and pulls data from the source.

Pre-requisite:
- Create an AppFlow Flow to transfer data from your connected SaaS, into your Amazon S3 Raw Bucket.
- Create an AWS Glue Job that would need to run after each Flow run
The CDK stack will create the following resources for event driven architecture:
- AWS Lambda
  -  `appflow_lambda_function` will create a Python Runtime Environment. Here is the [Python Code](lambda_function/invokeGlue.py)
  -  The name of the Glue Job is passed through environment variables, and `boto3` will execute the [start_job_run](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/start_job_run.html) API.
  - A IAM Role will be created granting `appflow_lambda_function` permissions to `glue:StartJobRun` only to the Glue Job that is specified.
- Amazon EventBridge Rule
  - `appflow_eventbridge_rule` will trigger `appflow_lambda_function` to run whenever the AppFlow End Flow Run Report shows that the number of records processed is not 0.

Here is the sample command to deploy this stack. There are no default parameters, so please replace the placeholder values with the names of your Flow name and Glue Job name:
- `gluejobname` is the name of the job you created. You can find this in the AWS Console by going to [AWS Glue](https://console.aws.amazon.com/glue/home), then clicking ETL jobs.
- `flowname` is the name of the AppFlow Flow that was created to pull data from your SaaS into AWS. You can find this in the AWS Console by going to [Amazon AppFlow](https://console.aws.amazon.com/appflow/home), then clicking on Flows.
```Shell
cdk deploy appflow-solution-eventdriven \
--parameters gluejobname=[ReplaceWithNameofGlueJob] \
--parameters flowname=[ReplaceWithNameofFlow]
```
Now, anytime you run your AppFlow Flow, it will automatically trigger the Lambda Function to run the Glue job. Here are the outputs of

<img src="imgs/cf_outputs_eventdriven.png" alt="image" width="800" height="auto">
