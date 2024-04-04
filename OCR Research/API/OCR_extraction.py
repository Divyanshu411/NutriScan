import re
import boto3
import pandas as pd
from PIL import Image
import Levenshtein
import pandas


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
        'Protein': ['protein'],
        'Carbohydrates': ['carbohydrate', 'carb', 'carbohydrates'],
        'Total Sugar': ['sugars', 'sugar', 'sugar)', '(of which sugars)'],
        'salt': ['salt'],
        'Fibre': ['fibre', 'fiber'],
        'Fat': ['fat', 'total fat'],
        'Saturated_fat': ['saturates', 'saturated', 'saturates)', '(of which saturates)'],
        'Monounsaturated_fat': ['monounsaturates'],
        'Polyunsaturated_fat': ['polyunsaturates'],
        'n-6_poly': ['n-6 poly', 'n-6'],
        'n-3_poly': ['n-3 poly', 'n-3'],
        'Trans_fat': ['trans fats', 'trans fat'],
        'Cholesterol': ['cholesterol'],
        'total_vitamin_A': ['vitamin a', 'a'],
        'Retinol': ['retinol'],
        'Carotene': ['carotene'],
        'Vitamin_D': ['vitamin d', 'd'],
        'Vitamin_E': ['vitamin e', 'e'],
        'Vitamin_K': ['vitamin k', 'k'],
        'Thiamin': ['thiamin', 'b1', '(b1)'],
        'Riboflavin': ['riboflavin', 'b2', '(b2)'],
        'Tryptophan': ['tryptophan'],
        'Niacin_equivalent': ['niacin equivalent', 'niacin', 'b3', '(b3)'],
        'Vitamin_B6': ['vitamin b6', 'b6', '(b6)'],
        'Vitamin_B12': ['vitamin b12', 'b12', '(b12)', 'cobalamin'],
        'Total_folate': ['total folate', 'folate', 'b9', '(b9)'],
        'Natural_folate': ['natural folate'],
        'Folic_acid': ['folic acid', 'b9', 'folic', '(b9)'],
        'Dietary_folate_equivalents': ['dietary folate equivalents'],
        'Pantothenate': ['pantothenate', 'pantothenic acid', 'pantothenic', '(b5)', 'b5'],
        'Biotin': ['biotin', '(b7)', 'b7'],
        'Vitamin_C': ['vitamin c', 'c'],
        'Sodium': ['sodium'],
        'Potassium': ['potassium'],
        'Calcium': ['calcium'],
        'Magnesium': ['magnesium'],
        'Phosphorus': ['phosphorus'],
        'Iron': ['iron'],
        'Copper': ['copper'],
        'Zinc': ['zinc'],
        'Selenium': ['selenium'],
        'Iodine': ['iodine']
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
                                if item['BlockType'] == 'LINE' and (
                                        item['Text'].lower() == tokens[index + 1] or tokens[index + 1] in item[
                                    'Text'].lower().split()):
                                    confidence = item.get('Confidence', 0)
                                    extracted_values[nutrient] = {'value': value, 'confidence': confidence}

    return extracted_values


def process_image(image_path):
    client = get_aws_client()

    with Image.open(image_path) as image:
        img = read_image_as_bytearray(image_path)

    response = client.detect_document_text(Document={'Bytes': img})

    text = ""
    for i, item in enumerate(response["Blocks"]):
        if item['BlockType'] == 'LINE':
            text = text + " " + item['Text']

    result = extract_nutritional_info(text, response)

    df = pd.DataFrame(result).T
    df.columns = ['Value', 'Confidence']
    df.to_csv('nutritional_info.csv', index_label='Nutrient')


if __name__ == "__main__":
    img_path = ("D:/Documents/College/Year 3/OCR Research/OCR Research/data/Drive_images/21567_Glenisk Organic Kids "
                "Bio No Added Sugar Vanilla Yogurt_Back (1).jpg")

    process_image(img_path)
