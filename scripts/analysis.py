import pandas as pd
import os

# -------- Project Paths --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# -------- Load Data --------
oil = pd.read_csv(os.path.join(DATA_DIR, "oil_prices.csv"))
sp500 = pd.read_csv(os.path.join(DATA_DIR, "sp500_data.csv"))
chips = pd.read_csv(os.path.join(DATA_DIR, "chip_data.csv"))
news = pd.read_csv(os.path.join(DATA_DIR, "conflict_news.csv"))

# -------- Clean Data --------
def clean_market_data(df):
    df = df.reset_index()
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna()
    return df

oil = clean_market_data(oil)
sp500 = clean_market_data(sp500)
chips = clean_market_data(chips)

# -------- Market Changes --------
oil_change = ((oil["Close"].iloc[-1] - oil["Close"].iloc[0]) / oil["Close"].iloc[0]) * 100
sp_change = ((sp500["Close"].iloc[-1] - sp500["Close"].iloc[0]) / sp500["Close"].iloc[0]) * 100
chip_change = ((chips["Close"].iloc[-1] - chips["Close"].iloc[0]) / chips["Close"].iloc[0]) * 100

# -------- Risk Scoring System --------
risk_score = 0

# Oil impact
if oil_change > 5:
    risk_score += 3
elif oil_change > 2:
    risk_score += 2
elif oil_change > 1:
    risk_score += 1

# Stock market reaction
if sp_change < -2:
    risk_score += 3
elif sp_change < -1:
    risk_score += 2
elif sp_change < 0:
    risk_score += 1

# Semiconductor impact
if chip_change < -3:
    risk_score += 3
elif chip_change < -1:
    risk_score += 2
elif chip_change < 0:
    risk_score += 1

# -------- Risk Level --------
if risk_score >= 6:
    risk_level = "High Geopolitical Risk"
elif risk_score >= 3:
    risk_level = "Moderate Risk"
else:
    risk_level = "Low Risk"

# -------- News --------
latest_news = news.iloc[0]["title"]

# -------- Output --------
print("\n----- Global Conflict Impact Analysis -----\n")

print("Oil Change %:", round(oil_change,2))
print("S&P500 Change %:", round(sp_change,2))
print("Chip Industry Change %:", round(chip_change,2))

print("\nLatest Conflict News:")
print(latest_news)

print("\nRisk Score:", risk_score)
print("Risk Level:", risk_level)