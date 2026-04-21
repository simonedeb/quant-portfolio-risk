
import yfinance as yf 
import pandas as pd

# Defining tickers symbols and periods of interest for the historical data we want to analyze
tickers = ['ASML.AS', 'MC.PA', 'RACE.MI', 'SAN.MC', 'AIR.PA',
           'SIE.DE', 'NESN.SW', 'ROG.SW', 'TTE.PA', 'BNP.PA']

start_date = '2022-01-01'
end_date   = '2025-01-01'

# Downloading historical data and prices for the defined tickers and periods
prices = yf.download(tickers, start=start_date, end=end_date)['Close']

#Removing rows with missing values
prices = prices.dropna()

#Saving the firrst rows to verify the data
print(prices.head())
print(f"\nRighe totali: {len(prices)}")
print(f"Colonne: {list(prices.columns)}")

# Saving the data to a CSV file 
prices.to_csv('prices.csv')
print("\nFile prices.csv salvato.")
