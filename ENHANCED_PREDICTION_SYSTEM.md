# Enhanced Cryptocurrency Prediction System

## Overview
The enhanced prediction system now supports dual-model predictions with live data fetching from multiple sources.

## Features Implemented

### 1. Enhanced User Input
- **Days Ahead (0-30)**: Users can specify how many days ahead to predict
- **Hours Ahead (0-23)**: Users can specify how many hours ahead to predict
- **Optional Current Price**: Auto-fetches current price if not provided

### 2. Live Data Fetching
- **Yahoo Finance**: Fetches 60 days of daily OHLCV data
- **Binance API**: Fetches 60 hours of hourly OHLCV data
- **CoinDesk API**: Gets current Bitcoin price (configurable via .env)

### 3. Dual Model System
- **Daily Predictions**: Uses LSTM models trained on daily data, outputs in INR
- **Hourly Predictions**: Uses LSTM models trained on hourly data, outputs in USDT
- **Fallback System**: Provides statistical predictions if models are unavailable

### 4. Supported Cryptocurrencies
- Bitcoin (BTC)
- Ethereum (ETH)
- Cardano (ADA)
- Binance Coin (BNB)
- XRP (XRP)
- Solana (SOL)
- Dogecoin (DOGE)
- Litecoin (LTC)
- Polygon (MATIC)

## API Endpoints

### Enhanced Prediction Endpoint
```
POST /api/predict/{symbol}
```

**Request Body:**
```json
{
  "symbol": "BTC",
  "days_ahead": 1,
  "hours_ahead": 2,
  "current_price": 50000.0  // optional
}
```

**Response:**
```json
{
  "symbol": "BTC",
  "timestamp": "2025-09-09T21:37:03.902574",
  "current_price": 50000.0,
  "daily_prediction": {
    "predicted_price": 3.63,
    "currency": "INR",
    "days_ahead": 1,
    "model_type": "daily_lstm"
  },
  "hourly_prediction": {
    "predicted_price": 1.03,
    "currency": "USDT", 
    "hours_ahead": 2,
    "model_type": "hourly_lstm"
  }
}
```

## Configuration

### Environment Variables (config.env)
```env
# CoinDesk API Configuration
COINDESK_API_KEY=your_coindesk_api_key_here
COINDESK_API_URL=https://api.coindesk.com/v1/bpi/currentprice.json

# Data fetching limits
YAHOO_FINANCE_DAYS_LIMIT=60
BINANCE_HOURS_LIMIT=60
DAYS_AHEAD_MAX=30
HOURS_AHEAD_MAX=23

# Model configuration
DAILY_MODEL_CURRENCY=INR
HOURLY_MODEL_CURRENCY=USDT
```

## Frontend Updates

### New Input Fields
- Days Ahead slider (0-30)
- Hours Ahead slider (0-23)
- Optional current price input

### Enhanced Results Display
- Separate cards for daily (INR) and hourly (USDT) predictions
- Dynamic forecast ranges based on predictions
- Loading states and error handling

## Technical Implementation

### Data Sources
1. **Yahoo Finance**: Daily OHLCV data via yfinance library
2. **Binance API**: Hourly OHLCV data via REST API
3. **CoinDesk API**: Real-time Bitcoin price

### Model Integration
- Automatic model loading with aliasing
- Input sequence preparation (60 timesteps)
- Dual prediction pipeline
- Fallback statistical predictions

### Error Handling
- API timeout and retry logic
- Data validation and sanitization
- Graceful degradation to fallback predictions

## Usage

1. **Start the server:**
   ```bash
   PORT=5050 python3 app.py
   ```

2. **Access the frontend:**
   ```
   http://127.0.0.1:5050/predictions.html
   ```

3. **Select cryptocurrency and timeframes:**
   - Choose from dropdown
   - Set days ahead (0-30)
   - Set hours ahead (0-23)
   - Optionally enter current price

4. **Generate predictions:**
   - Click "Generate Prediction"
   - View both daily (INR) and hourly (USDT) results

## Testing

The system has been tested with:
- ✅ BTC daily and hourly predictions
- ✅ ETH daily and hourly predictions  
- ✅ ADA daily and hourly predictions
- ✅ BNB daily and hourly predictions
- ✅ Live data fetching from Yahoo Finance and Binance
- ✅ Frontend integration and UI updates

## Dependencies

```
flask==3.0.3
numpy
joblib==1.4.2
pandas
yfinance
python-dotenv
requests
tensorflow==2.12.0
keras==3.4.1
```

## Next Steps

1. Add CoinDesk API key to config.env for Bitcoin price fetching
2. Implement prediction confidence intervals
3. Add historical prediction accuracy tracking
4. Implement prediction caching for performance
5. Add more cryptocurrency support as models become available
