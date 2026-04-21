# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

#Loading returns data + defining portfolio weights
returns = pd.read_csv('returns.csv', index_col='Date', parse_dates=True)

n = len(returns.columns)
weights = np.array([1/n] * n)

portfolio_returns = returns @ weights

# Calculating VaR using the Historical Simulation method + setting confidence levels
confidence_levels= [ 0.95, 0.99]

print('=== HISTORICAL VaR ===')

for cl in confidence_levels:
    var = np.percentile(portfolio_returns, (1 - cl) * 100)
    print(f'VaR {int(cl*100)}%: {var:.4f}  ({var*100:.2f}%)')

# Calculating VaR using the Parametric method (assuming normal distribution)
print('\n=== PARAMETRIC VaR ===')
mean = np.mean(portfolio_returns)
std  = np.std(portfolio_returns)
for cl in confidence_levels:
    var = stats.norm.ppf(1 - cl, loc=mean, scale=std)
    print(f'VaR {int(cl*100)}%: {var:.4f}  ({var*100:.2f}%)')


# Monte Carlo Simulation for VaR estimation
np.random.seed(42)
n_simulations = 10000

sim_returns = np.random.normal(mean, std, n_simulations)

print("\n=== MONTE CARLO SIMULATION VaR ===")
for cl in confidence_levels:
    var = np.percentile(sim_returns, (1-cl) * 100)
    print(f"VaR {int(cl*100)}%: {var:.4f}  ({var*100:.2f}%)")

# Plotting the distribution of portfolio returns + VaR lines
fig, ax = plt.subplots(figsize=(12, 5))
ax.hist(portfolio_returns, bins=60, color='steelblue',
        edgecolor='white', alpha=0.7, density=True, label='Historical Returns')

colors = ['orange', 'red']
for i, cl in enumerate(confidence_levels):
    var_h = np.percentile(portfolio_returns, (1 - cl) * 100)
    ax.axvline(var_h, color=colors[i], linewidth=2,
               linestyle='--', label=f'Historical VaR {int(cl*100)}%: {var_h*100:.2f}%')

ax.set_title('Portfolio Return Distribution & VaR', fontsize=13)
ax.set_xlabel('Daily Return')
ax.set_ylabel('Density')
ax.legend()
plt.tight_layout()
plt.savefig('var_distribution.png', dpi=150)
plt.show()
print("\nvar_distribution.png saved.")