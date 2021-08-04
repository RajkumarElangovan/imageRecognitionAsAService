import os.path
import time
import boto
import boto3
import subprocess
import json
import botocore.exceptions
import subprocess
from service import sqsService 
from service import s3Service
from botocore.config import Config


# QUEUE PROPERTIES
INPUT_QUEUE = "input_queue"
OUTPUT_QUEUE = "output_queue"

# BUCKET PROPERTIES
INPUT_BUCKET = "input.bucket11"
OUTPUT_BUCKET = "output.bucket11"

def main():
    idle_count = 0
    while True:
        messageBody = sqsService.getMessageFromQ(INPUT_QUEUE)
        if (messageBody is None):
            idle_count+=1
            if (idle_count >= 3):
                selfTerminate()
        else:
            idle_count = 0
            start(messageBody)
            
def selfTerminate():
    print("No Messages. So terminating")
    subprocess.call(["sudo", "shutdown", "-h", "now"])
    return

def start(messageBody):
    

    #fetch the input image name from the message received from input sqs queue
    keyName = json.loads(messageBody['Body'])['fileName']

    #logMessage
    print("Received Key to send to EC2 instance"+str(keyName))

    #construct url of the object in the S3 to download it and perform classification
    s3ObjectURL = r"https://s3.amazonaws.com/{}".format(INPUT_BUCKET)+r"/{}".format(keyName)
    
    #command to predict the image
    command = ["cd /home/ubuntu/classifier/; sudo wget {} -P /home/ubuntu/app-tier/; sudo python3 image_classification.py /home/ubuntu/app-tier/{};sudo rm -f /home/ubuntu/app-tier/{}".format(s3ObjectURL,keyName,keyName)]
    commandToRun = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    time.sleep(10)

    #output from the classifier
    output = commandToRun.stdout.decode()
    output = str(output)
    output = output.split("\n")
    print("Output of given Image {} from ML Model is:".format(keyName) + str(output))
    print(keyName)

    threadId = json.loads(messageBody['Body'])['request_id']
    s3Service.storeOutputS3(keyName, str(output))
    status = sqsService.putMessageOutputQueue(threadId, keyName, str(output))

    if status:
        sqsService.deleteMessage(INPUT_QUEUE, messageBody['ReceiptHandle'])

    return


if __name__ == "__main__":
    main()



