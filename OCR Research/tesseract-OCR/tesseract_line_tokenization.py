import nltk
from nltk.tokenize import LineTokenizer
import pytesseract
from collections import Counter

nltk.download('punkt')

text = pytesseract.image_to_string('../data/Image1/no_border.jpg')
text_without_empty_lines = ' '.join(line.strip() for line in text.splitlines() if line.strip())


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


ground_truth = ("Nutrition Facts\nServing Size 1 Tbsp (15 mL)\nServings Per Container About 64\nAmount Per Serving "
                "\nCalories 0 Calories from Fat 0\n% Daily Value*\nTotal Fat 0g 0%\nSaturated Fat 0g 0%\nTrans Fat 0g "
                "\nCholesterol 0mg 0%\nSodium 0mg 0%\nPotassium 15mg 0%\nTotal Carbohydrate 0g 0%\nDietary Fiber 0g 0% "
                "\nSugars 0g\nProtein 0g\nVitamin A 0% Vitamin C 0%\nCalcium 0% Iron 0%")

ocr_output = text

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
