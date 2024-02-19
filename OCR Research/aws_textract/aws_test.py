import boto3
import pandas as pd

client = boto3.client('aws_textract', region_name='us-east-1', aws_access_key_id='AKIATCKATOWRRSB6E5P7',
                      aws_secret_access_key='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')

from PIL import Image

image = Image.open("../data/Image1/download.jpeg")

with open('../data/Image1/download.jpeg', 'rb') as image:
    img = bytearray(image.read())

response = client.detect_document_text(
    Document={'Bytes': img}
)

text = ""
for item in response["Blocks"]:
    if item["BlockType"] == "LINE":
        print(item["Text"])
        text = text + " " + item["Text"]

print(text)

comprehend_client = boto3.client('comprehend', region_name='us-east-1', aws_access_key_id='AKIATCKATOWRRSB6E5P7',
                                 aws_secret_access_key='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')
response = comprehend_client.detect_entities(Text=text, LanguageCode='en')
pd.DataFrame(response['Entities'])
