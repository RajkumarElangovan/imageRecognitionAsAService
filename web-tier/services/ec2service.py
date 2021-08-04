import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')
IMAGE_ID = 'ami-0ee8cf7b8a34448a6'
imageId="ami-05c5bd67cc974f921"
user_data = '''#!/bin/bash
python3 -m pip install boto3
python3 -m pip install boto
bash /home/ubuntu/job.sh'''
INSTANCE_NAME_PREFIX = 'app-instance'

def startInstances(n):
    active_instance_nums = getRunningInstances()
    possible_instance_nums = range(1, 20)
    available_instance_nums = [n for n in possible_instance_nums if n not in active_instance_nums]
    for x in range(n):
        new_instance_num = available_instance_nums.pop(0)
        new_instance_name = INSTANCE_NAME_PREFIX + str(new_instance_num)
        response = ec2_client.run_instances(
            ImageId=IMAGE_ID,
            InstanceType='t2.micro',
            MaxCount=1,
            MinCount=1,
            InstanceInitiatedShutdownBehavior='terminate',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': new_instance_name
                        },
                    ]
                },
            ],
            UserData=user_data,
        )

def getNumRunningInstances():
    response = ec2_client.describe_instances()
    count = 0
    reservations = response['Reservations']
    for reservation in reservations:
        instances = reservation['Instances']
        for instance in instances:
            if (instance['State']['Code'] == 0 or instance['State']['Code'] == 16):
                count+=1
    while ("NextToken" in response):
        nextToken = response['NextToken']
        response = ec2_client.describe_instances(NextToken=nextToken)
        reservations = response['Reservations']
        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                if (instance['State']['Code'] == 0 or instance['State']['Code'] == 16):
                    count+=1
        nextToken = response['NextToken']
    return count

def getRunningInstances():
    response = ec2_client.describe_instances()
    active_instance_nums = []
    reservations = response['Reservations']
    if ("Tags" in response):
        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                for tag in instance['Tags']:
                    if (tag['Key'] == 'Name'):
                        instance_name = tag['Value']
                        instance_name_num = int(instance_name[12:])
                        active_instance_nums.append(instance_name_num)
        while ("NextToken" in response):
            nextToken = response['NextToken']
            response = ec2_client.describe_instances(nextToken)
            reservations = response['Reservations']
            for reservation in reservations:
                instances = reservation['Instances']
                for instance in instances:
                    for tag in instance['Tags']:
                        if (tag['Key'] == 'Name'):
                            instance_name = tag['Value']
                            instance_name_num = int(instance_name[12:])
                            active_instance_nums.append(instance_name_num)
            nextToken = response['NextToken']
    return active_instance_nums