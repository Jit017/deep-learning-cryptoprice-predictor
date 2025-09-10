import sys
from pathlib import Path

import pandas as pd
import yfinance as yf


def fetch_and_save_crypto_hourly_data():
    # Define the cryptocurrencies and their symbols
    crypto_pairs = {
        "ETH-USD": "ETH",
        "LTC-USD": "LTC", 
        "XRP-USD": "XRP",
        "ADA-USD": "ADA",
        "BNB-USD": "BNB",
        "SOL-USD": "SOL"
    }
    
    # Create an empty list to store individual dataframes
    dataframes = []
    
    for yf_symbol, symbol in crypto_pairs.items():
        print(f"Fetching {symbol} hourly data...")
        
        try:
            # Download hourly data (max period for hourly data is usually ~2 years)
            df = yf.download(
                tickers=yf_symbol,
                period="2y",  # 2 years of hourly data
                interval="1h",
                auto_adjust=False,
                threads=True,
                progress=False,
            )
            
            if df is None or df.empty:
                print(f"Warning: No data returned for {symbol}")
                continue
                
            # Reset index and handle multi-level columns
            df = df.reset_index()
            
            # If columns are multi-level, flatten them properly
            if isinstance(df.columns, pd.MultiIndex):
                # Get the first level (column names) and ignore the second level (ticker)
                df.columns = df.columns.get_level_values(0)
            
            # Keep only required columns
            df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]].copy()
            
            # Add Symbol column
            df["Symbol"] = symbol
            
            # Reorder columns
            df = df[["Datetime", "Open", "High", "Low", "Close", "Volume", "Symbol"]]
            
            dataframes.append(df)
            print(f"  ✓ {symbol}: {len(df)} rows")
            
        except Exception as e:
            print(f"  ✗ Error fetching {symbol}: {e}")
            continue
    
    if not dataframes:
        raise RuntimeError("No data was fetched for any cryptocurrency")
    
    # Merge all datasets using pandas concat
    print("\nMerging all datasets...")
    
    # Use concat with ignore_index=True to properly merge
    merged_df = pd.concat(dataframes, ignore_index=True, axis=0)
    
    # Sort by Datetime and Symbol for better organization
    merged_df = merged_df.sort_values(["Datetime", "Symbol"]).reset_index(drop=True)
    
    # Save merged dataset
    output_path = Path(__file__).resolve().parent / "crypto_hourly_data.csv"
    merged_df.to_csv(output_path, index=False)
    
    print(f"\nSaved merged CSV to: {output_path}")
    print(f"Total rows: {len(merged_df)}")
    print(f"Date range: {merged_df['Datetime'].min()} to {merged_df['Datetime'].max()}")
    
    # Print first 5 rows for verification
    print("\nFirst 5 rows of merged data:")
    print(merged_df.head().to_string(index=False))
    
    # Print summary by symbol
    print("\nSummary by cryptocurrency:")
    for symbol in crypto_pairs.values():
        symbol_data = merged_df[merged_df['Symbol'] == symbol]
        if not symbol_data.empty:
            print(f"  {symbol}: {len(symbol_data)} rows ({symbol_data['Datetime'].min()} to {symbol_data['Datetime'].max()})")
    
    return output_path


if __name__ == "__main__":
    try:
        csv_path = fetch_and_save_crypto_hourly_data()
        print(f"\n✓ Successfully created: {csv_path}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
