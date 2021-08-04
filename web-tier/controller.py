from time import sleep
from services import ec2service, sqsService

INPUT_QUEUE = 'input_queue'
incoming_requests = False

def startController():
    print("controller started")
    while(True):
        while (incoming_requests):
            autoscale()
        while(not incoming_requests):
            sleep(1)

def autoscale():
    numMessages = sqsService.getNumberOfMessagesInQ('input_queue')
    numActiveInstances = ec2service.getNumRunningInstances()
    if (numMessages > numActiveInstances):
        scaleUp(numMessages-numActiveInstances)

#scale up by n instances
def scaleUp(n):
    num = ec2service.getNumRunningInstances()
    if ((num + n) < 19):
        print("scaling up by " + str(n))
        ec2service.startInstances(n)
    else:
        maxAdditional = 19 - num
        if (maxAdditional <= 0):
            print("Cannot scale up more")
            return
        else:
            print("scaling up by " + str(maxAdditional))
            ec2service.startInstances(maxAdditional)
            