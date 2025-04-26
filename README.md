# Feature Engineering Service

## 🚀 Project Overview
This microservice transforms historical financial data into machine-learning-ready feature sets including RSI, EMA, MACD, and trend labels.

---

## 📂 Project Structure
- `app/` — Core logic: feature generation, pre-processing, labeling
- `scripts/dispatcher_cli.py` — Dispatcher CLI to automate runs
- `tests/` — Unit tests for all modules
- `.env.sample` — Environment variable template

---

## ⚙️ How to Run CLI
```bash
poetry run python scripts/dispatcher_cli.py --manifest ./data/manifest/historical_files.csv --feature-engineering-path ./data/filtered/ --output-dir ./data/features/
