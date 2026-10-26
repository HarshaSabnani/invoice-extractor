import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"
CACHE_DIR = "data/llm_cache"

PROMPT = """You extract data from receipt text produced by OCR. The text may contain OCR mistakes.

Return one JSON object with exactly these keys:
- vendor: the shop name as a clean string, without stray punctuation
- invoice_no: the invoice or bill number as printed (for example INV-12345 or B-12345)
- date: the date converted to DD/MM/YYYY
- items: a list of objects with name (string), qty (integer), price (number), amount (number)
- subtotal: number
- tax: number
- total: number

Rules:
- Copy numbers exactly as they appear in the text. Do not correct them and do not calculate anything.
- Use null for anything that is missing.
- Do not invent items or values.

Receipt text:
"""


def call_llm(text):
    for attempt in range(1, 6):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=PROMPT + text,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
            return json.loads(response.text)
        except errors.APIError as error:
            if error.code in (429, 503) and attempt < 5:
                wait = attempt * 10
                print("  busy (error %s), retrying in %s seconds" % (error.code, wait))
                time.sleep(wait)
            else:
                raise


def extract_llm(name, text):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, MODEL + "__" + name + ".json")
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    result = call_llm(text)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    from baseline import read_receipt

    text = read_receipt("data/raw/sample2.jpg")
    print(json.dumps(extract_llm("sample2", text), indent=2))