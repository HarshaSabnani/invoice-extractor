import difflib
import json
import os
from collections import Counter

MODEL = "gemini-3.1-flash-lite"

counts = Counter()
examples = []


def number_equal(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return False
    return abs(a - b) < 0.01


for filename in sorted(os.listdir("data/labels")):
    name = filename[:-5]
    cache_path = "data/llm_cache/" + MODEL + "__" + name + ".json"
    if not os.path.exists(cache_path):
        continue
    with open("data/labels/" + filename, encoding="utf-8") as f:
        truth = json.load(f)
    with open(cache_path, encoding="utf-8") as f:
        predicted = json.load(f)

    items = predicted.get("items") or []
    items = [i for i in items if isinstance(i, dict)]

    for p in items:
        try:
            if abs(p["qty"] * p["price"] - p["amount"]) > 0.01:
                counts["extracted rows where qty x price does not equal amount"] += 1
        except (KeyError, TypeError):
            counts["extracted rows with missing numbers"] += 1

    for t in truth["items"]:
        counts["expected items"] += 1
        exact = False
        best, best_score = None, 0
        for p in items:
            same_name = str(p.get("name")).lower() == t["name"].lower()
            if (same_name and number_equal(p.get("qty"), t["qty"])
                    and number_equal(p.get("price"), t["price"])
                    and number_equal(p.get("amount"), t["amount"])):
                exact = True
                break
            score = difflib.SequenceMatcher(None, str(p.get("name")).lower(), t["name"].lower()).ratio()
            if score > best_score:
                best, best_score = p, score
        if exact:
            counts["correct"] += 1
            continue
        if best is None or best_score < 0.6:
            counts["item not found at all"] += 1
            examples.append(name + ": expected " + t["name"] + " - nothing similar extracted")
            continue
        problems = []
        if str(best.get("name")).lower() != t["name"].lower():
            problems.append("name")
        for key in ("qty", "price", "amount"):
            if not number_equal(best.get(key), t[key]):
                problems.append(key)
        counts["wrong: " + " + ".join(problems)] += 1
        examples.append(
            name + ": expected " + t["name"] + " | " + str(t["qty"]) + " | " + str(t["price"]) + " | " + str(t["amount"])
            + "   got " + str(best.get("name")) + " | " + str(best.get("qty")) + " | " + str(best.get("price")) + " | " + str(best.get("amount"))
        )

print("SUMMARY")
for label, number in counts.most_common():
    print(" ", number, "x", label)
print()
print("EXAMPLES (first 15)")
for line in examples[:15]:
    print(" ", line)