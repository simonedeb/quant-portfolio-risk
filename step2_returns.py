# Importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Loading the dataset
prices = pd.read_csv('prices.csv', index_col='Date', parse_dates=True)


# Calculating daily returns
returns = prices.pct_change().dropna()

# Annualizing statistics
ann_return = returns.mean() * 252
ann_vol    = returns.std() * np.sqrt(252)


print("=== RENDIMENTO MEDIO ANNUALIZZATO ===")
print(ann_return.round(4))
print("\n=== VOLATILITÀ ANNUALIZZATA ===")
print(ann_vol.round(4))


# Correlation matrix
print("\n=== CORRELAZIONE ===")
print(returns.corr().round(2))


# Plotting cumulative returns
cumulative = (1 + returns).cumprod()
cumulative.plot(figsize=(12,6), title='Cumulative Returns 2022–2025')
plt.ylabel('Value (base 1.0)')
plt.tight_layout()
plt.savefig('cumulative_returns.png', dpi=150)
plt.show()


# Saving returns
returns.to_csv('returns.csv')
print("\nreturns.csv saved.")


