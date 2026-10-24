import json
import os
from baseline import read_receipt, extract

FIELDS = ["vendor", "invoice_no", "date", "subtotal", "tax", "total"]


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 0.01
    return str(a).strip().lower() == str(b).strip().lower()


def item_found(truth_item, predicted_items):
    for p in predicted_items:
        if (same(p["name"], truth_item["name"])
                and p["qty"] == truth_item["qty"]
                and same(p["price"], truth_item["price"])
                and same(p["amount"], truth_item["amount"])):
            return True
    return False


field_correct = {field: 0 for field in FIELDS}
items_correct = 0
items_total = 0
receipts = 0

for filename in sorted(os.listdir("data/labels")):
    if not filename.endswith(".json"):
        continue
    name = filename[:-5]
    image_path = "data/raw/" + name + ".jpg"
    if not os.path.exists(image_path):
        continue

    with open("data/labels/" + filename, encoding="utf-8") as f:
        truth = json.load(f)
    predicted = extract(read_receipt(image_path))

    receipts += 1
    print("Receipt:", name)
    for field in FIELDS:
        if same(predicted[field], truth[field]):
            field_correct[field] += 1
        else:
            print("  WRONG", field, "- expected", truth[field], "got", predicted[field])
    for item in truth["items"]:
        items_total += 1
        if item_found(item, predicted["items"]):
            items_correct += 1
        else:
            print("  WRONG item - expected", item["name"], item["amount"])

print()
print("Receipts evaluated:", receipts)
for field in FIELDS:
    print(field.ljust(12), str(round(100 * field_correct[field] / receipts)) + "%")
print("items".ljust(12), str(round(100 * items_correct / items_total)) + "%")