import re

CONFUSABLE_TO_DIGIT = {"l": "1", "I": "1", "|": "1", "S": "5", "O": "0", "o": "0"}
STANDARD_TAX_RATES = [0, 5, 12, 18, 28]
UNIT_TOKEN = re.compile(r"^([0-9lI|SOo]+)(kg|ml|g|9|l|L)$")


def fix_unit_token(token):
    match = UNIT_TOKEN.match(token)
    if not match:
        return token
    number_part, unit = match.groups()
    has_real_digit = any(ch.isdigit() for ch in number_part)

    if unit in ("l", "L"):
        if not has_real_digit:
            return token
        unit = "L"
    elif unit == "9":
        if not (number_part.isdigit() and len(number_part) >= 2):
            return token
        unit = "g"

    digits = "".join(CONFUSABLE_TO_DIGIT.get(ch, ch) for ch in number_part)
    return digits + unit


def fix_item_name(name):
    return " ".join(fix_unit_token(token) for token in name.split(" "))


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def matches_standard_rate(tax_amount, subtotal):
    return any(abs(tax_amount - subtotal * r / 100) <= 0.011 for r in STANDARD_TAX_RATES)


def clean(result):
    fixes = []
    items = result.get("items") or []

    for item in items:
        name = item.get("name")
        if isinstance(name, str):
            new_name = fix_item_name(name)
            if new_name != name:
                fixes.append("item name '%s' -> '%s'" % (name, new_name))
                item["name"] = new_name

        qty, price, amount = item.get("qty"), item.get("price"), item.get("amount")
        if not (is_number(price) and is_number(amount)) or price <= 0:
            continue

        guess = round(amount / price)
        if not is_number(qty) or qty <= 0:
            if guess > 0 and abs(guess * price - amount) < 0.01:
                item["qty"] = int(guess)
                fixes.append("'%s': filled missing qty with %d" % (item.get("name"), guess))
        elif abs(qty * price - amount) > 0.01:
            if guess > 0 and abs(guess * price - amount) < 0.01:
                item["qty"] = int(guess)
                fixes.append("'%s': qty %s -> %d" % (item.get("name"), qty, guess))
            else:
                new_amount = round(qty * price, 2)
                fixes.append("'%s': amount %s -> %s" % (item.get("name"), amount, new_amount))
                item["amount"] = new_amount

    amounts = [i.get("amount") for i in items]
    if amounts and all(is_number(a) for a in amounts):
        items_sum = round(sum(amounts), 2)
        subtotal = result.get("subtotal")
        if not is_number(subtotal) or abs(subtotal - items_sum) > 0.01:
            fixes.append("subtotal %s -> %s (sum of items)" % (subtotal, items_sum))
            result["subtotal"] = items_sum

    subtotal, tax, total = result.get("subtotal"), result.get("tax"), result.get("total")
    if is_number(subtotal) and subtotal > 0:
        if is_number(total) and not is_number(tax):
            result["tax"] = round(total - subtotal, 2)
            fixes.append("filled missing tax with %s" % result["tax"])
        elif is_number(tax) and not is_number(total):
            result["total"] = round(subtotal + tax, 2)
            fixes.append("filled missing total with %s" % result["total"])
        elif is_number(tax) and is_number(total) and abs(subtotal + tax - total) > 0.01:
            if matches_standard_rate(total - subtotal, subtotal):
                fixes.append("tax %s -> %s (total minus subtotal)" % (tax, round(total - subtotal, 2)))
                result["tax"] = round(total - subtotal, 2)
            elif matches_standard_rate(tax, subtotal):
                fixes.append("total %s -> %s (subtotal plus tax)" % (total, round(subtotal + tax, 2)))
                result["total"] = round(subtotal + tax, 2)
            else:
                fixes.append("WARNING: subtotal + tax does not equal total")

    result["corrections"] = fixes
    return result