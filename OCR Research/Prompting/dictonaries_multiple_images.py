import re
import boto3
import pandas as pd
import Levenshtein
from PIL import Image
import os


def get_aws_client():
    return boto3.client(
        'textract',
        region_name='us-east-1',
        aws_access_key_id='AKIATCKATOWRRSB6E5P7',
        aws_secret_access_key='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'
    )


def read_image_as_bytearray(image_path):
    with open(image_path, 'rb') as image:
        return bytearray(image.read())


def calculate_accuracy_and_errors(str1, str2):
    def normalize_string(s):
        if isinstance(s, list):
            s = ' '.join(s)
        return ''.join(s.split())

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


def extract_value(nutrient, tokens, index):
    if nutrient == 'energy_kj' or nutrient == 'energy_kcal':
        match = re.match(r'(\d+(\.\d+)?)(kj|kcal)/(\d+(\.\d+)?)(kj|kcal)', tokens[index + 1], re.IGNORECASE)
        if match:
            value1, _, unit1, value2, _, unit2 = match.groups()
            value1 = float(value1)
            value2 = float(value2)
            if unit1.lower() == 'kj' and nutrient == 'energy_kj':
                return value1
            elif unit2.lower() == 'kcal' and nutrient == 'energy_kcal':
                return value2
            elif unit1.lower() == 'kj' and nutrient == 'energy_kcal':
                return round(value2 / 4.184, 2)
            elif unit2.lower() == 'kcal' and nutrient == 'energy_kj':
                return round(value1 * 4.184, 2)
        else:
            match = re.match(r'(\d+(\.\d+)?)(kj|kcal)', tokens[index + 1], re.IGNORECASE)
            if match:
                value, _, unit = match.groups()
                value = float(value)
                if unit.lower() == 'kj' and nutrient == 'energy_kj':
                    return value
                elif unit.lower() == 'kcal' and nutrient == 'energy_kcal':
                    return value
                elif unit.lower() == 'kj' and nutrient == 'energy_kcal':
                    return round(value / 4.184, 2)
                elif unit.lower() == 'kcal' and nutrient == 'energy_kj':
                    return round(value * 4.184, 2)
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


def extract_nutritional_info(text, response):
    nutrient_keywords = {
        'energy_kj': ['energy', 'kj'],
        'energy_kcal': ['energy', 'kcal'],
        'calories': ['calories'],
        'protein': ['protein'],
        'carbohydrates': ['carbohydrate', 'carb', 'carbohydrates'],
        'sugar': ['sugars', 'sugar', 'sugar)', '(of which sugars)'],
        'fat': ['fat', 'total fat'],
        'saturated_fat': ['saturates', 'saturated', 'saturates)', '(of which saturates)'],
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
        'vitamin_B12': ['vitamin b12', 'b12', '(b12)'],
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

    extracted_values = {nutrient: {'value': 0, 'confidence': 0} for nutrient in nutrient_keywords}

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
                            for i, item in enumerate(response["Blocks"]):
                                if item['BlockType'] == 'LINE' and (item['Text'].lower() == tokens[index + 1] or tokens[index + 1] in item['Text'].lower().split()):
                                    confidence = item.get('Confidence', 0)
                                    extracted_values[nutrient] = {'value': value, 'confidence': confidence}

    return extracted_values


def process_image(image_folder_path, ground_truth_folder_path):
    files = [file for file in os.listdir(image_folder_path) if file.lower().endswith('.jpg')]

    for file in files:
        image_path = os.path.join(image_folder_path, file)
        client = get_aws_client()

        with Image.open(image_path) as img:
            img_bytearray = read_image_as_bytearray(image_path)

        response = client.detect_document_text(Document={'Bytes': img_bytearray})

        text = ""
        for i, item in enumerate(response["Blocks"]):
            if item['BlockType'] == 'LINE':
                text = text + " " + item['Text']
                confidence = item.get('Confidence', 0)
                # print(f"Text: {item['Text']}, Confidence: {confidence}")


        txt_file = os.path.splitext(file)[0] + '.txt'
        with open(os.path.join(ground_truth_folder_path, txt_file), 'r') as f:
            lines = f.readlines()

        ground_truth = lines
        ocr_output = text

        accuracy, errors = calculate_accuracy_and_errors(ocr_output, ground_truth)

        print(file)
        print(text)
        print(f"Levenshtein Accuracy: {accuracy:.2f}%")
        print(f"Errors: {errors}")
        print()

        result = extract_nutritional_info(text, response)

        df = pd.DataFrame(result).T
        df.index.name = 'Nutrients'
        df.to_csv(
            f'D:/Documents/College/Year 3/OCR Research/OCR Research/Prompting/Nutrition_Info/Nutritional_info_{file}.csv')


if __name__ == "__main__":
    image_folder_path = 'D:/Documents/College/Year 3/OCR Research/OCR Research/data/Drive_images'
    ground_truth_folder_path = 'D:/Documents/College/Year 3/OCR Research/OCR Research/data/Ground_truth_text'

    process_image(image_folder_path, ground_truth_folder_path)
