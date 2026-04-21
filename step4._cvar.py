#Importing necessary libraries + loading return data and  defining portfolio returns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

returns = pd.read_csv('returns.csv', index_col='Date', parse_dates=True)

n = len(returns.columns)
weights = np.array([1/n] * n)
portfolio_returns = returns @ weights


#Calculating VaR + CVaR 

confidence_levels = [0.95, 0.99]

print("=== VaR & CVaR (Expected Shortfall) ===\n")
for cl in confidence_levels:
    var  = np.percentile(portfolio_returns, (1 - cl) * 100)
    cvar = portfolio_returns[portfolio_returns <= var].mean()
    print(f"Confidence {int(cl*100)}%:")
    print(f"  VaR  : {var:.4f}  ({var*100:.2f}%)")
    print(f"  CVaR : {cvar:.4f}  ({cvar*100:.2f}%)")
    print(f"  Tail excess: {(cvar - var)*100:.2f}%\n")


#Plotting VaR vs CVaR

fig, ax = plt.subplots(figsize=(12, 5))

ax.hist(portfolio_returns, bins=60, color='steelblue',
        edgecolor='white', alpha=0.7, density=True, label='Returns')

colors_var  = ['orange', 'red']
colors_cvar = ['darkorange', 'darkred']

for i, cl in enumerate(confidence_levels):
    var  = np.percentile(portfolio_returns, (1 - cl) * 100)
    cvar = portfolio_returns[portfolio_returns <= var].mean()

    ax.axvline(var,  color=colors_var[i],  linewidth=2,
               linestyle='--', label=f'VaR  {int(cl*100)}%: {var*100:.2f}%')
    ax.axvline(cvar, color=colors_cvar[i], linewidth=2,
               linestyle=':',  label=f'CVaR {int(cl*100)}%: {cvar*100:.2f}%')

ax.set_title('VaR vs CVaR (Expected Shortfall)', fontsize=13)
ax.set_xlabel('Daily Return')
ax.set_ylabel('Density')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('cvar_distribution.png', dpi=150)
plt.show()
print("cvar_distribution.png saved.")


