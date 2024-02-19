import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from Levenshtein import distance
import Levenshtein
import os

#nltk.download('punkt')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:/Documents/College/Year 3/OCR Research/Google Vision/comparison-demo-e1cd4f179084.json'

all_text = ""

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision

    global all_text

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    filtered_texts = [text.description for text in texts[1:] if text.description is not None]
    all_text = " ".join(filtered_texts)
    print(all_text)

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )


print(detect_text('D:/Documents/College/Year 3/OCR Research/data/Image5/normal.jpg'))

ground_truth = ("NUTRITION This pack contains approx. 6 servings. TYPICAL VALUES Per 100g  Per serving (25g) Energy "
                "2032kj/486kcal 508kj/121kcal fat 23.7g 5.9g of which saturates 2.2g 0.6g of which monounsaturates "
                "18.5g 4.6g of which polyunsaturates 1.8g 0.5g Carbohydrate 61.6g 15.4g of which sugars 4.3g 1.1g "
                "Fibre 3.9g 1.0g Protein 4.6g 1.2g Salt 1.7g 0.43g")

ocr_output = all_text

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