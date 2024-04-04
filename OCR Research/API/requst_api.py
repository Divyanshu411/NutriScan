import requests
import datetime

response = requests.post(
    'https://ocrextraction.pythonanywhere.com/extract',
    json={
        'img_path': 'D:/Documents/College/Year 3/OCR Research/OCR Research/data/Drive_images/21040_Dairygold '
                    'Original - 63_ Fat Blended Spread_back.jpg'}
)

print(response.json())
