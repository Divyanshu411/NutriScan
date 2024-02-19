import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes


API_KEY = "6e7497d70b9246028447cc56ef2fc37e"
ENDPOINT = "https://research-vision-api.cognitiveservices.azure.com/"

cv_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))

image_path = '../data/Image1/no_border.jpg'
response = cv_client.read_in_stream(open(image_path, 'rb'), Language='en', raw=True)
operationLocation = response.headers['Operation-Location']
operation_id = operationLocation.split('/')[-1]
time.sleep(5)
result = cv_client.get_read_result(operation_id)

all_text = ' '
if result.status == OperationStatusCodes.succeeded:
    read_result = result.analyze_result.read_results
    for analyze_result in read_result:
        for line in analyze_result.lines:
            all_text += line.text
            all_text += " "

text_without_lines = ' '.join(line.strip() for line in all_text.splitlines() if line.strip())
print(text_without_lines)
