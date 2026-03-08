import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def fix_market_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    print(f"Fixing {filename}...")

    # Read with 2-row header (how yfinance saved it)
    df = pd.read_csv(path, header=[0, 1], index_col=0)

    # Flatten multi-level columns → keeps only first level (Close, High, etc.)
    df.columns = df.columns.get_level_values(0)

    # Reset index → Date becomes a normal column
    df = df.reset_index()
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)

    # Parse and reformat Date cleanly
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=False, errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Save back cleanly — single header row, no index
    df.to_csv(path, index=False)
    print(f"  ✅ Fixed — {len(df)} rows, first date: {df['Date'].iloc[0]}")

# Fix all 3 market CSVs
fix_market_csv("oil_prices.csv")
fix_market_csv("sp500_data.csv")
fix_market_csv("chip_data.csv")

# conflict_news.csv doesn't need this fix (not from yfinance)
print("\nAll CSVs fixed! Run: streamlit run dashboard/app.py")