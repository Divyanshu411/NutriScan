import re
import boto3
import pandas as pd
from PIL import Image
import Levenshtein
import pandas

path = "D:/Documents/College/Year 3/OCR Research/OCR Research/data/Image8/normal.jpg"

client = client = boto3.client('textract', region_name='us-east-1', aws_access_key_id='AKIATCKATOWRRSB6E5P7',
                               aws_secret_access_key='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')
Image = Image.open(path)

with open(path, 'rb') as image:
    img = bytearray(image.read())

response = client.detect_document_text(
    Document={'Bytes': img}
)

text = ""
for i, item in enumerate(response["Blocks"]):
    if item['BlockType'] == 'LINE':
        text = text + " " + item['Text']
        confidence = item.get('Confidence', 0)
        print(f"Text: {item['Text']}, Confidence: {confidence}")

ground_truth = ("NUTRITION INFORMATION /100g %RI* /30g %RI* Energy 1517kJ 455kJ 5% 359kcal 108kcal Fat 2.6g 0.8g 1% of "
                "which saturates 0.4g 0.1g 1% Carbohydrate 65g 20g 8% of which sugars 14g 4.2g 5% Fibre 14g 4.2g "
                "Protein 12g 3.6g 7% Salt 0.68g 0.2g 3% Vitamins: Vitamin D 8.4ug 168% 2.5ug 50% Thiamin (B1) 0.91mg "
                "83% 0.27mg 25% Riboflavin (B2) 1.2mg 86% 0.35mg 25% Niacin (B3) 13mg 81% 4.0mg 25% Vitamin B6 1.2mg "
                "86% 0.35mg 25% Folic Acid (B9) 166ug 83% 49.8ug 25% Vitamin B12 2.1ug 84% 0.63ug 25% Minerals: Iron "
                "8.0mg 57% 2.4mg 17%")

ocr_output = text


def normalize_string(s):
    return ''.join(s.split())


def calculate_accuracy_and_errors(str1, str2):
    str1_normalized = normalize_string(str1)
    str2_normalized = normalize_string(str2)

    levenshtein_distance = Levenshtein.distance(str1_normalized, str2_normalized)
    levenshtein_editops = Levenshtein.editops(str1_normalized, str2_normalized)

    max_length = max(len(str1_normalized), len(str2_normalized))
    accuracy = ((max_length - levenshtein_distance) / max_length) * 100

    error_elements = []
    for error in levenshtein_editops:
        operation, pos1, pos2 = error
        if operation == 'replace':
            error_elements.append((operation, str1_normalized[pos1], str2_normalized[pos2]))
        elif operation == 'insert':
            error_elements.append((operation, '-', str2_normalized[pos2]))
        elif operation == 'delete':
            error_elements.append((operation, str1_normalized[pos1], '-'))

    return accuracy, error_elements


accuracy, errors = calculate_accuracy_and_errors(ocr_output, ground_truth)

print()
print(f"Levenshtein Accuracy: {accuracy:.2f}%")
print(f"Errors: {errors}")


def extract_value(nutrient, tokens, index):
    if nutrient == 'energy_kj' or nutrient == 'energy_kcal':
        match = re.match(r'(\d+(\.\d+)?)(kj|kcal)', tokens[index + 1], re.IGNORECASE)
        if match:
            value, _, unit = match.groups()
            value = float(value)
            if unit.lower() == 'kj' and nutrient == 'energy_kj':
                return value
            elif unit.lower() == 'kcal' and nutrient == 'energy_kcal':
                return value
    else:
        for i in range(index + 1, len(tokens)):
            match = re.match(r'(\d+(\.\d+)?)(g|mg|ug)', tokens[i], re.IGNORECASE)
            if match:
                value, _, unit = match.groups()
                value = float(value)
                if unit.lower() == 'mg':
                    value /= 1000
                elif unit.lower() == 'ug':
                    value /= 1000000
                return value
    return 0


def extract_nutritional_info():
    nutrient_keywords = {
        'energy_kj': ['energy'],
        'energy_kcal': ['energy'],
        'calories': ['calories'],
        'protein': ['protein'],
        'carbohydrates': ['carbohydrate', 'carb', 'carbohydrates'],
        'sugar': ['sugars'],
        'fat': ['fat', 'total fat'],
        'saturated_fat': ['saturates', 'saturated'],
        'monounsaturated_fat': ['monounsaturates'],
        'polyunsaturated_fat': ['polyunsaturates'],
        'cholesterol': ['cholesterol'],
        'sodium': ['sodium'],
        'salt': ['salt'],
        'potassium': ['potassium'],
        'calcium': ['calcium'],
        'magnesium': ['magnesium'],
        'phosphorus': ['phosphorus'],
        'fiber': ['fibre'],
        'copper': ['copper'],
        'zinc': ['zinc'],
        'selenium': ['selenium'],
        'iodine': ['iodine'],
        'vitamin_A': ['vitamin a', 'a'],
        'vitamin_B': ['vitamin b', 'b'],
        'vitamin_C': ['vitamin c', 'c'],
        'vitamin_D': ['vitamin d', 'd'],
        'vitamin_E': ['vitamin e', 'e'],
        'vitamin_K': ['vitamin k', 'k'],
        'vitamin_B6': ['vitamin b6', 'b6'],
        'vitamin_B12': ['vitamin b12', 'b12'],
        'iron': ['iron'],
        'retinol': ['retinol'],
        'carotene': ['carotene'],
        'thiamin': ['thiamin'],
        'riboflavin': ['riboglavin'],
        'tryptophan': ['tryptophan'],
        'niacin': ['niacin'],
        'total_folate': ['total folate', 'folate'],
        'Natural_Folate': ['natural folate'],
        'niacin_equivalent': ['niacin equivalent'],
        'folic_acid': ['folic acid', 'acid', 'b9'],
        'dietary_folate_equivalents': ['dietary folate equivalents'],
        'pantothenate': ['pantothenate'],
        'biotin': ['biotin'],
    }

    extracted_values = {nutrient: 0 for nutrient in nutrient_keywords}

    lines = text.split('\n')
    for line in lines:
        line = line.lower()
        if any(keyword in line for nutrient, keywords in nutrient_keywords.items() for keyword in keywords):
            tokens = line.split()
            for nutrient, keywords in nutrient_keywords.items():
                for keyword in keywords:
                    if keyword in tokens:
                        index = tokens.index(keyword)
                        if index + 1 < len(tokens):
                            value = extract_value(nutrient, tokens, index)
                            extracted_values[nutrient] = value

    return extracted_values


result = extract_nutritional_info()

# for nutrient, value in result.items():
#     if value:
#         print(f'{nutrient.capitalize()}: {value}')
#     is_correct = input("Is this value correct? (y/n): ")
#     is_correct.lower()
#     if is_correct == 'n':
#         correct_value = input("Enter the correct value: ")
#         result[nutrient] = correct_value

df = pd.DataFrame(result.items(), columns=['Nutrient', 'Value'])
df.to_csv('nutritional_info.csv', index=False)