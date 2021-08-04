import boto3
import _thread
from time import sleep
from services import sqsService, ec2service
import controller

sqsService.createQueue('input_queue')
print('queue created')
controller_thread = _thread.start_new_thread(controller.startController, ())
print("Putting 1 message in queue")
sqsService.putMessageInQueue('input_queue', '1', 'test1')
controller.incoming_requests = True
sleep(30)
print("Putting 10 messages in queue")
for x in range(10):
    sqsService.putMessageInQueue('input_queue', '1', 'test1')
sleep(30)
print("Putting 30 messages in queue")
for x in range(30):
    sqsService.putMessageInQueue('input_queue', '1', 'test1')
sleep(30)
print("Putting 2 messages in queue")
for x in range(2):
    sqsService.putMessageInQueue('input_queue', '1', 'test1')
sleep(30)
controller.incoming_requests = False