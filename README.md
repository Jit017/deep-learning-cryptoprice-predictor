# 🚀 Crypto Prediction System

A comprehensive machine learning-powered web platform for cryptocurrency price forecasting using LSTM neural networks. This system provides both daily and hourly predictions for multiple cryptocurrencies with a modern web interface.

## 🌟 Features

### 🔮 **Dual Prediction System**
- **Daily Predictions**: Long-term forecasting (1-30 days ahead) in INR
- **Hourly Predictions**: Short-term forecasting (1-23 hours ahead) in USDT
- **Multi-Currency Support**: Bitcoin, Ethereum, Cardano, Binance Coin, Dogecoin, Solana, Polygon

### 🤖 **Advanced ML Models**
- **LSTM Neural Networks**: Trained on historical OHLCV data
- **Separate Models**: Dedicated models for daily and hourly predictions
- **Real-time Data**: Fetches live data from Yahoo Finance and Binance APIs
- **Fallback Predictions**: Statistical models when ML models are unavailable

### 🌐 **Modern Web Interface**
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Charts**: Visual representation of price trends
- **Real-time Updates**: Live price feeds and predictions
- **User-friendly Controls**: Easy cryptocurrency selection and timeframe settings

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   ML Models     │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   (LSTM .h5)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Data Sources  │
                       │ Yahoo Finance   │
                       │ Binance API     │
                       │ CoinDesk API    │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd infosysspringboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp config.env.example config.env
   # Edit config.env with your API keys (optional)
   ```

4. **Start the server**
   ```bash
   PORT=5050 python3 app.py
   ```

5. **Open in browser**
   ```
   http://127.0.0.1:5050
   ```

## 📊 Available Models

| Cryptocurrency | Daily Model | Hourly Model | Status |
|----------------|-------------|--------------|---------|
| Bitcoin (BTC)  | ✅ lstm_btc_daily.h5 | ✅ lstm_btc_hourly.h5 | Active |
| Ethereum (ETH) | ✅ lstm_eth_daily.h5 | ✅ lstm_eth_hourly.h5 | Active |
| Cardano (ADA)  | ✅ lstm_ada_daily.h5 | ✅ lstm_ada_hourly.h5 | Active |
| Binance Coin (BNB) | ✅ lstm_bnb_daily.h5 | ✅ lstm_bnb_hourly.h5 | Active |
| Dogecoin (DOGE) | ✅ lstm_doge_daily.h5 | ✅ DOGE_hourly_inr.h5 | Active |

## 🔧 API Endpoints

### Prediction API
```http
POST /api/predict/{symbol}
Content-Type: application/json

{
  "symbol": "BTC",
  "days_ahead": 7,
  "hours_ahead": 12,
  "current_price": 45000.00
}
```

**Response:**
```json
{
  "symbol": "BTC",
  "current_price": 45000.00,
  "daily_prediction": {
    "predicted_price": 46500.00,
    "days_ahead": 7,
    "model_type": "LSTM",
    "currency": "INR"
  },
  "hourly_prediction": {
    "predicted_price": 45200.00,
    "hours_ahead": 12,
    "model_type": "LSTM",
    "currency": "USDT"
  },
  "timestamp": "2025-09-09T22:00:00Z"
}
```

### Health Check
```http
GET /api/health
```

### Model Details
```http
GET /api/models/details
```

## 🎯 Usage Examples

### 1. **Basic Prediction**
1. Open `http://127.0.0.1:5050/predictions.html`
2. Select a cryptocurrency (e.g., Bitcoin)
3. Set prediction timeframe:
   - Days ahead: 7
   - Hours ahead: 12
4. Click "Generate Prediction"
5. View results in prediction cards

### 2. **API Integration**
```python
import requests

response = requests.post('http://127.0.0.1:5050/api/predict/btc', json={
    'symbol': 'BTC',
    'days_ahead': 7,
    'hours_ahead': 12
})

data = response.json()
print(f"Daily prediction: ₹{data['daily_prediction']['predicted_price']}")
print(f"Hourly prediction: ${data['hourly_prediction']['predicted_price']}")
```

### 3. **Simple Test Page**
For debugging and testing, use the simplified interface:
```
http://127.0.0.1:5050/simple_test.html
```

## 📁 Project Structure

```
infosysspringboard/
├── app.py                          # Flask backend server
├── config.env                      # Environment configuration
├── requirements.txt                 # Python dependencies
├── models/                         # LSTM model files (.h5)
│   ├── lstm_btc_daily.h5
│   ├── lstm_btc_hourly.h5
│   └── ...
├── crypto-prediction-website-main/ # Frontend files
│   ├── index.html                  # Homepage
│   ├── predictions.html            # Main prediction interface
│   ├── script.js                   # Frontend JavaScript
│   ├── styles.css                  # Styling
│   ├── simple_test.html            # Debug interface
│   └── debug_prediction.html       # Advanced debugging
├── hourly data/                    # Historical data files
│   ├── BTCUSDT_hourly_INR.csv
│   ├── ETHUSDT_hourly_INR.csv
│   └── ...
└── milestone1/                     # Data collection scripts
    ├── fetch_bitcoin_data.py
    ├── fetch_crypto_hourly_data.py
    └── ...
```

## 🔧 Configuration

### Environment Variables (`config.env`)
```env
COINDESK_API_KEY=""                    # Optional: CoinDesk API key
COINDESK_API_URL="https://api.coindesk.com/v1/bpi/currentprice.json"
YAHOO_FINANCE_DAYS_LIMIT="60"          # Days of historical data to fetch
BINANCE_HOURS_LIMIT="60"               # Hours of historical data to fetch
DAYS_AHEAD_MAX="30"                    # Maximum days for prediction
HOURS_AHEAD_MAX="23"                   # Maximum hours for prediction
DAILY_MODEL_CURRENCY="INR"             # Currency for daily predictions
HOURLY_MODEL_CURRENCY="USDT"           # Currency for hourly predictions
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Use a different port
   PORT=5051 python3 app.py
   ```

2. **Model Loading Errors**
   - Ensure model files are in the `models/` directory
   - Check file permissions
   - Verify TensorFlow installation

3. **API Connection Issues**
   - Check internet connection
   - Verify API endpoints are accessible
   - Review error logs in terminal

4. **Frontend Not Loading**
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Use the debug pages for troubleshooting

### Debug Pages
- **Simple Test**: `http://127.0.0.1:5050/simple_test.html`
- **Debug Interface**: `http://127.0.0.1:5050/debug_prediction.html`

## 📈 Performance

- **Model Loading**: ~2-3 seconds on startup
- **Prediction Time**: ~1-2 seconds per prediction
- **Data Fetching**: ~3-5 seconds for 60 days of data
- **Memory Usage**: ~500MB with all models loaded

## 🔮 Future Enhancements

- [ ] **Additional Cryptocurrencies**: Add support for more coins
- [ ] **Advanced Models**: Implement Transformer and GRU models
- [ ] **Real-time Streaming**: WebSocket integration for live updates
- [ ] **Portfolio Management**: Multi-asset portfolio predictions
- [ ] **Mobile App**: React Native mobile application
- [ ] **Cloud Deployment**: Docker containerization and cloud hosting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Sources**: Yahoo Finance, Binance API, CoinDesk
- **ML Framework**: TensorFlow/Keras
- **Web Framework**: Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the debug pages for error details

---

**Built with ❤️ for the crypto community**
