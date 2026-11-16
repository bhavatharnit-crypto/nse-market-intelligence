
# NSE Market Intelligence

An AI-powered stock analysis and strategy backtesting platform built for the Arthaton 2026 AI for Finance challenge.

## Features
- Stock price and historical market data analysis
- Annualised return and volatility estimates
- Maximum drawdown and risk metrics
- Moving average crossover strategy backtesting
- Interactive charts and CSV downloads
- AI-generated market commentary when an API key is configured

## Technology
- Python
- Streamlit
- Pandas and NumPy
- Plotly
- yfinance
- Google Gemini API (optional)

## Run locally
1. Install Python.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Start the application:

   `streamlit run app.py`

## AI configuration
Set the `GEMINI_API_KEY` environment variable to enable Gemini-powered commentary. The app also includes a rule-based fallback.

## Data and disclaimer
The bundled dataset is synthetic sample data, not actual NSE data. Live historical data can be requested through yfinance. This application is for educational and analytical purposes only. It does not provide investment advice or execute real trades.
