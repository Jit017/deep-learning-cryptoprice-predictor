# Milestone 1: Cryptocurrency Data Collection

This folder contains scripts and datasets for fetching and organizing cryptocurrency data.

## Files Overview

### Scripts
- `fetch_bitcoin_data.py` - Fetches daily and hourly Bitcoin data (BTC-USD)
- `fetch_crypto_hourly_data.py` - Fetches hourly data for 6 major cryptocurrencies (yfinance)
- `convert_to_inr.py` - Converts USD-quoted OHLC to INR with historical USD/INR
- `fetch_crypto_hourly_inr_full.py` - Multi-API hourly INR fetcher (CryptoCompare)
- `fetch_extended_hourly_inr.py` - Extended hourly INR using free APIs only
- `fetch_coindesk_hourly_inr.py` - (experimental) CoinDesk integration

### Datasets (INR)
- `crypto_daily_data_inr.csv` - Daily data (6 cryptos) in INR
- `crypto_hourly_data_inr.csv` - Hourly data (6 cryptos) in INR (yfinance, ~2 years)
- `crypto_hourly_inr_max.csv` - Max yfinance hourly INR (2 years)
- `bitcoin_data_inr.csv`, `bitcoin_hourly_data_inr.csv` - BTC daily/hourly in INR
- `crypto_hourly_inr_merged.csv` - MERGED hourly INR for 7 cryptos you provided
  - Symbols merged: ADA, BNB, BTC, DOGE, ETH, SOL, XRP
  - Columns: `Datetime, Open, High, Low, Close, Volume, Symbol, Currency`
  - Sorted by `Datetime` and `Symbol`, OHLC non-negative

### Raw hourly INR files you added (merged above)
- `BTCUSDT_hourly_INR.csv`
- `ETHUSDT_hourly_INR.csv`
- `XRPUSDT_hourly_INR.csv`
- `ADAUSDT_hourly_INR.csv`
- `BNBUSDT_hourly_INR.csv`
- `SOLUSDT_hourly_INR.csv`
- `DOGE_hourly_inr.csv`

## Coverage summary (from merged file)
- BTC: 2017-08-17 04:00:00+00:00 → 2025-08-26 08:00:00+00:00 (70,221 rows)
- ETH: 2017-08-17 04:00:00+00:00 → 2025-08-26 08:00:00+00:00 (70,221)
- XRP: 2018-05-04 08:00:00+00:00 → 2025-08-26 08:00:00+00:00 (64,017)
- ADA: 2018-04-17 04:00:00+00:00 → 2025-08-26 08:00:00+00:00 (64,429)
- BNB: 2017-11-06 03:00:00+00:00 → 2025-08-26 08:00:00+00:00 (68,284)
- SOL: 2020-08-11 06:00:00+00:00 → 2025-08-26 08:00:00+00:00 (44,167)
- DOGE: 2023-08-28 00:00:00+00:00 → 2025-08-26 09:00:00+00:00 (17,497)

Notes:
- No duplicate hourly timestamps detected per symbol.
- Small gaps exist (typical exchange/API maintenance). If strict continuity is needed, we can forward-fill missing hours and mark `Filled=true`.

## Data Format
All CSV files contain OHLCV data with columns:
- Daily: `Date, Open, High, Low, Close, Volume, Symbol`
- Hourly: `Datetime, Open, High, Low, Close, Volume, Symbol, Currency`

## Usage
```bash
# Fetch Bitcoin data (daily + hourly)
python3 fetch_bitcoin_data.py

# Fetch hourly data for 6 cryptocurrencies (yfinance)
python3 fetch_crypto_hourly_data.py

# Convert existing USD CSVs to INR
python3 convert_to_inr.py

# Extended hourly INR (free APIs)
python3 fetch_extended_hourly_inr.py

# Full-history hourly INR with checkpointing (CryptoCompare paging)
python3 fetch_crypto_hourly_inr_full.py
```

## Data Sources
- Yahoo Finance via yfinance
- CryptoCompare histohour endpoint (free)
- Binance klines (as fallback)
- USD/INR rates via exchangerate-api
