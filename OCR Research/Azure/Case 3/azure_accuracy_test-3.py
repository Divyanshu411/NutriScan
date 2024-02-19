import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import Levenshtein
from nltk.tokenize import word_tokenize
from collections import Counter
from Levenshtein import distance


API_KEY = "6e7497d70b9246028447cc56ef2fc37e"
ENDPOINT = "https://research-vision-api.cognitiveservices.azure.com/"

cv_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))

image_path = 'D:/Documents/College/Year 3/OCR Research/data/Image6/normal.jpg'
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

ground_truth = ("NUTRITION As sold Typical values Per One glass % 100ml (150ml) RI* Energy 12kJ / 3kcal 17kJ / 4kcal "
                "<1% Fat <0.1g <0.1g <1% of which saturates <0.1g <0.1g <1% Carbohydrate 0.4g 0.6g of which sugars "
                "0.4g 0.6g 1% Fibre <0.1g <0.1g Protein <0.1g <0.1g Salt <0.01g <0.01g <1%")

ocr_output = text_without_lines


# Levenshtein
print()
print("================================================")
print("*************** Levenshtein *************")
print("================================================")

def normalize_string(s):
    return ''.join(s.split())


def calculate_accuracy(str1, str2):
    str1_normalized = normalize_string(str1)
    str2_normalized = normalize_string(str2)

    levenshtein_distance = Levenshtein.distance(str1_normalized, str2_normalized)

    max_length = max(len(str1_normalized), len(str2_normalized))
    accuracy = ((max_length - levenshtein_distance) / max_length) * 100

    return accuracy


accuracy = calculate_accuracy(ocr_output, ground_truth)

print(f"Levenshtein Accuracy: {accuracy:.2f}%")

# Tokenization
print()
print("================================================")
print("**************** Tokenization *******************")
print("================================================")


def tokenize(text):
    nltk_tokens = word_tokenize(text)
    return nltk_tokens


def calculate_token_accuracy(tokens_ocr, tokens_ground_truth):
    counter_ocr = Counter(tokens_ocr)
    counter_ground_truth = Counter(tokens_ground_truth)

    common_tokens = counter_ocr & counter_ground_truth

    precision = sum(common_tokens.values()) / sum(counter_ocr.values())
    recall = sum(common_tokens.values()) / sum(counter_ground_truth.values())
    f1_score = 2 * precision * recall / (precision + recall)

    return precision, recall, f1_score


tokens_ground_truth = tokenize(ground_truth)
tokens_ocr = tokenize(ocr_output)

precision, recall, f1_score = calculate_token_accuracy(tokens_ocr, tokens_ground_truth)

print("Tokenized OCR output:")
print(tokens_ocr)

print("\nTokenized Ground Truth:")
print(tokens_ground_truth)

print("\nToken Precision: ", precision)
print("Token recall: ", recall)
print("Token f1_score: ", f1_score)


# Character Frequency
print()
print("================================================")
print("*************** Character Frequency *************")
print("================================================")
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

char_counts_ocr, char_counts_truth = compare_char_frequencies(ocr_output, ground_truth)
accuracy = calculate_accuracy(ocr_output, ground_truth)

print("Alphabet frequencies in OCR output:")
print(char_counts_ocr)

print("\nAlphabet frequencies in Ground Truth:")
print(char_counts_truth)

print("Character frequency Accuracy: {:.2f}%".format(accuracy))
