# Running the CDK

If you are new to deploying CDK, follow this guide to set up environment [CDK Setup](ConfigureCDKENV.md)
There are 2 CDK deployments in this app. The first is called `appflow-solution-foundation`,
and this is the foundation of what is needed to deploy this solution. The second stack is the `appflow-solution-eventdriven`


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

Here is the sample command to deploy this stack. Please replace the placeholder values with the names you want to provide:
- `RawBucketName`,`CuratedBucketName`, and `ResultsBucketName` names can consist only of lowercase letters, numbers, dots (.), and hyphens (-). Refer to [Bucket Naming Rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html?icmpid=docs_amazons3_console) for more information.
- `GlueDatabaseName` names can consist of lowercase letters, numbers, and the underscore character. Refer to [Database, table, and column names](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html#schema-names) for more information.
- `AthenaWGName` must be a unique name for your workgroup. Use 1 - 128 characters. (A-Z,a-z,0-9,_,-,.). This name cannot be changed. Refer to [Managing workgroups](https://docs.aws.amazon.com/athena/latest/ug/workgroups-create-update-delete.html#creating-workgroups) for more information.
```bash
cdk deploy appflow-solution-foundation \
--parameters RawBucketName= [ReplaceWithRawBucketName] \
--parameters CuratedBucketName= [ReplaceWithCuratedBucketName]\
--parameters ResultsBucketName=[ReplaceWithResultsBucketName] \
--parameters GlueDatabaseName=[ReplaceWithGlueDatabaseName] \
--parameters AthenaWGName=[ReplaceWithAthenaWGName]
```




