import json
import os
import sys
from baseline import read_receipt, extract

FIELDS = ["vendor", "invoice_no", "date", "subtotal", "tax", "total"]

method = sys.argv[1] if len(sys.argv) > 1 else "baseline"
if method == "llm":
    from llm_extract import extract_llm


def same(a, b):
    if a is None or b is None:
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 0.01
    return str(a).strip().lower() == str(b).strip().lower()


def clean_llm_output(result):
    if isinstance(result.get("invoice_no"), str):
        result["invoice_no"] = result["invoice_no"].replace(" ", "")
    if not isinstance(result.get("items"), list):
        result["items"] = []
    result["items"] = [i for i in result["items"] if isinstance(i, dict)]
    return result


def item_found(truth_item, predicted_items):
    for p in predicted_items:
        if (same(p.get("name"), truth_item["name"])
                and same(p.get("qty"), truth_item["qty"])
                and same(p.get("price"), truth_item["price"])
                and same(p.get("amount"), truth_item["amount"])):
            return True
    return False


field_correct = {field: 0 for field in FIELDS}
items_correct = 0
items_total = 0
receipts = 0

print("Method:", method)
for filename in sorted(os.listdir("data/labels")):
    if not filename.endswith(".json"):
        continue
    name = filename[:-5]
    image_path = "data/raw/" + name + ".jpg"
    if not os.path.exists(image_path):
        continue

    with open("data/labels/" + filename, encoding="utf-8") as f:
        truth = json.load(f)

    text = read_receipt(image_path)
    if method == "llm":
        predicted = clean_llm_output(extract_llm(name, text))
    else:
        predicted = extract(text)

    receipts += 1
    print("Receipt:", name)
    for field in FIELDS:
        if same(predicted.get(field), truth[field]):
            field_correct[field] += 1
        else:
            print("  WRONG", field, "- expected", truth[field], "got", predicted.get(field))
    for item in truth["items"]:
        items_total += 1
        if item_found(item, predicted["items"]):
            items_correct += 1
        else:
            print("  WRONG item - expected", item["name"], item["amount"])

print()
print("Method:", method)
print("Receipts evaluated:", receipts)
for field in FIELDS:
    print(field.ljust(12), str(round(100 * field_correct[field] / receipts)) + "%")
print("items".ljust(12), str(round(100 * items_correct / items_total)) + "%")