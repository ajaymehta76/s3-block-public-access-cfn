## S3BlockPublicAccessCFN
CloudFormation custom resource to enable S3 Block Public access at the account level

Amazon S3 now supports ability to block public access at account level as well as the individual bucket level. With the new settings you have the ability to block existing public access (whether it was specified by an ACL or a policy) and to ensure that public access is not granted to newly created buckets and objects within it. At present CloudFormation supports enabling this feature at the individual bucket level but there isn't a built-in way in CloudFormation to do this at the account level.

For organizations that have multiple accounts, enabling these settings on each account manually could be tedious and time consuming. Having an automated way to do this via CloudFormation can help them manage these settings across many accounts with ease. 

The included CloudFormation template attempts to address this. It contains a custom resource lambda to enable the S3 Block Public Access feature at the account level. The Lambda function is implemented in Python3 and uses S3 Control API to enable the S3 Block public access settings in the account where the template is deployed. Currently boto3 library that the AWS Lambda container includes does not support the newly added S3Control resource and therefore the latest boto3 library needs to be packaged with the lambda codebase. This is done using Lambda Layer. In future when the Lambda python runtime is updated to include boto3 version 1.9.84 or later this can be removed. 

# Steps for Deploying cloudformation template
- Ensure you have the latest version of aws cli (On mac you can run pip install awscli --upgrade --user)
- Decide the bucket where you want to upload the boto3 library that is included as a lambda layer
- Run the following commands to package the template and deploy

aws cloudformation package --template-file ./S3BlockPublicAccess.yml --s3-bucket <S3_BUCKET_NAME> --output-template ./pkgd-cfn.json

aws cloudformation deploy --template-file ./pkgd-cfn.json --stack-name S3BlockPublicAccess --capabilities CAPABILITY_IAM

# Template Parameters
S3 Block Public access has four settings as below that each can be turned on/off via the cloudformation template. By default all four of these settings will be turned on if the stack is deployed with default settings.

- S3BlockPublicAcls : Block new public ACLs and uploading public objects 
- S3IgnorePublicAcls : Remove public access granted through public ACLs 
- S3BlockPublicPolicy : Block new public bucket policies 
- S3RestrictPublicBuckets: Block public and cross-account access to buckets that have public policies

More info about each of these settings can be found in S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html) as well as this [blog post](https://aws.amazon.com/blogs/aws/amazon-s3-block-public-access-another-layer-of-protection-for-your-accounts-and-buckets/) 
