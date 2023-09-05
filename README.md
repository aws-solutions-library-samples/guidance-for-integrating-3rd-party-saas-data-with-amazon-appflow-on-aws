
# Guidance for Integrating 3rd Party SaaS Data with Amazon AppFlow

Welcome to Guidance for Integrating 3rd Party SaaS Data with Amazon AppFlow!
## Overview
Customers work with a variety of SaaS providers that keep their data in silos. By using AppFlow to retrieve data, customers are able to quickly, and easily pull and catalog the data to a central data lake in S3. Once data is in S3, customers would be able to prepare data for machine learning, cleans the data, or load it into a Redshift DW.

In this guidance, we are going to deploy the necessary resources to sync data from Salesforce, and load it into Amazon S3. 
Athena will serve as the querying engine to load data into Amazon QuickSight.

There is going to be an optional stack deployment that will enable you to run your AWS Glue ETL job based on AppFlow End Flow Run Report results in EventEngine.

## Solution Architecture for Integrating 3rd Party SaaS Data with Amazon AppFlow

![reference_architecture.png](reference_architecture.png)

## Prerequisites
For being able to follow this solution, you will need:  
- An AWS account with sufficient permissions to deploy this solution.
- Supported SaaS application, such as Salesforce or ServiceNow, from the [AppFlow supported applications](https://docs.aws.amazon.com/appflow/latest/userguide/app-specific.html). 
- Meet the requirements specific to your application. Please find and review the requirements for your application [here](https://docs.aws.amazon.com/appflow/latest/userguide/app-specific.html).

## Deploying Solution
In this guidance, we are going to import Salesforce opportunities into S3 as they are created, and create a pipeline to transform the dataset and make it avaiable to import into QuickSight.

### **Step 1** Deploying CloudFormation Template or CDK stack
There are 2 ways that you can deploy the foundational resources.
- The first method is using uploading this CF template [appflow_solution_library_foundation_cf.json](appflow_solution_library_foundation_cf.json),  
into the [CloudFormation Console](https://console.aws.amazon.com/cloudformation).  
- The second method is to use  the [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)(CDK).
The code and instructions to deploy this solution with CDK can be found in the [AppFlow Solution CDK](appflow_solution_cdk) directory.

This guide will focus on using CloudFormation to deploy all resources.  
The CloudFormation template will create the following resources that are needed for creating an AppFlow Flow:
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

Fill in the parameter fields:
- `RawBucketName`,`CuratedBucketName`, and `ResultsBucketName` names can consist only of lowercase letters, numbers, dots (.), and hyphens (-). Refer to [Bucket Naming Rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html?icmpid=docs_amazons3_console) for more information.
- `GlueDatabaseName` names can consist of lowercase letters, numbers, and the underscore character. Refer to [Database, table, and column names](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html#schema-names) for more information.
- `AthenaWGName` must be a unique name for your workgroup. Use 1 - 128 characters. (A-Z,a-z,0-9,_,-,.). This name cannot be changed. Refer to [Managing workgroups](https://docs.aws.amazon.com/athena/latest/ug/workgroups-create-update-delete.html#creating-workgroups) for more information.

### **Step 2** Set up AppFlow Connector
Next step is to create a connection profile to connect Salesforce to AppFlow. For Connecting Salesforce to AppFlow, detailed instructions could be found here: [Connecting Amazon AppFlow to your Salesforce account](https://docs.aws.amazon.com/appflow/latest/userguide/salesforce.html). If you are using a service other than Salesforce, you can find your supported application [here](https://docs.aws.amazon.com/appflow/latest/userguide/app-specific.html). Follow the instructions for your respective application, and the connection will provide you access 
[Manage Connections](https://console.aws.amazon.com/appflow/home#/connections)

### **Step 3** Set up AppFlow Flow
Once an AppFlow Connection Profile is created, create a Flow by going to [Amazon AppFlow](https://console.aws.amazon.com/appflow/home), then clicking Flows and `Create Flow`.
Follow this guide, [Create a flow using the AWS console](https://docs.aws.amazon.com/appflow/latest/userguide/create-flow-console.html), on configuring your Flow. Be sure to use the `RawBucket` that was created in Step 1 as your destination,  
and use the AppFlow Glue Policy
### **Step 4** Enrich data using AWS Glue
Crete an AWS Glue Job. In the outputs of the CloudFormation Template, there will be a Role Service Role created that will allow your Glue job Read only access into resources in your Raw Data Bucket, and read and write permissions into your Curated_Data bucket.

### **Step 5** Create Trigger to run AWS Glue Job ***(Optional)***
This step is optional. This step will create resources for automating your data pipeline and having it be event driven to trigger based on the results of the AppFlow End Flow Run Report.
By deploying the [appflow_solution_library_eventdriven_cf.json](appflow_solution_library_eventdriven_cf.json) template, this will deploy an EventBridge Rule that will trigger an AWS Lambda function to run the AWS Glue Job whenever the AppFlow finishes running and pulls data from the source.

#### Pre-requisites:
- Create an AppFlow Flow that you want to monitor
- Create an AWS Glue Job that runs successfully, and you want to run automatically

#### Deploy CloudFormation Template
 Once you have created the pre-requisite resources, you will need to get the names of the resources and enter this information into the Parameters of the CloudFormation template.
- `gluejobname` is the name of the AWS Glue job you want to run automatically. You can find this in the AWS Console by going to [AWS Glue](https://console.aws.amazon.com/glue/home), then clicking ETL jobs.
- `flowname` is the name of the AppFlow Flow that was created to pull data from your SaaS into AWS. This is the Flow you want to monitor and serve as your trigger to run the AWS Glue Job. You can find this in the AWS Console by going to [Amazon AppFlow](https://console.aws.amazon.com/appflow/home), then clicking on Flows.

Finish Deploying the CloudFormation Template, and all the resources will be provisioned and run when your flow finishes running.

### **Step 5** Query data with Athena
A WorkGroup was created in Amazon Athena that has been pre-configured to store query results in `ResultsBucket`. To query the data that has been imported into your AWS Environment, you can query the Raw Data, or you can Query the data that has been transformed and stored in your `CuratedBucket`

### **Step 6** Connect Athena to QuickSight ***(Optional)***
This may incur a recurring monthly charge since QuickSight is a subscription and is charged per user. Only proceed if you accept the charges, or already have a QuickSight active account.
- Follow this guide, [Signing up for an Amazon QuickSight subscription](https://docs.aws.amazon.com/quicksight/latest/user/signing-up.html), if you want to sign up for QuickSight.
- Subscribe to QuickSight
- Create Dataset
- Generate visualization

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

