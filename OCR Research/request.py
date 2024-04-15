import requests

# Specify the URL of the API endpoint
url = "http://nutriscan.pythonanywhere.com/extract"  # Replace with your actual API URL

# Open the image file in binary mode
with open("D:/Documents/College/Year 3/OCR Research/OCR Research/data/Drive_images/21040_Dairygold Original - 63_ Fat Blended Spread_back.jpg", "rb") as img_file:
    # Prepare the image data
    img_data = {"img_path": img_file}

    # Send the POST request
    response = requests.post(url, files=img_data)

# Print the response
print(response.json())
