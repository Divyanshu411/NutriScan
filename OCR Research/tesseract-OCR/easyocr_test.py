import easyocr

reader = easyocr.Reader(['en']) 
result = reader.readtext('image.jpg')

for (bbox, text, prob) in result:
    print(f'Text: {text}, Probability: {prob}')