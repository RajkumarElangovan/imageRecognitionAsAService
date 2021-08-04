import boto3
import botocore.exceptions as ex
from flask import json
import json
from time import sleep

# objects to represent the SQS queue
sqs_client = boto3.client('sqs', region_name="us-east-1")

# create the queue based on queue name if it does not exist and return the queueUrl
def createQueue(queueName):
    try:
        response = sqs_client.create_queue(QueueName=queueName, Attributes={"DelaySeconds": "0", "VisibilityTimeout": "60"})
    except ex.ClientError as err:
        if err.response['Error']['Code'] == 'QueueNameExists':
            return sqs_client.get_queue_url(QueueName=queueName)
        else:
            return "Queue deleted"
    sleep(1)
    queue_url = response['QueueUrl']

def getQueueUrl(queueName):
    try:
        queue_url = sqs_client.get_queue_url(QueueName=queueName)
        return queue_url['QueueUrl']
    except ex.ClientError as err:
        if err.response['Error']['Code'] == 'QueueDoesNotExist':
            return createQueue(queueName)


# Enqueue the image name into the queue
def putMessageInQueue(queueName, requestThreadId, fileName, push_to_sqs=True):
    queue_url = getQueueUrl(queueName)
    msg = {
        "request_id": requestThreadId,
        "filename": fileName
    }
    response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(msg))
    return True

# method to return the number of messages in the queue
def getNumberOfMessagesInQ(queueName):
    queue_url = getQueueUrl(queueName)
    response = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['ApproximateNumberOfMessages'])
    return int(response['Attributes']['ApproximateNumberOfMessages'])
    
def getMessageFromQ(queueName):
    message = None
    queueUrl = getQueueUrl(queueName)
    sqsMessage = sqs_client.receive_message(QueueUrl=queueUrl, MaxNumberOfMessages=1, WaitTimeSeconds=1)    #Wait time triggers long polling
    if ('Messages' in sqsMessage):
        message_arr = sqsMessage['Messages']
        message = sqsMessage['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        sqs_client.change_message_visibility(QueueUrl=queueUrl, ReceiptHandle=receipt_handle, VisibilityTimeout=20)
        # print('Received and changed visibility timeout of message: %s' % message)
        return message
    else:
        return None

def deleteMessageFromQ(queueName, receiptHandle):
    response = sqs_client.delete_message(QueueUrl=getQueueUrl(queueName), ReceiptHandle=receiptHandle)
    print("Message deleted")
    return