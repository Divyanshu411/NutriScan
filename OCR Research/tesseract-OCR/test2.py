import cv2
from PIL import Image
import pytesseract
import numpy as np

im_file = "../data/Image2/image_2.jpg"
img = cv2.imread(im_file)

# Inverted --------------
inverted_image = cv2.bitwise_not(img)
cv2.imwrite("../data/Image2/inverted.jpeg", inverted_image)


# im = Image.open("data/inverted.jpeg")
# im.show()


# Grayscale -------------
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


gray_image = grayscale(img)
cv2.imwrite("../data/Image2/grayscale.jpeg", gray_image)

# im = Image.open("data/grayscale.jpeg")
# im.show()

# Binarization ---------------
thresh, im_bw = cv2.threshold(gray_image, 165, 250, cv2.THRESH_BINARY)
cv2.imwrite("../data/Image2/bw_image.jpeg", im_bw)

# im = Image.open("data/Image2/bw_image.jpeg")
# im.show()


# Noise reduction ---------------
def noise_removal(image):
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return image


no_noise = noise_removal(im_bw)
cv2.imwrite("../data/Image2/no_noise.jpeg", no_noise)

# im = Image.open("data/Image2/no_noise.jpeg")
# im.show()


# Erosion ---------------
def thin_font(image):
    image = cv2.bitwise_not(image)
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return image


eroded_image = thin_font(no_noise)
cv2.imwrite("../data/Image2/erroded_image.jpeg", eroded_image)

# im = Image.open("data/Image2/erroded_image.jpeg")
# im.show()


# Dilation ---------------
def thick_font(image):
    image = cv2.bitwise_not(image)
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return image


dilated_image = thick_font(no_noise)
cv2.imwrite("../data/Image2/dilated_image.jpeg", dilated_image)

# im = Image.open("data/Image2/dilated_image.jpeg")
# im.show()


# Rotation
def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        cv2.rectangle(newImage, (x, y), (x + w, y + h), (0, 255, 0), 2)

    largestContour = contours[0]
    print(len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    cv2.imwrite("../data/Image2/boxes.jpg", newImage)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = cvImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage


def deskew(cvImage):
    angle = getSkewAngle(cvImage)
    return rotateImage(cvImage, -1.0 * angle)


fixed = deskew(img)
cv2.imwrite("../data/Image2/rotation_fixed.jpg", fixed)

# im = Image.open("data/Image2/rotation_fixed.jpg")
# im.show()


# Removing border
def remove_border(image):
    contours, heirarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntSorted = sorted(contours, key=lambda x: cv2.contourArea(x))
    cnt = cntSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y + h, x:x + w]
    return crop


no_border = remove_border(im_bw)
cv2.imwrite("../data/Image2/no_border.jpg", no_border)

text = pytesseract.image_to_string(img)
# Print the extracted text
print(text)

# im = Image.open("data/no_border.jpg")
# im.show()

color = [255, 255, 255]
top, bottom, left, right = [150] * 4

# image_with_border = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
# cv2.imwrite("data/Image2/with_border.jpg", image_with_border)

# im = Image.open("data/with_border.jpg")
# im.show()
