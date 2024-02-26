import nltk
from nltk.tokenize import word_tokenize
import pytesseract

nltk.download('punkt')


def process_image(image_path, ground_truth):
    text = pytesseract.image_to_string(image_path)
    text_without_empty_lines = ' '.join(line.strip() for line in text.splitlines() if line.strip())

    print(f"\nProcessing image: {image_path}")
    print(text_without_empty_lines)

    def tokenize(text):
        nltk_tokens = word_tokenize(text)
        return nltk_tokens

    def calculate_token_accuracy(tokens_ocr, tokens_ground_truth):
        common_tokens = set(tokens_ocr) & set(tokens_ground_truth)
        accuracy = len(common_tokens) / len(set(tokens_ground_truth)) * 100
        return accuracy

    ocr_output = text_without_empty_lines

    tokens_ground_truth = tokenize(ground_truth)
    tokens_ocr = tokenize(ocr_output)

    accuracy = calculate_token_accuracy(tokens_ocr, tokens_ground_truth)

    print("Tokenized OCR output:")
    print(tokens_ocr)

    print("\nTokenized Ground Truth:")
    print(tokens_ground_truth)

    print("\nToken Accuracy: {:.3f}%".format(accuracy))


ground_truth = ("Nutrition Facts Serving Size 1 Tbsp (15 mL) Servings Per Container About 64 Amount Per Serving "
                "Calories 0 Calories from Fat 0 % Daily Value* Total Fat 0g 0% Saturated Fat 0g 0% Trans Fat 0g "
                "Cholesterol 0mg 0% Sodium 0mg 0% Potassium 15mg 0% Total Carbohydrate 0g 0% Dietary Fiber 0g 0% "
                "Sugars 0g Protein 0g Vitamin A 0% Vitamin C 0% Calcium 0% Iron 0%")

image_paths = ['../data/Image1/no_border.jpg',
               '../data/Image1/download.jpeg',
               '../data/Image1/bw_image.jpeg']

for image_path in image_paths:
    process_image(image_path, ground_truth)
