# Hands-On Assignment 4: Fraud Detection Using PyOD AutoEncoder

**Course:** MSCS-633-M20 — Advance Artificial Intelligence  
**Student:** Xhon Pelushi  
**University:** University of the Cumberlands

## Overview

This project implements a credit card fraud detection system using PyOD's
AutoEncoder model. The AutoEncoder learns normal transaction patterns through
reconstruction and flags anomalies (potential fraud) based on high
reconstruction error.

## How It Works

1. **Data Generation** — Creates a synthetic credit card transaction dataset
   with 5,050 transactions (0.99% fraud rate), featuring 28 PCA-transformed
   features and a transaction amount.
2. **Preprocessing** — Standardizes all features using StandardScaler and
   splits into 70/30 train/test sets.
3. **AutoEncoder Training** — Trains a neural network with encoder layers
   [64, 32, 16] that compresses inputs to a bottleneck representation and
   reconstructs the original features.
4. **Anomaly Detection** — Transactions with high reconstruction error are
   flagged as fraudulent.
5. **Evaluation** — Generates classification report, confusion matrix, ROC
   curve, and precision-recall curve.

## Results

- **ROC AUC Score:** 1.0000
- **Average Precision:** 1.0000
- **Fraud Recall:** 100% (all 15 test fraud cases detected)
- **False Positives:** 1 (out of 1,500 normal transactions)

## Files

| File | Description |
|------|-------------|
| `fraud_detection.py` | Main Python script |
| `requirements.txt` | Python dependencies |
| `fraud_detection_results.png` | Evaluation visualizations |
| `screenshot_output.png` | Terminal output screenshot |
| `Hands-On Assignment 4 - Fraud Detection with PyOD.docx` | Assignment report |

## Running

```bash
pip install -r requirements.txt
python fraud_detection.py
```
