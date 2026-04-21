# Importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# ── Load data & rebuild optimised weights ────────────────────────────────────

returns = pd.read_csv('returns.csv', index_col='Date', parse_dates=True)
n       = len(returns.columns)

mean_returns = returns.mean() * 252
cov_matrix   = returns.cov() * 252

def port_return(w): return np.dot(w, mean_returns)
def port_vol(w):    return np.sqrt(w @ cov_matrix @ w)
def port_sharpe(w): return -port_return(w) / port_vol(w)
def port_var(w):    return -np.percentile(returns @ w, 5)

constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
bounds      = tuple((0, 1) for _ in range(n))
w0          = np.array([1/n] * n)

min_vol = minimize(port_vol,    w0, method='SLSQP', bounds=bounds, constraints=constraints)
max_sh  = minimize(port_sharpe, w0, method='SLSQP', bounds=bounds, constraints=constraints)
min_var = minimize(port_var,    w0, method='SLSQP', bounds=bounds, constraints=constraints)

portfolios = {
    'Equal Weight': np.array([1/n] * n),
    'Min Variance': min_vol.x,
    'Max Sharpe':   max_sh.x,
    'Min VaR':      min_var.x,
}

# ── Helper: max drawdown ─────────────────────────────────────────────────────

def max_drawdown(cum_ret_series):
    peak   = cum_ret_series.cummax()
    dd     = (cum_ret_series - peak) / peak
    return dd.min()

# ── SCENARIO 1: 2022 Rate-Hike Selloff (actual data) ────────────────────────

mask_2022 = (returns.index >= '2022-01-01') & (returns.index <= '2022-10-31')
ret_2022  = returns.loc[mask_2022]

print("=== STRESS TEST 1: 2022 Rate-Hike Selloff (Jan–Oct 2022) ===\n")
for name, w in portfolios.items():
    pr      = ret_2022 @ w
    cum     = (1 + pr).cumprod()
    total   = (cum.iloc[-1] - 1) * 100
    mdd     = max_drawdown(cum) * 100
    worst_d = pr.min() * 100
    print(f"{name}:")
    print(f"  Total return : {total:.2f}%")
    print(f"  Max drawdown : {mdd:.2f}%")
    print(f"  Worst day    : {worst_d:.2f}%\n")

# ── SCENARIO 2: COVID-like shock (−35% over 25 days) ────────────────────────
# Simulated as correlated draw from empirical distribution scaled to target loss

def simulate_shock(target_total_return, n_days=25, seed=42):
    """Draw n_days from empirical tail (worst 10%) scaled to target shock."""
    np.random.seed(seed)
    shock_rows = returns[returns.mean(axis=1) < returns.mean(axis=1).quantile(0.10)]
    idx        = np.random.choice(len(shock_rows), size=n_days, replace=True)
    raw        = shock_rows.iloc[idx].values
    # Scale rows so equal-weight portfolio hits target
    ew_daily   = raw @ np.array([1/n]*n)
    scale      = target_total_return / ew_daily.sum()
    return pd.DataFrame(raw * scale, columns=returns.columns)

shock_covid = simulate_shock(-0.35, n_days=25)
shock_gfc   = simulate_shock(-0.50, n_days=60)

print("=== STRESS TEST 2: COVID-like Shock (-35% EW reference, 25 days) ===\n")
for name, w in portfolios.items():
    pr    = shock_covid @ w
    total = (np.prod(1 + pr) - 1) * 100
    mdd   = max_drawdown((1 + pr).cumprod()) * 100
    print(f"{name}:  Total = {total:.2f}%  |  Max DD = {mdd:.2f}%")

print("\n=== STRESS TEST 3: GFC-like Shock (-50% EW reference, 60 days) ===\n")
for name, w in portfolios.items():
    pr    = shock_gfc @ w
    total = (np.prod(1 + pr) - 1) * 100
    mdd   = max_drawdown((1 + pr).cumprod()) * 100
    print(f"{name}:  Total = {total:.2f}%  |  Max DD = {mdd:.2f}%")

# ── Build summary table ──────────────────────────────────────────────────────

scenarios = {
    '2022 Selloff\n(actual)':      ret_2022,
    'COVID-like\n(-35% shock)':    shock_covid,
    'GFC-like\n(-50% shock)':      shock_gfc,
}

results = {}
for pname, w in portfolios.items():
    results[pname] = {}
    for sname, sdata in scenarios.items():
        pr    = sdata @ w
        total = (np.prod(1 + pr) - 1) * 100
        mdd   = max_drawdown((1 + pr).cumprod()) * 100
        results[pname][sname] = (total, mdd)

# ── PLOT 1: Total return + Max drawdown ─────────────────────────────────────

