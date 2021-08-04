import threading
import _thread
from time import sleep
from services import s3Service, ec2Service, sqsService
from flask import Flask, render_template, request, redirect, url_for, abort, send_file, json
from werkzeug.utils import secure_filename
import os

# BUCKET PROPERTIES
INPUT_BUCKET = "input_bucket12"
OUTPUT_BUCKET = "output_bucket12"

# QUEUE PROPERTIES
INPUT_QUEUE = "input_queue"
OUTPUT_QUEUE = "output_queue"

responses = []

app = Flask(__name__)

@app.before_first_request
def setup():
    _thread.start_new_thread(output_poller_thread, ())
    #_thread.start_new_thread(controller.startController, ())

def output_poller_thread():
    print("poller started", flush=True)
    while True:
        response_message = sqsService.getMessageFromQ(OUTPUT_QUEUE)
        if (response_message is not None):
            message = json.loads(response_message['Body'])
            res = {
                "thread": message["request_id"],
                "filename": message["filename"],
                "output": message["output"],
                "handled": "false",
            }
            print(res, flush=True)
            responses.append(res)
            receipt_handle = response_message['ReceiptHandle']
            sqsService.deleteMessageFromQ(OUTPUT_QUEUE, receipt_handle)


def send_to_input_bucket(file):
    s3Service.storeInputS3(INPUT_BUCKET, file)
    threadID = threading.Thread.getName()
    sqsService.putMessageInQueue(INPUT_QUEUE, threadID, file)
    return get_result(threadID)

def get_result(threadId):
    found = False
    while (not found):
        for response in responses:
            if (response["thread"] == threadId and response["handled"] == "false"):
                found = True
                response["handled"] = "true"
                return {response['filename']: response["output"]}

@app.route('/', methods=['GET'])
def hello():
    return "hello"

@app.route('/', methods=['POST', 'GET'])
def process_thread():
    if (request.method == 'POST'):
        return "here"
        img = request.files['myfile']
        if img:
            filename = secure_filename(img.filename)
            img.save(filename)
            print("here", flush=True)
        return _thread.start_new_thread(send_to_input_bucket, (filename))
    if (request.method == 'GET'):
        return "Get works!"

if __name__ == '__main__':
    app.run(
        #debug=True,
        #host=os.getenv('LISTEN', '0.0.0.0'),
        #port=int(os.getenv('PORT', '8080')),
    )
