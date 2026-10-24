import json
import re
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def read_receipt(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    background = cv2.GaussianBlur(gray, (0, 0), 25)
    flat = cv2.divide(gray, background, scale=255)
    big = cv2.resize(flat, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(big, (3, 3), 0)
    _, clean = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(clean, config="--psm 6")


def to_number(text):
    cleaned = text.replace(" ", "")
    match = re.search(r"\d+\.\d{2}", cleaned)
    return float(match.group()) if match else None


def extract(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = {
        "vendor": lines[0] if lines else None,
        "invoice_no": None,
        "date": None,
        "items": [],
        "subtotal": None,
        "tax": None,
        "total": None,
    }
    for line in lines:
        upper = line.upper()

        match = re.search(r"INV\s*-?\s*(\d+)", upper)
        if match:
            result["invoice_no"] = "INV-" + match.group(1)

        match = re.search(r"\d{2}/\d{2}/\d{4}", line)
        if match:
            result["date"] = match.group()

        if upper.startswith("SUBTOTAL"):
            value = to_number(line)
            if value is not None:
                result["subtotal"] = value
        elif upper.startswith("GST"):
            value = to_number(line)
            if value is not None:
                result["tax"] = value
        elif upper.startswith("TOTAL"):
            value = to_number(line)
            if value is not None:
                result["total"] = value
        else:
            match = re.match(r"^(.+?)\s+(\d+)\s+(\d+\.\d{2})\s+(\d+\.\d{2})$", line)
            if match:
                result["items"].append({
                    "name": match.group(1),
                    "qty": int(match.group(2)),
                    "price": float(match.group(3)),
                    "amount": float(match.group(4)),
                })
    return result


if __name__ == "__main__":
    text = read_receipt("data/raw/sample2.jpg")
    print(json.dumps(extract(text), indent=2))