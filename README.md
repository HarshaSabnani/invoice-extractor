# Invoice Extractor

Extracts structured data (vendor, invoice number, date, line items, subtotal, tax, total) from receipt and invoice images using OCR, with an LLM-based stage coming next.

**Status:** work in progress (Week 1 of 4)

## What works so far

- Image preprocessing (grayscale, lighting correction, upscaling, thresholding) to improve OCR on phone photos
- Rule-based baseline extractor that outputs JSON
- Evaluation script that compares extracted output with hand-labelled ground truth

## Baseline results

Early numbers on a tiny test set (2 images). A larger test set is coming.

| Field | Accuracy |
|---|---|
| Vendor | 100% |
| Invoice number | 100% |
| Date | 100% |
| Subtotal | 50% |
| Tax | 100% |
| Total | 50% |
| Line items | 50% |

Most errors come from OCR misreading digits (for example 1344.00 read as 1344.66).

## Project structure

```
data/raw/        sample receipt images
data/labels/     ground-truth JSON for each image
data/processed/  preprocessed images
src/             OCR, baseline extractor, evaluation
```

## Setup (Windows)

1. Install Python 3.11 and [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Create and activate a virtual environment, then run `pip install -r requirements.txt`
3. Run `python src\baseline.py` to extract one receipt, or `python src\evaluate.py` to measure accuracy

## Roadmap

- [ ] Larger labelled test set (30-50 receipts)
- [ ] LLM-based extraction, compared against the baseline
- [ ] Validation rules (quantity x price = amount, items add up to subtotal)
- [ ] FastAPI endpoint, Docker, and a live demo