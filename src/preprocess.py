import os
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = cv2.imread("data/raw/sample2.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
background = cv2.GaussianBlur(gray, (0, 0), 25)
flat = cv2.divide(gray, background, scale=255)
big = cv2.resize(flat, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
blur = cv2.GaussianBlur(big, (3, 3), 0)
_, clean = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

os.makedirs("data/processed", exist_ok=True)
cv2.imwrite("data/processed/sample2_clean.png", clean)

print(pytesseract.image_to_string(clean, config="--psm 6"))