plt.style.use('dark_background')
BG      = '#0d1117'
PANEL   = '#111827'
GRID    = '#1e2a3a'
snames  = list(scenarios.keys())
snames_clean = ['2022 Selloff\n(actual data)', 'COVID-like\n(-35% shock)', 'GFC-like\n(-50% shock)']
pnames  = list(portfolios.keys())
colors_p = ['#8888aa', '#00e676', '#ffd600', '#ff4d6d']
width   = 0.19

def styled_bar_panel(ax, metric_idx, ylabel, title):
    x = np.arange(len(snames))
    # Shaded scenario bands
    for xi in x:
        ax.axvspan(xi - 0.45, xi + 0.45, color='#ffffff', alpha=0.02, zorder=0)
    for i, (pname, col) in enumerate(zip(pnames, colors_p)):
        vals = [results[pname][s][metric_idx] for s in snames]
        offsets = x + (i - 1.5) * width
        bars = ax.bar(offsets, vals, width * 0.92,
                      label=pname, color=col, alpha=0.88,
                      edgecolor=BG, linewidth=0.6, zorder=3)
        for bar, v in zip(bars, vals):
            bx = bar.get_x() + bar.get_width() / 2
            # Label outside bar tip
            pad   = -0.6 if v < 0 else 0.4
            va    = 'top' if v < 0 else 'bottom'
            ymin  = ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else -1
            # Only label if bar tall enough
            ax.text(bx, v + pad, f'{v:.1f}%',
                    ha='center', va=va, fontsize=7.5,
                    color=col, fontweight='bold', zorder=5)
    ax.axhline(0, color='#ffffff', linewidth=1.0, alpha=0.3, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(snames_clean, color='#cccccc', fontsize=10)
    ax.set_ylabel(ylabel, color='#aaaaaa', fontsize=10, labelpad=10)
    ax.tick_params(axis='y', colors='#777777', labelsize=9)
    ax.tick_params(axis='x', length=0)
    ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=14)
    ax.set_facecolor(PANEL)
    ax.grid(axis='y', color=GRID, linewidth=0.7, linestyle='--', zorder=1)
    ax.grid(axis='x', visible=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    # Extend y-axis 15% beyond data range for label headroom
    ylo, yhi = ax.get_ylim()
    margin = abs(ylo) * 0.15
    ax.set_ylim(ylo - margin, min(yhi + 2, 2))
    legend = ax.legend(fontsize=8.5, facecolor='#1a1a2e', edgecolor='#333355',
                       labelcolor='white', framealpha=0.9,
                       loc='lower left', ncol=2, columnspacing=0.8,
                       handlelength=1.2)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor(BG)
fig.subplots_adjust(top=0.88, hspace=0.35, wspace=0.28,
                    left=0.06, right=0.97, bottom=0.12)

styled_bar_panel(axes[0], 0, 'Total Return (%)',   'Total Return Under Stress')
styled_bar_panel(axes[1], 1, 'Max Drawdown (%)', 'Max Drawdown Under Stress')

fig.suptitle('Portfolio Stress Testing  —  Scenario Analysis',
             color='white', fontsize=15, fontweight='bold', y=0.97)
fig.text(0.5, 0.01,
         'Actual: Jan-Oct 2022 data  |  Hypothetical: correlated tail shocks scaled to EW reference loss',
         ha='center', color='#666688', fontsize=8)

plt.savefig('stress_test_bars.png', dpi=180, facecolor=BG, bbox_inches='tight')
plt.show()

# ── PLOT 2: Cumulative returns during 2022 selloff ───────────────────────────

fig2, ax2 = plt.subplots(figsize=(13, 6))
fig2.patch.set_facecolor('#0d1117')
ax2.set_facecolor('#0d1117')
ax2.grid(color='#2a2a3e', linewidth=0.6, linestyle='--', alpha=0.7)
for spine in ax2.spines.values():
    spine.set_edgecolor('#2a2a3e')

for (pname, w), col in zip(portfolios.items(), colors_p):
    pr  = ret_2022 @ w
    cum = (1 + pr).cumprod() - 1
    ax2.plot(cum.index, cum * 100, color=col, linewidth=2.0, label=pname)

ax2.axhline(0, color='white', linewidth=0.8, alpha=0.4, linestyle='--')
ax2.set_title('Cumulative Returns — 2022 Rate-Hike Selloff (Jan–Oct 2022)',
              color='white', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Date', color='#cccccc', fontsize=10, labelpad=8)
ax2.set_ylabel('Cumulative Return (%)', color='#cccccc', fontsize=10, labelpad=8)
ax2.tick_params(colors='#aaaaaa', labelsize=9)
ax2.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444466',
           labelcolor='white', framealpha=0.85)

plt.tight_layout()
plt.savefig('stress_test_2022.png', dpi=180, facecolor=fig2.get_facecolor(),
            bbox_inches='tight')
plt.show()

print("\nstress_test_bars.png  saved.")
print("stress_test_2022.png  saved.")
