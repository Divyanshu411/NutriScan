import boto3
from PIL import Image
from nltk import LineTokenizer
from nltk.tokenize import word_tokenize
from collections import Counter
from Levenshtein import distance
import Levenshtein

client = client = boto3.client('textract', region_name='us-east-1', aws_access_key_id='AKIATCKATOWRRSB6E5P7',
                               aws_secret_access_key='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')
Image = Image.open("../data/Image1/no_border.jpg")

with open('../data/Image1/no_border.jpg', 'rb') as image:
    img = bytearray(image.read())

response = client.detect_document_text(
    Document={'Bytes': img}
)

text = ""
for item in response['Blocks']:
    if item['BlockType'] == 'LINE':
        print(item["Text"])
        text = text + "\n" + item['Text']

ground_truth = ("Nutrition Facts Serving Size 1 Tbsp (15 mL) Servings Per Container About 64 Amount Per Serving "
                "Calories 0 Calories from Fat 0 % Daily Value* Total Fat 0g 0% Saturated Fat 0g 0% Trans Fat 0g "
                "Cholesterol 0mg 0% Sodium 0mg 0% Potassium 15mg 0% Total Carbohydrate 0g 0% Dietary Fiber 0g 0% "
                "Sugars 0g Protein 0g Vitamin A 0% Vitamin C 0% Calcium 0% Iron 0%")

ocr_output = text
print(ocr_output)

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

ground_truth_line = (
    "Nutrition Facts\nServing Size 1 Tbsp (15 mL)\nServings Per Container About 64\nAmount Per Serving"
    "\nCalories 0 Calories from Fat 0\n% Daily Value*\nTotal Fat 0g 0%\nSaturated Fat 0g 0%\nTrans Fat 0g"
    "\nCholesterol 0mg 0%\nSodium 0mg 0%\nPotassium 15mg 0%\nTotal Carbohydrate 0g 0%\nDietary Fiber 0g 0%"
    "\nSugars 0g\nProtein 0g\nVitamin A 0% Vitamin C 0%\nCalcium 0% Iron 0%")

ocr_output_line = text


def tokenize(text):
    tk = LineTokenizer(blanklines='discard')
    tokens = tk.tokenize(text)
    return tokens


def calculate_token_accuracy(tokens_ocr, tokens_ground_truth):
    counter_ocr = Counter(tokens_ocr)
    counter_ground_truth = Counter(tokens_ground_truth)

    common_tokens = counter_ocr & counter_ground_truth

    precision = sum(common_tokens.values()) / sum(counter_ocr.values())
    recall = sum(common_tokens.values()) / sum(counter_ground_truth.values())
    f1_score = 2 * precision * recall / (precision + recall)

    return precision, recall, f1_score


tokens_ground_truth = tokenize(ground_truth_line)
tokens_ocr = tokenize(ocr_output_line)

print("Tokenized OCR output:")
print(tokens_ocr)

print("\nTokenized Ground Truth:")
print(tokens_ground_truth)

precision, recall, f1_score = calculate_token_accuracy(tokens_ocr, tokens_ground_truth)

# print("Tokenized OCR output:")
# print(tokens_ocr)
#
# print("\nTokenized Ground Truth:")
# print(tokens_ground_truth)

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
