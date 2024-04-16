from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from OCR_extraction import process_image  # Importing OCR extraction function
import pandas as pd
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/extract', methods=['POST'])
def extract_nutritional_info():
    """
    Endpoint to extract nutritional information from an image file.
    """
    if 'img_path' not in request.files:
        return jsonify({'error': 'No image file provided'})

    file = request.files['img_path']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(filename)
            file.save(file_path)

            # Process the image to extract nutritional information
            process_image(file_path)

            # Read the extracted data from the CSV file
            extracted_data = pd.read_csv('nutritional_info.csv')

            # Convert the data to a dictionary for JSON serialization
            data_dict = dict(zip(extracted_data['Nutrient'], extracted_data['Value']))

            # Remove the temporary image file
            os.remove(file_path)

            return jsonify({'data': data_dict})
        except Exception as e:
            return jsonify({'error': str(e)})
