import os
import boto
import boto3
import botocore.exceptions as ex
import json
import time


# QUEUE PROPERTIES
INPUT_QUEUE = "input_queue"
OUTPUT_QUEUE = "output_queue"

# objects to represent the SQS queue
sqs_client = boto3.client('sqs')
sqs_resource = boto3.resource('sqs')




# create the queue based on queue name if it does not exist and return the queueUrl
def createQueue(queueName):
    response = sqs_client.create_queue(QueueName=queueName)
    queue_url = response['QueueUrl']
    time.sleep(1)
    return queue_url

def getQueueUrl(queueName):
    response = sqs_client.get_queue_url(QueueName=queueName)
    queueUrl = response['QueueUrl']
    return queueUrl

# method to return the number of messages in the queue
def getNumberOfMessages():
    queueName = sqs_resource.get_queue_by_name(QueueName=INPUT_QUEUE)
    return int(queueName.attributes.get('ApproximateNumberOfMessages'))


def putMessageOutputQueue(request_id, fileName, result):
    if OUTPUT_QUEUE not in sqs_resource.queues.all():
        queueUrl = createQueue(OUTPUT_QUEUE)
    queueUrl = getQueueUrl(OUTPUT_QUEUE)
    resultList = [fileName, result]
    requestDict = {"request_id": request_id}
    fileNameDict = {"filename": fileName}
    resultDict = {"value":result}
    serializedData = json.dumps([requestDict,fileNameDict,resultDict])
    response = sqs_client.send_message(QueueUrl=queueUrl, MessageBody=serializedData)
    return True


def getMessageFromQ(queueName):
    
    message = None
    queueUrl = getQueueUrl(INPUT_QUEUE)
    sqsMessage = sqs_client.receive_message(QueueUrl=queueUrl, MaxNumberOfMessages=1, WaitTimeSeconds=1)
    if ('Messages' in sqsMessage):
        message_arr = sqsMessage['Messages']
        message = sqsMessage['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        sqs_client.change_message_visibility(QueueUrl=queueUrl, ReceiptHandle=receipt_handle, VisibilityTimeout=20)
        return message
    else:
        return None

def deleteMessage(receiptHandle):
    response = sqs_client.delete_message(QueueUrl=getQueueUrl(INPUT_QUEUE), ReceiptHandle=receiptHandle)
    print("Message deleted")
    return
