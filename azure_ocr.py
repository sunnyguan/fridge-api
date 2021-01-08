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

def getWords(url, endpoint, subscription_key):
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    remote_image_url = url
    recognize_handw_results = computervision_client.read(remote_image_url,  raw=True)

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

    # Create and return list
    arr = []
    if get_handw_text_results.status == OperationStatusCodes.succeeded:
        for text_result in get_handw_text_results.analyze_result.read_results:
            for line in text_result.lines:
                arr.append(line.text.lower())
    return arr
