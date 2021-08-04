import os.path
import boto3
import botocore.exceptions

# objects to access S3
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')


# send Image from input Bucket to EC2 for prediction
def getImage(bucketName, object_name):
    print(object_name)
    s3_client.download_file(bucketName, object_name, object_name)

# create Input and Output S3 Buckets
def createBucket(bucketName):
    s3_client.create_bucket(Bucket=bucketName)
    print(bucketName + " Created")
    return

# upload received image request into the input s3 bucket
def storeInputS3(bucketName, file_path):
    # check if Bucket exists and create it
    if s3_resource.Bucket(bucketName) not in s3_resource.buckets.all():
        createBucket(bucketName)
    # extract the fileName and store the image in input bucket
    fileName = os.path.split(file_path)[-1]
    s3_resource.meta.client.upload_file(Filename=file_path, Bucket=bucketName, Key=fileName, ExtraArgs={'ACL': 'public-read'})
    print("Uploaded file to S3 bucket")
    return True