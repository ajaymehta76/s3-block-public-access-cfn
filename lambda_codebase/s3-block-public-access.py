import logging
import sys
import os
import ast
## Currently lambda python environment does not support the latest boto3 library
## with s3control resource so need to package the boto3 library with lambda and use that
envLambdaTaskRoot = os.environ["LAMBDA_TASK_ROOT"]
print("LAMBDA_TASK_ROOT env var:"+os.environ["LAMBDA_TASK_ROOT"])
print("sys.path:"+str(sys.path))

sys.path.insert(0,envLambdaTaskRoot+"/boto3_1.9.84")
print("sys.path:"+str(sys.path))

import botocore
import boto3
import json
from botocore.vendored import requests

def lambda_handler(event, context):
    setup_logger()
    log.info(json.dumps(event))
    response_data = {}
    requestType = event['RequestType']

    if requestType != 'Create' and requestType != 'Update' and requestType != 'Delete':
        send(event, context, 'SUCCESS', response_data)
        exit(0)

    s3control_client = boto3.client('s3control')
    accountId = event['ResourceProperties']['AccountId']

    if requestType == 'Delete':
        try:
          log.info("Deleting S3 Block Public Access for account: " + accountId)
          response = s3control_client.delete_public_access_block(
                AccountId = accountId)
          log.info("Done deleting S3 Block Public Access settings")
          exit(0)
        except Exception as e:
          log.error("Error configuring S3 Blcok Public Access settings")
          do_err(e,event, context)

    else: # create/update scenario
        blockPublicAcls = ast.literal_eval(event["ResourceProperties"]['S3BlockPublicAcls'])
        ignorePublicAcls = ast.literal_eval(event["ResourceProperties"]['S3IgnorePublicAcls'])
        blockPublicPolicy = ast.literal_eval(event["ResourceProperties"]['S3BlockPublicPolicy'])
        restrictPublicBuckets = ast.literal_eval(event["ResourceProperties"]['S3RestrictPublicBuckets'])

        try:
          log.info("Configuring S3 Block Public Access for account: " + accountId)
          log.info("BlockPublicAcls: " + str(blockPublicAcls) + "\n" +
                    "IgnorePublicAcls: " + str(ignorePublicAcls) + "\n" +
                    "BlockPublicPolicy: " + str(blockPublicPolicy) + "\n" +
                    "RestrictPublicBuckets: " + str(restrictPublicBuckets))
          response = s3control_client.put_public_access_block(
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': blockPublicAcls,
                    'IgnorePublicAcls': ignorePublicAcls,
                    'BlockPublicPolicy': blockPublicPolicy,
                    'RestrictPublicBuckets': restrictPublicBuckets
                },
                AccountId=accountId
            )
          log.info("Done configuring S3 Block Public Access settings")
        except Exception as e:
          log.error("Error configuring S3 Block Public Access settings")
          do_err(e,event, context)

    # Send response to CloudFormation
    send(event, context, 'SUCCESS', response_data)

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))

def setup_logger():
    global log
    log = logging.getLogger()
    log_levels = {'INFO': 20, 'WARNING': 30, 'ERROR': 40}
    log.setLevel(log_levels['INFO'])

def do_err(e, event, context):
    log.error(e)
    response_data = {}
    send(event, context, 'FAILED', response_data)
    exit(1)
