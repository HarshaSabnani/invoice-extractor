import json
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(42)
rng = np.random.default_rng(42)

FONT_OPTIONS = [
    (r"C:\Windows\Fonts\cour.ttf", r"C:\Windows\Fonts\courbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
]
for regular_path, bold_path in FONT_OPTIONS:
    if os.path.exists(regular_path):
        REGULAR = ImageFont.truetype(regular_path, 26)
        BOLD = ImageFont.truetype(bold_path, 30)
        break

VENDORS = [
    "SUNRISE SUPERMART", "CITY MART", "GREEN LEAF GROCERS", "NEW INDIA PROVISIONS",
    "ROYAL KIRANA BAZAAR", "SHREE GANESH STORES", "MODERN MART",
    "DAILY NEEDS HYPERMART", "LUCKY GENERAL STORE", "METRO FRESH STORES",
]
ITEMS = [
    ("Basmati Rice 5kg", 520), ("Toor Dal 1kg", 165), ("Sunflower Oil 1L", 140),
    ("Tea Powder 500g", 95), ("Biscuits Pack", 25), ("Wheat Flour 5kg", 245),
    ("Sugar 1kg", 48), ("Salt 1kg", 22), ("Milk 1L", 60), ("Butter 100g", 58),
    ("Paneer 200g", 90), ("Curd 400g", 35), ("Maggi Noodles", 14),
    ("Bath Soap", 38), ("Shampoo 180ml", 165), ("Toothpaste 100g", 72),
    ("Detergent 1kg", 120), ("Dish Wash 500ml", 99), ("Mustard Oil 1L", 175),
    ("Red Chilli 100g", 45), ("Turmeric 100g", 40), ("Cashew 250g", 310),
    ("Coffee 200g", 285), ("Jam 500g", 150),
]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_receipt(layout):
    vendor = random.choice(VENDORS)
    number = random.randint(10000, 99999)
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    rate = random.choice([5, 12, 18])

    chosen = random.sample(ITEMS, random.randint(3, 7))
    items = []
    for name, price in chosen:
        qty = random.randint(1, 5)
        items.append({"name": name, "qty": qty, "price": float(price),
                      "amount": float(qty * price)})
    subtotal = round(sum(i["amount"] for i in items), 2)
    tax = round(subtotal * rate / 100, 2)
    total = round(subtotal + tax, 2)

    if layout == "A":
        invoice_text = "Invoice No : INV-" + str(number)
        date_text = "Date       : %02d/%02d/2026" % (day, month)
        sub_label, total_label = "Subtotal", "TOTAL"
    elif layout == "B":
        invoice_text = "Bill No    : B-" + str(number)
        date_text = "Date       : %02d-%02d-2026" % (day, month)
        sub_label, total_label = "Sub Total", "Grand Total"
    else:
        invoice_text = "Invoice #  : INV-" + str(number)
        date_text = "Date       : %02d %s 2026" % (day, MONTHS[month - 1])
        sub_label, total_label = "Subtotal", "TOTAL DUE"

    invoice_no = invoice_text.split(": ")[1]
    label = {
        "vendor": vendor,
        "invoice_no": invoice_no,
        "date": "%02d/%02d/2026" % (day, month),
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
    }

    rule = "-" * 37
    lines = [
        (vendor, BOLD, "c"),
        ("12 Market Road, Kanpur", REGULAR, "c"),
        (rule, REGULAR, "l"),
        (invoice_text, REGULAR, "l"),
        (date_text, REGULAR, "l"),
        (rule, REGULAR, "l"),
        ("ITEM            QTY    PRICE   AMOUNT", REGULAR, "l"),
        (rule, REGULAR, "l"),
    ]
    for item in items:
        row = (item["name"].ljust(16) + str(item["qty"]).rjust(3)
               + ("%.2f" % item["price"]).rjust(9) + ("%.2f" % item["amount"]).rjust(9))
        lines.append((row, REGULAR, "l"))
    lines.append((rule, REGULAR, "l"))
    lines.append((sub_label.ljust(37 - 9) + ("%.2f" % subtotal).rjust(9), REGULAR, "l"))
    lines.append((("GST %d%%" % rate).ljust(28) + ("%.2f" % tax).rjust(9), REGULAR, "l"))
    lines.append((total_label.ljust(37 - 9) + ("%.2f" % total).rjust(9), BOLD, "l"))
    lines.append((rule, REGULAR, "l"))
    lines.append(("Thank you! Visit again", REGULAR, "c"))
    return lines, label


def draw_receipt(lines):
    width, pad = 720, 30
    height = pad * 2 + sum(font.size + 14 for _, font, _ in lines)
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    y = pad
    for text, font, align in lines:
        x = (width - d.textlength(text, font=font)) / 2 if align == "c" else pad
        d.text((x, y), text, fill="black", font=font)
        y += font.size + 14
    return img


def make_photo_like(img):
    angle = random.uniform(-4, 4)
    img = img.rotate(angle, expand=True, fillcolor=(200, 200, 200), resample=Image.BICUBIC)
    a = np.asarray(img).astype("float32")
    h, w, _ = a.shape
    low = random.uniform(0.6, 0.9)
    gradient = np.linspace(low, 1.05, w)[None, :, None]
    if random.random() < 0.5:
        gradient = gradient[:, ::-1, :]
    a = a * gradient + rng.normal(0, random.uniform(6, 14), a.shape)
    a = np.clip(a, 0, 255).astype("uint8")
    return Image.fromarray(a).filter(ImageFilter.GaussianBlur(random.uniform(0.6, 1.2)))


os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/labels", exist_ok=True)

COUNT = 40
for n in range(1, COUNT + 1):
    layout = ["A", "B", "C"][n % 3]
    lines, label = build_receipt(layout)
    photo = make_photo_like(draw_receipt(lines))
    name = "synth_%03d" % n
    photo.save("data/raw/" + name + ".jpg", quality=random.randint(60, 85))
    with open("data/labels/" + name + ".json", "w", encoding="utf-8") as f:
        json.dump(label, f, indent=2)

print("Created", COUNT, "receipts in data/raw and data/labels")