import time
from collections import Counter
from Levenshtein import distance
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

def count_char_frequencies(text):
    char_counts = Counter(char for char in text)
    return char_counts


def compare_char_frequencies(ocr_output, ground_truth):
    char_counts_ocr = count_char_frequencies(ocr_output)
    char_counts_truth = count_char_frequencies(ground_truth)

    return char_counts_ocr, char_counts_truth


def calculate_accuracy(ocr_output, ground_truth):
    levenshtein_distance = distance(ocr_output, ground_truth)
    max_length = max(len(ocr_output), len(ground_truth))
    accuracy = (1 - levenshtein_distance / max_length) * 100
    return accuracy


ground_truth = ("Nutrition Facts Serving Size 1 Tbsp (15 mL) Servings Per Container About 64 Amount Per Serving "
                "Calories 0 Calories from Fat 0 % Daily Value* Total Fat 0g 0% Saturated Fat 0g 0% Trans Fat 0g "
                "Cholesterol 0mg 0% Sodium 0mg 0% Potassium 15mg 0% Total Carbohydrate 0g 0% Dietary Fiber 0g 0% "
                "Sugars 0g Protein 0g Vitamin A 0% Vitamin C 0% Calcium 0% Iron 0%")
ocr_output = text_without_lines

char_counts_ocr, char_counts_truth = compare_char_frequencies(ocr_output, ground_truth)
accuracy = calculate_accuracy(ocr_output, ground_truth)

print("Alphabet frequencies in OCR output:")
print(char_counts_ocr)

print("\nAlphabet frequencies in Ground Truth:")
print(char_counts_truth)

print("Accuracy: {:.2f}%".format(accuracy))