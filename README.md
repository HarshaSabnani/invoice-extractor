# Invoice Extractor

Extracts structured data (vendor, invoice number, date, line items, subtotal, tax, total) from receipt and invoice images using OCR, an LLM, and validation rules.

**Status:** work in progress (Week 1 of 4)

## What works so far

- Image preprocessing (grayscale, lighting correction, upscaling, thresholding) to improve OCR on phone photos
- Rule-based baseline extractor that outputs JSON
- LLM-based extractor that reads the OCR text and returns structured JSON
- Validation rules that fix common errors (quantity x price = amount, items add up to subtotal, subtotal + tax = total, OCR unit mistakes like `1kg` read as `lkg`)
- Synthetic receipt generator: 40 receipts in 3 different layouts, rendered as tilted, shadowed, noisy "phone photos", each with an automatically generated answer file
- Evaluation script that compares extracted output with the ground truth, field by field, for all three methods

## Results (42 receipts)

Evaluated on 42 receipts (40 synthetic across 3 layouts + 2 hand-made samples).

| Field | Baseline (regex) | LLM only | LLM + rules |
|---|---|---|---|
| Vendor | 71% | 100% | 100% |
| Invoice number | 64% | 100% | 100% |
| Date | 36% | 100% | 100% |
| Subtotal | 52% | 98% | 98% |
| Tax | 86% | 98% | 100% |
| Total | 55% | 98% | 100% |
| Line items | 69% | 82% | 96% |

What the results show:

- The regex baseline only understands one layout. Receipts that say "Bill No", "Sub Total", or "Grand Total", or write dates like `21-03-2026` or `08 Aug 2026`, mostly return nothing.
- The LLM fixes most of those layout failures. Vendor, invoice number, and date reach 100%.
- The validation rules improve line items from 82% to 96% and fix the remaining tax and total errors.

Known issues:

- On one receipt (`synth_028`), the rules change a correct subtotal into a wrong one. This is still to be fixed.
- Most remaining line-item errors are on items whose names contain units such as `1kg` or `1L`.

## Data note

The test receipts are synthetic. They are useful for fast, repeatable measurement, but they are cleaner than real-world receipts, so these numbers should not be read as real-world accuracy. Evaluation on real receipts is planned.

## Project structure

```
data/raw/        receipt images
data/labels/     ground-truth JSON for each image
data/processed/  preprocessed images
src/             OCR, baseline extractor, LLM extractor, validation rules, evaluation, data generator
```

## Setup (Windows)

1. Install Python 3.11 and [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Create and activate a virtual environment, then run `pip install -r requirements.txt`
3. Run `python src\generate_data.py` to create the test receipts
4. Run `python src\baseline.py` to extract one receipt
5. Measure accuracy with any of the three methods:

```
python src\evaluate.py baseline
python src\evaluate.py llm
python src\evaluate.py llm+rules
```

## Roadmap

- [x] Preprocessing, baseline extractor, and evaluation script
- [x] Larger labelled test set (synthetic)
- [x] LLM-based extraction, compared against the baseline
- [x] Validation rules (quantity x price = amount, items add up to subtotal)
- [ ] Add real receipts to the test set
- [ ] FastAPI endpoint, Docker, and a live demo