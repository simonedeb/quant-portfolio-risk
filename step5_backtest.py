#Importing libraries + data about weighted returns 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

returns = pd.read_csv('returns.csv', index_col='Date', parse_dates=True)

n = len(returns.columns)
weights = np.array([1/n] * n)
portfolio_returns = returns @ weights


#Importing Kupiec Test Function

def kupiec_test(returns, confidence_level):
    var = np.percentile(returns, (1 - confidence_level) * 100)
    
    violations = (returns < var).sum()
    T = len(returns)
    expected = (1 - confidence_level)
    actual   = violations / T
    
    # Likelihood ratio statistic
    if violations == 0 or violations == T:
        lr_stat = np.nan
        p_value = np.nan
    else:
        lr_stat = -2 * (
            np.log((1 - expected)**(T - violations) * expected**violations) -
            np.log((1 - actual)**(T - violations)   * actual**violations)
        )
        p_value = 1 - stats.chi2.cdf(lr_stat, df=1)
    
    return var, violations, T, expected * T, actual * 100, lr_stat, p_value


#Backtesting  the portfolio returns with the Kupiec Test and plotting the results

confidence_levels = [0.95, 0.99]

print("=== KUPIEC BACKTESTING ===\n")
for cl in confidence_levels:
    var, viol, T, exp_viol, act_pct, lr, pval = kupiec_test(portfolio_returns, cl)
    
    result = "✅ PASS" if pval is not np.nan and pval > 0.05 else "❌ FAIL"
    
    print(f"Confidence Level : {int(cl*100)}%")
    print(f"VaR              : {var*100:.2f}%")
    print(f"Total days       : {T}")
    print(f"Expected breaches: {exp_viol:.1f}")
    print(f"Actual breaches  : {viol}  ({act_pct:.2f}%)")
    print(f"LR statistic     : {lr:.4f}")
    print(f"p-value          : {pval:.4f}")
    print(f"Model verdict    : {result}\n")


#Plotting violations over time

var_95 = np.percentile(portfolio_returns, 5)

fig, ax = plt.subplots(figsize=(13, 5))

ax.plot(portfolio_returns.index, portfolio_returns,
        color='steelblue', linewidth=0.8, label='Portfolio Daily Return')

ax.axhline(var_95, color='orange', linewidth=1.5,
           linestyle='--', label=f'VaR 95%: {var_95*100:.2f}%')

breaches = portfolio_returns[portfolio_returns < var_95]
ax.scatter(breaches.index, breaches, color='red', s=20, zorder=5,
           label=f'Breaches: {len(breaches)}')

ax.set_title('VaR Backtesting — Daily Returns & Breaches', fontsize=13)
ax.set_xlabel('Date')
ax.set_ylabel('Daily Return')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('backtest.png', dpi=150)
plt.show()
print("backtest.png saved.")
