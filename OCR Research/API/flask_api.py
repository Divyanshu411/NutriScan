from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from OCR_extraction import process_image
import pandas as pd
import os

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_nutritional_info():
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
            process_image(file_path)
            extracted_data = pd.read_csv('nutritional_info.csv')
            data_dict = dict(zip(extracted_data['Nutrient'], extracted_data['Value']))
            os.remove(file_path)
            return jsonify({'data': data_dict})
        except Exception as e:
            return jsonify({'error': str(e)})


if __name__ == "__main__":
    app.run(debug=True)
