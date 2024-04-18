# NutriScan

NutriScan is a Tkinter-based application that leverages AWS Textract's state-of-the-art OCR tool to extract nutritional
information from food labels and organizes them in a user-friendly table format.

[NutriScan Tutorial.mp4](Media%2FNutriScan%20Tutorial.mp4)

## Features

### Page 1: Image Selection and Editing

![Page 1.png](Media%2FPage%201.png)

![CropApp.png](Media%2FCropApp.png)

- **Select File Button**: Enables users to select a food label image from their local file system.
- **Drag & Drop Area**: Users can conveniently drag and drop their image into this area.
- **Crop Image Button**: Triggers the "Crop App" window, allowing users to crop the selected image. Displays an error
  message if no image is selected.
    - **Crop App Window**: Displays the selected image and an adjustable frame for cropping.
        - **Reset Button**: Resets the cropping frame to its initial position.
        - **Crop and Save Button**: Saves the cropped image for further use in the application and closes the popup
          window.
        - **Rotate Button**: Rotates the image by 90 degrees for better alignment.
- **Next Button**: Navigates to Page 2. Displays an error message if no image is selected.

### Page 2: Text Extraction & Data Management

![Page 2.png](Media%2FPage%202.png)

- **Back Button**: Allows users to navigate back to Page 1.
- **Image Frame**: Displays the selected or cropped image for reference.
- **Table**: Displays the extracted text with columns for "Nutrient", "Value", and "Confidence Score". Highlights rows
  with a confidence score below 90 for attention. Values can be edited by double-clicking or using the edit button.
- **Export CSV Button**: Exports the current table data (including any edits) as a CSV file.
- **Append CSV Button**: Adds the extracted data (excluding the confidence score) to an SQLite database. Each time text
  is extracted from a different label, it appends to the database.
- **Export Append CSV Button**: Exports the SQLite database data into a CSV file.

## Installation

1. **Download the Release Source Zip**:
    - Navigate to the GitHub repository at [https://github.com/Divyanshu411/comparing_ocr_tools/releases/tag/v1.1.0](https://github.com/Divyanshu411/comparing_ocr_tools/releases/tag/v1.1.0).
    - Click and download "Source code (zip)" to download software.

2. **Access the OCR Research GUI**:
    - After downloading, extract the contents of the zip file to a convenient location on your system.
    - Navigate to the extracted directory.
    - Head to the "_OCR research/GUI/dist_" directory within the extracted files.

3. **Configure AWS Credentials**:
    - Locate the `aws_credential.json` file in the project directory.
    - Edit this file with your own AWS credentials.
    - If you don’t have AWS credentials yet, follow these steps or this video:
        1. **Create an AWS Account**:
            - Visit AWS Signup and create an account using
              this [link](https://portal.aws.amazon.com/billing/signup?type=enterprise#/start/email).
        2. **Create an IAM User**:
            - Watch a tutorial to learn how to create an IAM user with appropriate permissions.
        3. **Update Credentials**:
            - Once you have the credentials, update the `aws_credential.json` file with the `access key` and `secret access key`.

4. **Run Nutriscan**:
    - Execute the `Nutriscan.exe` file.
    - Your Nutriscan application should now be up and running!

## Usage

1. On Page 1, select or drag and drop your food label image.
2. Use the Crop Image button to crop your image as needed.
3. Click the Next button to proceed to Page 2.
4. On Page 2, review the extracted text in the table. Edit values as needed.
5. Use the Export CSV button to save your table as a CSV file.
6. Use the Append CSV button to add your data to the SQLite database.
7. Use the Export Append CSV button to export your SQLite database to a CSV file.
