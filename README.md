# Invoice Extractor

Extracts structured data (vendor, invoice number, date, line items, subtotal, tax, total) from receipt and invoice images using OCR, with an LLM-based stage coming next.

**Status:** work in progress (Week 1 of 4)

## What works so far

- Image preprocessing (grayscale, lighting correction, upscaling, thresholding) to improve OCR on phone photos
- Rule-based baseline extractor that outputs JSON
- Synthetic receipt generator: 40 receipts in 3 different layouts, rendered as tilted, shadowed, noisy "phone photos", each with an automatically generated answer file
- Evaluation script that compares extracted output with the ground truth, field by field

## Baseline results

Evaluated on 42 receipts (40 synthetic across 3 layouts + 2 hand-made samples).

| Field | Accuracy |
|---|---|
| Vendor | 71% |
| Invoice number | 64% |
| Date | 36% |
| Subtotal | 52% |
| Tax | 86% |
| Total | 55% |
| Line items | 69% |

What the errors show:

- The rules only understand one layout. Receipts that say "Bill No", "Sub Total", or "Grand Total", or write dates like `21-03-2026` or `08 Aug 2026`, mostly return nothing.
- OCR noise adds stray characters to vendor names and drops or misreads digits in prices.

The next stage (LLM-based extraction plus validation rules) is aimed at exactly these failures.

## Data note

The test receipts are synthetic. They are useful for fast, repeatable measurement, but they are cleaner than real-world receipts, so these numbers should not be read as real-world accuracy. Evaluation on real receipts is planned.

## Project structure

```
data/raw/        receipt images
data/labels/     ground-truth JSON for each image
data/processed/  preprocessed images
src/             OCR, baseline extractor, evaluation, data generator
```

## Setup (Windows)

1. Install Python 3.11 and [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Create and activate a virtual environment, then run `pip install -r requirements.txt`
3. Run `python src\generate_data.py` to create the test receipts
4. Run `python src\baseline.py` to extract one receipt, or `python src\evaluate.py` to measure accuracy

## Roadmap

- [x] Preprocessing, baseline extractor, and evaluation script
- [x] Larger labelled test set (synthetic)
- [ ] Add real receipts to the test set
- [ ] LLM-based extraction, compared against the baseline
- [ ] Validation rules (quantity x price = amount, items add up to subtotal)
- [ ] FastAPI endpoint, Docker, and a live demo