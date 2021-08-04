import json
import os.path
import boto
import boto3
import botocore.exceptions

# BUCKET PROPERTIES
INPUT_BUCKET = "input.bucket11"
OUTPUT_BUCKET = "output.bucket11"

# objects to access S3
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')


# send Image from input Bucket to EC2 for prediction
def getImageUrl(object_name):
    print(object_name)
    s3_client.download_file(INPUT_BUCKET, object_name, object_name)

# store the predicted result in the output S3 bucket in key-value pair
def storeOutputS3(fileName, result):
    if s3_resource.Bucket(OUTPUT_BUCKET) not in s3_resource.buckets.all():
        createBucket(OUTPUT_BUCKET)
    predictedResult = {fileName: result}
    serializedData = json.dumps(predictedResult)
    
    s3_client.put_object(Bucket = OUTPUT_BUCKET, Key=fileName+".json", Body=serializedData)
    print("Uploaded result in key-value pair to S3 output bucket")

# create Input and Output S3 Buckets
def createBucket(bucketName):
    s3_client.create_bucket(Bucket=bucketName)
    print(bucketName + " Created")
    return

