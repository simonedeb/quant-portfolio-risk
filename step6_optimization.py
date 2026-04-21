#Importing libraries 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


#Loading returns data

returns = pd.read_csv('returns.csv', index_col='Date', parse_dates=True)
n = len(returns.columns)
tickers = returns.columns.tolist()

mean_returns = returns.mean() * 252
cov_matrix   = returns.cov() * 252


#Defining the objective function for optimization (minimize portfolio variance)

def port_return(w): return np.dot(w, mean_returns)
def port_vol(w):    return np.sqrt(w @ cov_matrix @ w)
def port_sharpe(w): return -port_return(w) / port_vol(w)
def port_var(w):
    pr = returns @ w
    return np.percentile(pr, 5)
def port_min_var(w): return -port_var(w)

constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
bounds = tuple((0, 1) for _ in range(n))
w0 = np.array([1/n] * n)


#Optimizing for volatility , sharpe ratio and VaR

min_vol = minimize(port_vol,    w0, method='SLSQP',
                   bounds=bounds, constraints=constraints)
max_sh  = minimize(port_sharpe, w0, method='SLSQP',
                   bounds=bounds, constraints=constraints)
min_var = minimize(port_min_var,w0, method='SLSQP',
                   bounds=bounds, constraints=constraints)

portfolios = {
    'Equal Weight' : np.array([1/n]*n),
    'Min Variance' : min_vol.x,
    'Max Sharpe'   : max_sh.x,
    'Min VaR'      : min_var.x,
}

print("=== PORTFOLIO OPTIMISATION RESULTS ===\n")
for name, w in portfolios.items():
    r   = port_return(w) * 100
    v   = port_vol(w)    * 100
    sh  = r / v
    var = port_var(w)    * 100
    print(f"{name}:")
    print(f"  Return    : {r:.2f}%")
    print(f"  Volatility: {v:.2f}%")
    print(f"  Sharpe    : {sh:.3f}")
    print(f"  VaR 95%   : {var:.2f}%\n")


#Plotting the efficient frontier

frontier_vols, frontier_rets = [], []
target_returns = np.linspace(mean_returns.min(), mean_returns.max(), 100)

for target in target_returns:
    cons = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'eq', 'fun': lambda w, t=target: port_return(w) - t}
    ]
    res = minimize(port_vol, w0, method='SLSQP',
                   bounds=bounds, constraints=cons)
    if res.success:
        frontier_vols.append(port_vol(res.x) * 100)
        frontier_rets.append(port_return(res.x) * 100)

mc_vols, mc_rets, mc_sharpes = [], [], []
for _ in range(5000):
    w = np.random.dirichlet(np.ones(n))
    mc_rets.append(port_return(w) * 100)
    mc_vols.append(port_vol(w) * 100)
    mc_sharpes.append(port_return(w) / port_vol(w))

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

# Monte Carlo scatter
sc = ax.scatter(mc_vols, mc_rets, c=mc_sharpes, cmap='plasma',
                alpha=0.35, s=6, zorder=2, label='Random Portfolios')
cbar = plt.colorbar(sc, ax=ax, pad=0.02)
cbar.set_label('Sharpe Ratio', color='#cccccc', fontsize=10)
cbar.ax.yaxis.set_tick_params(color='#cccccc')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#cccccc')

# Efficient frontier
ax.plot(frontier_vols, frontier_rets,
        color='#00d4ff', linewidth=2.8, zorder=4,
        label='Efficient Frontier', solid_capstyle='round')

# Capital Market Line (risk-free rate ~3.5% annualised)
rf = 0.035
ms_w   = portfolios['Max Sharpe']
ms_vol = port_vol(ms_w) * 100
ms_ret = port_return(ms_w) * 100
cml_x  = np.linspace(0, ms_vol * 1.25, 200)
slope  = (ms_ret - rf * 100) / ms_vol
cml_y  = rf * 100 + slope * cml_x
ax.plot(cml_x, cml_y,
        color='#ffffff', linewidth=1.2, linestyle='--',
        alpha=0.5, zorder=3, label='Capital Market Line')

# Optimal portfolio markers
styles = {
    'Equal Weight': {'color': '#aaaaaa', 'marker': 'o', 'size': 160},
    'Min Variance': {'color': '#00ff88', 'marker': 's', 'size': 160},
    'Max Sharpe':   {'color': '#ffd700', 'marker': '*', 'size': 320},
    'Min VaR':      {'color': '#ff4d6d', 'marker': '^', 'size': 180},
}
for name, w in portfolios.items():
    v = port_vol(w) * 100
    r = port_return(w) * 100
    s = styles[name]
    ax.scatter(v, r, color=s['color'], marker=s['marker'],
               s=s['size'], zorder=6, edgecolors='white',
               linewidths=0.8, label=name)
    ax.annotate(name,
                xy=(v, r), xytext=(6, 6), textcoords='offset points',
                color=s['color'], fontsize=8.5, fontweight='bold',
                zorder=7)

# Grid and spines
ax.grid(color='#2a2a3e', linewidth=0.6, linestyle='--', alpha=0.7)
for spine in ax.spines.values():
    spine.set_edgecolor('#2a2a3e')

ax.set_title('Efficient Frontier & Optimal Portfolios',
             fontsize=14, color='white', fontweight='bold', pad=14)
ax.set_xlabel('Annualised Volatility (%)', fontsize=11, color='#cccccc', labelpad=8)
ax.set_ylabel('Annualised Return (%)',     fontsize=11, color='#cccccc', labelpad=8)
ax.tick_params(colors='#aaaaaa', labelsize=9)

legend = ax.legend(fontsize=8.5, facecolor='#1a1a2e',
                   edgecolor='#444466', labelcolor='white',
                   framealpha=0.85, loc='upper left')

plt.tight_layout()
plt.savefig('efficient_frontier.png', dpi=180, facecolor=fig.get_facecolor())
plt.show()
print("efficient_frontier.png saved.")
