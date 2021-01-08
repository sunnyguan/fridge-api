import requests
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

def getWords():
    endpoint = "https://c1-fridge.cognitiveservices.azure.com/" # os.environ['COMPUTER_VISION_ENDPOINT'] # https://homeworkocr.cognitiveservices.azure.com/
    subscription_key = "ed643e1b154d45b6a2e27311ccb0eb9c" # os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY'] # a87c544e2d874de5a8b3eb6c92122482
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    remote_image_url = "https://miro.medium.com/max/400/1*aJN2ulfd0WD28C4S7qgFGQ.jpeg"
    recognize_handw_results = computervision_client.read_in_stream(open('trader.jpeg', 'rb'),  raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    operation_location_remote = recognize_handw_results.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = operation_location_remote.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        get_handw_text_results = computervision_client.get_read_result(operation_id)
        if get_handw_text_results.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if get_handw_text_results.status == OperationStatusCodes.succeeded:
        for text_result in get_handw_text_results.analyze_result.read_results:
            for line in text_result.lines:
                print(line.text)
                print(line.bounding_box)
    print()


if __name__ == '__main__':
    getWords()