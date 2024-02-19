import Levenshtein
import pytesseract

text = pytesseract.image_to_string('../data/Image1/no_border.jpg')
text_without_empty_lines = ' '.join(line.strip() for line in text.splitlines() if line.strip())

print(text_without_empty_lines)


def normalize_string(s):
    return ''.join(s.split())


def calculate_accuracy(str1, str2):
    str1_normalized = normalize_string(str1)
    str2_normalized = normalize_string(str2)

    levenshtein_distance = Levenshtein.distance(str1_normalized, str2_normalized)

    max_length = max(len(str1_normalized), len(str2_normalized))
    accuracy = ((max_length - levenshtein_distance) / max_length) * 100

    return accuracy


ground_truth = ("Nutrition Facts Serving Size 1 Tbsp (15 mL) Servings Per Container About 64 Amount Per Serving "
                "Calories 0 Calories from Fat 0 % Daily Value* Total Fat 0g 0% Saturated Fat 0g 0% Trans Fat 0g "
                "Cholesterol 0mg 0% Sodium 0mg 0% Potassium 15mg 0% Total Carbohydrate 0g 0% Dietary Fiber 0g 0% "
                "Sugars 0g Protein 0g Vitamin A 0% Vitamin C 0% Calcium 0% Iron 0%")

ocr_output = text_without_empty_lines

accuracy = calculate_accuracy(ocr_output, ground_truth)

print(f"Accuracy: {accuracy:.2f}%")
