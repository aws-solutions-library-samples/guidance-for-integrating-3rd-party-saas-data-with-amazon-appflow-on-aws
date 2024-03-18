import uuid

import aws_cdk
from aws_cdk import (
    Stack,
    CfnParameter,
    aws_iam as iam,
    aws_s3 as s3,
    CfnOutput,
    aws_glue as glue,
    aws_athena as athena
)
from constructs import Construct


class AppflowSolutionStackFoundation(Stack):
    def __init__ (self, scope: Construct, construct_id: str,
                  RawBucketName,
                  CuratedBucketName,
                  ResultsBucketName,
                  GlueDatabaseName,
                  AthenaWGName,
                  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # parameters for Data Lake
        self.RawBucketName = RawBucketName
        self.CuratedBucketName = CuratedBucketName
        self.ResultsBucketName = ResultsBucketName
        self.GlueDatabaseName = GlueDatabaseName
        self.AthenaWGName = AthenaWGName

        # appflow_solutionslibrary_role
        appflow_solutionslibrary_role_name = CfnParameter(self, "AppflowSolutionslibraryRole",
                                                          default='appflow_solutionslibrary_role',
                                                          type="String",
                                                          description="Name of the role for AppFlow to access Glue Data Catalog")
        # glue_solutionslibrary_role
        glue_solutionslibrary_role_name = CfnParameter(self, "GlueSolutionslibraryRole",
                                                       default='glue_solutionslibrary_role',
                                                       type="String",
                                                       description="Name of the role for Glue to access Glue Data Catalog")

        # s3 buckets

        raw_bucket = s3.Bucket(self, "RawBucket",
                               bucket_name=self.RawBucketName,
                               enforce_ssl=True,
                               encryption=s3.BucketEncryption.S3_MANAGED,
                               block_public_access=s3.BlockPublicAccess.BLOCK_ALL)
        curated_bucket = s3.Bucket(self, "CuratedBucket",
                                   bucket_name=self.CuratedBucketName,
                                   enforce_ssl=True, encryption=s3.BucketEncryption.S3_MANAGED,
                                   block_public_access=s3.BlockPublicAccess.BLOCK_ALL)
        results_bucket = s3.Bucket(self, "ResultsBucket",
                                   bucket_name=self.ResultsBucketName,
                                   enforce_ssl=True,
                                   encryption=s3.BucketEncryption.S3_MANAGED,
                                   block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

        # Glue Database
        glue_db = glue.CfnDatabase(self, "GlueAppFlowDB",
                                   catalog_id=aws_cdk.Aws.ACCOUNT_ID,
                                   database_input=glue.CfnDatabase.DatabaseInputProperty(
                                       name=self.GlueDatabaseName))
        # IAM
        appflow_s3_policy = iam.Policy(self, "appflow_s3_policy",
                                       statements=[
                                           iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                                               actions=[
                                                                   "s3:PutObject",
                                                                   "s3:AbortMultipartUpload",
                                                                   "s3:ListMultipartUploadParts",
                                                                   "s3:ListBucketMultipartUploads",
                                                                   "s3:GetBucketAcl",
                                                                   "s3:PutObjectAcl"
                                                               ],
                                                               resources=[
                                                                   f'{raw_bucket.bucket_arn}/*',
                                                                   raw_bucket.bucket_arn
                                                               ]
                                                               )
                                       ]
                                       )
        appflow_glue_policy = iam.Policy(self, "appflow_glue_policy",
                                         statements=[iam.PolicyStatement(effect=iam.Effect.ALLOW, actions=[
                                             "glue:BatchCreatePartition",
                                             "glue:CreatePartitionIndex",
                                             "glue:DeleteDatabase",
                                             "glue:GetTableVersions",
                                             "glue:GetPartitions",
                                             "glue:BatchDeletePartition",
                                             "glue:DeleteTableVersion",
                                             "glue:UpdateTable",
                                             "glue:DeleteTable",
                                             "glue:DeletePartitionIndex",
                                             "glue:GetTableVersion",
                                             "glue:CreatePartition",
                                             "glue:UntagResource",
                                             "glue:UpdatePartition",
                                             "glue:TagResource",
                                             "glue:UpdateDatabase",
                                             "glue:CreateTable",
                                             "glue:BatchUpdatePartition",
                                             "glue:GetTables",
                                             "glue:BatchGetPartition",
                                             "glue:GetDatabases",
                                             "glue:GetPartitionIndexes",
                                             "glue:GetTable",
                                             "glue:GetDatabase",
                                             "glue:GetPartition",
                                             "glue:CreateDatabase",
                                             "glue:BatchDeleteTableVersion",
                                             "glue:BatchDeleteTable",
                                             "glue:DeletePartition"
                                         ], resources=[
                                             f'arn:aws:glue:{aws_cdk.Aws.REGION}:{aws_cdk.Aws.ACCOUNT_ID}:table/{glue_db.database_input.name}/*',
                                             f'arn:aws:glue:{aws_cdk.Aws.REGION}:{aws_cdk.Aws.ACCOUNT_ID}:database/{glue_db.database_input.name}',
                                             f'arn:aws:glue:{aws_cdk.Aws.REGION}:{aws_cdk.Aws.ACCOUNT_ID}:catalog']
                                                                         )
                                                     ]
                                         )
        appflow_role = iam.Role(self, "appflow_solutionslibrary_role",
                                assumed_by=iam.ServicePrincipal("appflow.amazonaws.com"),
                                role_name=appflow_solutionslibrary_role_name.value_as_string
                                )
        appflow_role.attach_inline_policy(appflow_s3_policy)
        appflow_role.attach_inline_policy(appflow_glue_policy)
        athena_wg = athena.CfnWorkGroup(self, "appflow_workgroup",
                                        name=self.AthenaWGName,
                                        description='Workgroup for Athena queries',
                                        work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                                            result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                                                output_location=f's3://{results_bucket.bucket_name}/results/',
                                                encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                                                    encryption_option='SSE_S3'
                                                ),
                                            )
                                        )
                                        )

        # create glue iam policy to read from s3
        glue_policy = iam.Policy(self, "gluejob_solution_policy",
                                 statements=[iam.PolicyStatement(effect=iam.Effect.ALLOW, actions=[
                                     "s3:GetObject",
                                     "s3:ListObject",
                                     "s3:GetObjectVersion"
                                 ], resources=[
                                     f'{raw_bucket.bucket_arn}/*',
                                     raw_bucket.bucket_arn])]
                                 )
        glue_policy.add_statements(iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                                       actions=[
                                                           "s3:GetObject",
                                                           "s3:ListObject",
                                                           "s3:GetObjectVersion",
                                                           "s3:PutObject"
                                                       ],
                                                       resources=[
                                                           f'{curated_bucket.bucket_arn}/*']
                                                       )
                                   )

        glue_role = iam.Role(self, "glue_solutionslibrary_role",
                             assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
                             role_name=glue_solutionslibrary_role_name.value_as_string,
                             description="Role uses the Glue Service role for baseline glue permissions. Add inline policy developed to "
                                         "provide Read only access to Raw Bucket, and read and write permissions into the curated bucket."
                             )

        glue_role.add_managed_policy(
            policy=iam.ManagedPolicy.from_managed_policy_arn(self, id='glueServiceRole',
                                                             managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'
                                                             )
        )
        glue_role.attach_inline_policy(glue_policy)
        # outputs
        CfnOutput(self, "appflow_role_name",
                  value=appflow_role.role_name,
                  description="Name of role to be used when configuring AppFlow Flow.")
        CfnOutput(self, "glue_role_name",
                  value=glue_role.role_name,
                  description="Name of role for AWS Glue to use for read Only access")
        CfnOutput(self, "raw_bucket_name",
                  value=raw_bucket.bucket_name,
                  description="Name of raw bucket created")
        CfnOutput(self, "curated_bucket_name",
                  value=curated_bucket.bucket_name,
                  description="Name of curated bucket created")
        CfnOutput(self, "results_bucket_name",
                  value=results_bucket.bucket_name,
                  description="Name of results bucket created")
        CfnOutput(self, "glue_db_name",
                  value=glue_db.database_input.name,
                  description="Name of Glue database")
        CfnOutput(self, "athena_wg_name",
                  value=athena_wg.name,
                  description="Name of Athena workgroup")
