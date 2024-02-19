import nltk
from nltk.tokenize import word_tokenize
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'comparison-demo-e1cd4f179084.json'

nltk.download('punkt')

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


print(detect_text('../data/Image1/bw_image.jpeg'))


def tokenize(text):
    nltk_tokens = word_tokenize(text)
    return nltk_tokens


def calculate_token_accuracy(tokens_ocr, tokens_ground_truth):
    common_tokens = set(tokens_ocr) & set(tokens_ground_truth)
    accuracy = len(common_tokens) / len(set(tokens_ground_truth)) * 100
    return accuracy


ground_truth = ("Nutrition Facts Serving Size 1 Tbsp (15 mL) Servings Per Container About 64 Amount Per Serving "
                "Calories 0 Calories from Fat 0 % Daily Value* Total Fat 0g 0% Saturated Fat 0g 0% Trans Fat 0g "
                "Cholesterol 0mg 0% Sodium 0mg 0% Potassium 15mg 0% Total Carbohydrate 0g 0% Dietary Fiber 0g 0% "
                "Sugars 0g Protein 0g Vitamin A 0% Vitamin C 0% Calcium 0% Iron 0%")

ocr_output = all_text

tokens_ground_truth = tokenize(ground_truth)
tokens_ocr = tokenize(ocr_output)

accuracy = calculate_token_accuracy(tokens_ocr, tokens_ground_truth)

print("Tokenized OCR output:")
print(tokens_ocr)

print("\nTokenized Ground Truth:")
print(tokens_ground_truth)

print("\nToken Accuracy: {:.3f}%".format(accuracy))
