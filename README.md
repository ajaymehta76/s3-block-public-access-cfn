## S3BlockPublicAccessCFN
CloudFormation custom resource to enable S3 Block Public access at the account level

Amazon S3 now supports ability to block public access at account level as well as the individual bucket level. With the new settings you have the ability to block existing public access (whether it was specified by an ACL or a policy) and to ensure that public access is not granted to newly created buckets and objects within it. At present CloudFormation supports enabling this feature at the individual bucket level but there isn't a built-in way in CloudFormation to do this at the account level.

The included CloudFormation template contains a custom resource lambda to enable the S3 Block Public Access feature at the account level. The Lambda function is implemented in Python3 and uses S3 Control API to enable the S3 Block public access settings in the account where the template is deployed. Currently boto3 library that Lambda container includes does not support the newly added S3Control resource and therefore the latest boto3 library needs to be packaged with the lambda codebase. In future when Lambda python runtime is updated to include boto3 version 1.9.84 or later this can be removed. 

# Steps for Deploying cloudformation template
- Decide the bucket where you want to upload the lambda function code base 
- Run the following commands to package the template and deploy

aws cloudformation package --template-file ./S3BlockPublicAccessCFN.yml --s3-bucket <S3_BUCKET_NAME> --output-template ./pkgd-cfn.yml

aws cloudformation deploy --template-file ./pkgd-cfn.yml --stack-name S3BucketBlockPublicAccess --capabilities CAPABILITY_IAM
