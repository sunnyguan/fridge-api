from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time


subscription_key = "-insert-here-"
endpoint = "https://analyze-receipts.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# '''
# Batch Read File, recognize handwritten text - local
# This example will extract handwritten text in an image, then print results, line by line.
# This API call can also recognize handwriting (not shown).
# '''
# print("===== Batch Read File - local =====")
# # Get an image with handwritten text
# remote_image_handw_text_url = "https://images.iwaspoisoned.com/414967/tn1200h_16056582337837.JPG"

# # Open the image
# "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"

# # Call API with URL and raw response (allows you to get the operation location)
# recognize_handw_results = computervision_client.read(remote_image_handw_text_url,  raw=True)

# # Get the operation location (URL with an ID at the end) from the response
# operation_location_remote = recognize_handw_results.headers["Operation-Location"]

# # Grab the ID from the URL
# operation_id = operation_location_remote.split("/")[-1]

# # Call the "GET" API and wait for it to retrieve the results 
# while True:
#     get_handw_text_results = computervision_client.get_read_result(operation_id)
#     if get_handw_text_results.status not in ['notStarted', 'running']:
#         break
#     time.sleep(1)

# # Print the detected text, line by line
# if get_handw_text_results.status == OperationStatusCodes.succeeded:
#     for text_result in get_handw_text_results.analyze_result.read_results:
#         for line in text_result.lines:
#             print(line.text)
#             # print(line.bounding_box)
# print()


'''
Batch Read File, recognize handwritten text - local
This example extracts text from a handwritten local image, then prints results.
This API call can also recognize remote image text (shown in next example, Batch Read File - remote).
'''
print("===== Batch Read File - local =====")
# Get image of handwriting
local_image_handwritten_path = "test-what-is-in-your-fridge/resources/IMG_20210107_024116.jpg"
# Open the image
local_image_handwritten = open(local_image_handwritten_path, "rb")

# Call API with image and raw response (allows you to get the operation location)
recognize_handwriting_results = computervision_client.batch_read_file_in_stream(local_image_handwritten, raw=True)
# Get the operation location (URL with ID as last appendage)
operation_location_local = recognize_handwriting_results.headers["Operation-Location"]
# Take the ID off and use to get results
operation_id_local = operation_location_local.split("/")[-1]

# Call the "GET" API and wait for the retrieval of the results
while True:
    recognize_handwriting_result = computervision_client.get_read_operation_result(operation_id_local)
    if recognize_handwriting_result.status not in ['notStarted', 'running']:
        break
    time.sleep(1)

# Print results, line by line
if recognize_handwriting_result.status == OperationStatusCodes.succeeded:
    for text_result in recognize_handwriting_result.analyze_result.read_results:
        for line in text_result.lines:
            print(line.text)
            # print(line.bounding_box)
print()
'''
END - Batch Read File - local
'''