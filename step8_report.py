import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from datetime import date

# ── Rebuild portfolio metrics for summary table ──────────────────────────────
returns      = pd.read_csv('returns.csv', index_col='Date', parse_dates=True)
n            = len(returns.columns)
mean_returns = returns.mean() * 252
cov_matrix   = returns.cov() * 252

def port_return(w): return np.dot(w, mean_returns)
def port_vol(w):    return np.sqrt(w @ cov_matrix @ w)
def port_sharpe(w): return -port_return(w) / port_vol(w)
def port_var(w):    return -np.percentile(returns @ w, 5)

constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
bounds = tuple((0, 1) for _ in range(n))
w0 = np.array([1/n] * n)
min_vol = minimize(port_vol,    w0, method='SLSQP', bounds=bounds, constraints=constraints)
max_sh  = minimize(port_sharpe, w0, method='SLSQP', bounds=bounds, constraints=constraints)
min_var = minimize(port_var,    w0, method='SLSQP', bounds=bounds, constraints=constraints)

portfolios = {
    'Equal Weight': np.array([1/n]*n),
    'Min Variance': min_vol.x,
    'Max Sharpe':   max_sh.x,
    'Min VaR':      min_var.x,
}

# ── Colour palette ────────────────────────────────────────────────────────────
BG    = '#0d1117'
PANEL = '#111827'
NAVY  = '#0D1B3E'
BLUE  = '#006AC1'
WHITE = '#FFFFFF'
LGRAY = '#cccccc'
MGRAY = '#888888'

plt.style.use('dark_background')

def fig_base(w=16, h=9):
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    return fig

def header_bar(fig, title, subtitle, step_label):
    ax = fig.add_axes([0, 0.91, 1, 0.09])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.03, 0.62, step_label, color=BLUE,   fontsize=9,  fontweight='bold', va='center')
    ax.text(0.03, 0.30, title,      color=WHITE,  fontsize=14, fontweight='bold', va='center')
    ax.text(0.97, 0.30, subtitle,   color=LGRAY,  fontsize=9,  va='center', ha='right', style='italic')

def footer(fig, page_num, total):
    ax = fig.add_axes([0, 0, 1, 0.035])
    ax.set_facecolor('#050a0f')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.03, 0.5, 'Simon De Bartolo  —  Quantitative Risk & Portfolio Management  |  Independent Research Project',
            color='#445566', fontsize=7.5, va='center')
    ax.text(0.97, 0.5, f'{page_num} / {total}', color='#445566', fontsize=7.5, va='center', ha='right')

def add_chart(fig, img_path, rect):
    ax = fig.add_axes(rect)
    img = mpimg.imread(img_path)
    ax.imshow(img, aspect='auto')
    ax.axis('off')
    return ax

def description_box(fig, rect, lines):
    ax = fig.add_axes(rect)
    ax.set_facecolor(PANEL)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    y = 0.88
    for kind, text in lines:
        if kind == 'label':
            ax.text(0.04, y, text, color=BLUE, fontsize=8.5, fontweight='bold', va='top')
            y -= 0.13
        elif kind == 'body':
            ax.text(0.04, y, text, color=LGRAY, fontsize=8, va='top', wrap=True,
                    multialignment='left')
            y -= 0.13
        elif kind == 'bullet':
            ax.text(0.04, y, u'\u2022  ' + text, color=MGRAY, fontsize=7.8, va='top')
            y -= 0.11
        elif kind == 'gap':
            y -= 0.07

TOTAL_PAGES = 9

with PdfPages('Portfolio_Risk_Report.pdf') as pdf:

    # ════════════════════════════════════════════════════════════════
    # PAGE 1 — TITLE
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG); ax.axis('off')

    # Accent strip
    strip = fig.add_axes([0, 0.46, 1, 0.005])
    strip.set_facecolor(BLUE); strip.axis('off')

    # Title block
    ax.text(0.5, 0.72, 'Quantitative Risk &\nPortfolio Management',
            color=WHITE, fontsize=34, fontweight='bold',
            ha='center', va='center', linespacing=1.4)
    ax.text(0.5, 0.56, 'Independent Research Project  —  MSc Finance Applications',
            color=LGRAY, fontsize=13, ha='center', va='center', style='italic')

    # Info grid
    info = [
        ('Author',   'Simon De Bartolo'),
        ('Universe', '10 EU Large-Cap Equities'),
        ('Period',   '2022 – 2025  (3 years daily data)'),
        ('Tools',    'Python  |  pandas  |  NumPy  |  SciPy  |  Matplotlib'),
        ('Modules',  'Data  |  Returns  |  VaR  |  CVaR  |  Backtest  |  Optimisation  |  Stress Test'),
        ('Date',     str(date.today().strftime('%B %Y'))),
    ]
    col_x = [0.18, 0.37]
    y0 = 0.40
    for i, (k, v) in enumerate(info):
        yi = y0 - i * 0.055
        ax.text(col_x[0], yi, k + ':', color=BLUE,  fontsize=10, fontweight='bold', ha='right')
        ax.text(col_x[0] + 0.015, yi, v, color=LGRAY, fontsize=10)

    footer(fig, 1, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 2 — RETURNS ANALYSIS
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Return Analysis', 'Log returns, annualised statistics, correlation matrix', 'STEP 2')
    add_chart(fig, 'cumulative_returns.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Methodology:'),
        ('body',  'Log returns r_t = ln(P_t / P_{t-1}). Annualised: mean x252, volatility x sqrt(252). Correlation matrix shows diversification structure.'),
    ])
    footer(fig, 2, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 3 — VaR
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Value at Risk (VaR)', 'Historical | Parametric | Monte Carlo  —  95% & 99% confidence', 'STEP 3')
    add_chart(fig, 'var_distribution.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Three methods:'),
        ('body',  'Historical (5th pct empirical) | Parametric (normal z-score) | Monte Carlo (10,000 simulations). VaR 95% ~ -0.9% daily.'),
    ])
    footer(fig, 3, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 4 — CVaR
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Conditional VaR — Expected Shortfall', 'Tail risk beyond VaR threshold  |  Basel III / FRTB standard metric', 'STEP 4')
    add_chart(fig, 'cvar_distribution.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Definition:'),
        ('body',  'CVaR = mean of returns below VaR threshold. CVaR 95% ~ -1.4% vs VaR 95% ~ -0.9%. Adopted by Basel III FRTB as primary capital metric since 2019.'),
    ])
    footer(fig, 4, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 5 — BACKTEST
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'VaR Model Backtesting', 'Kupiec POF Test  —  Likelihood-ratio validation of breach frequency', 'STEP 5')
    add_chart(fig, 'backtest.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Kupiec Test:'),
        ('body',  'H0: observed breach rate = expected 5%. p-value > 0.05 = well-calibrated model. Regulatory validation approach used by banks daily.'),
    ])
    footer(fig, 5, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 6 — EFFICIENT FRONTIER
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Portfolio Optimisation — Efficient Frontier', 'Markowitz Mean-Variance  |  4 optimal portfolios  |  Capital Market Line', 'STEP 6')
    add_chart(fig, 'efficient_frontier.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Optimisation:'),
        ('body',  'SLSQP solver minimises variance / maximises Sharpe subject to weights summing to 1. 5,000 Monte Carlo random portfolios show feasible set. CML tangent from rf=3.5%.'),
    ])
    footer(fig, 6, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 7 — STRESS TEST BARS
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Stress Testing — Scenario Analysis', '2022 Selloff  |  COVID-like -35%  |  GFC-like -50%', 'STEP 7')
    add_chart(fig, 'stress_test_bars.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Scenarios:'),
        ('body',  'Actual Jan-Oct 2022 data + hypothetical tail shocks. Min Variance consistently outperforms: -5.1% vs -9.5% EW in 2022; -17.4% vs -31.7% MaxSharpe in COVID scenario.'),
    ])
    footer(fig, 7, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 8 — 2022 CUMULATIVE
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Stress Testing — 2022 Cumulative Returns', 'Real portfolio performance during rate-hike selloff  Jan–Oct 2022', 'STEP 7b')
    add_chart(fig, 'stress_test_2022.png', [0.01, 0.10, 0.98, 0.78])
    description_box(fig, [0.01, 0.038, 0.98, 0.058], [
        ('label', 'Context:'),
        ('body',  'ECB + Fed aggressive rate hike cycle 2022. EU equities entered bear market. Min Variance recovered fastest; Max Sharpe showed deepest intra-period drawdown.'),
    ])
    footer(fig, 8, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    # PAGE 9 — SUMMARY TABLE
    # ════════════════════════════════════════════════════════════════
    fig = fig_base()
    header_bar(fig, 'Portfolio Summary — Key Metrics', 'Annualised figures  |  Equal-weight baseline vs optimised portfolios', 'SUMMARY')

    ax = fig.add_axes([0.04, 0.10, 0.92, 0.78])
    ax.set_facecolor(BG); ax.axis('off')

    rows_data = []
    port_colors = ['#8888aa', '#00e676', '#ffd600', '#ff4d6d']
    for name, w in portfolios.items():
        r    = port_return(w) * 100
        v    = port_vol(w)    * 100
        sh   = r / v
        var_ = np.percentile(returns @ w, 5) * 100
        cvar_= (returns @ w)[returns @ w <= np.percentile(returns @ w, 5)].mean() * 100
        rows_data.append([name, f'{r:.2f}%', f'{v:.2f}%', f'{sh:.3f}',
                          f'{var_:.2f}%', f'{cvar_:.2f}%'])

    col_labels = ['Portfolio', 'Ann. Return', 'Ann. Volatility', 'Sharpe Ratio', 'VaR 95%', 'CVaR 95%']
    col_w = [0.25, 0.13, 0.15, 0.14, 0.13, 0.13]
    y_hdr = 0.88
    x0 = 0.0

    # Header row
    xi = x0
    for ci, (lbl, cw) in enumerate(zip(col_labels, col_w)):
        rect = FancyBboxPatch((xi + 0.005, y_hdr - 0.04), cw - 0.012, 0.055,
                              boxstyle='round,pad=0.005',
                              facecolor=NAVY, edgecolor='none')
        ax.add_patch(rect)
        ax.text(xi + cw/2, y_hdr - 0.012, lbl,
                color=WHITE, fontsize=10, fontweight='bold',
                ha='center', va='center')
        xi += cw

    # Data rows
    for ri, (row, pcol) in enumerate(zip(rows_data, port_colors)):
        yi = y_hdr - 0.04 - (ri + 1) * 0.14
        xi = x0
        row_bg = '#111827' if ri % 2 == 0 else '#0d1a27'
        for ci, (val, cw) in enumerate(zip(row, col_w)):
            rect = FancyBboxPatch((xi + 0.005, yi), cw - 0.012, 0.115,
                                  boxstyle='round,pad=0.005',
                                  facecolor=row_bg, edgecolor='none')
            ax.add_patch(rect)
            col = pcol if ci == 0 else LGRAY
            fw  = 'bold' if ci == 0 else 'normal'
            ax.text(xi + cw/2, yi + 0.057, val,
                    color=col, fontsize=11, fontweight=fw,
                    ha='center', va='center')
            xi += cw

    # Column separator lines
    xi = x0 + col_w[0]
    for cw in col_w[1:]:
        ax.plot([xi, xi], [y_hdr - 0.04 - 4*0.14, y_hdr + 0.015],
                color='#1e2a3a', linewidth=0.8)
        xi += cw

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # Caption
    ax.text(0.5, 0.02,
            'VaR and CVaR are daily figures (not annualised).  '
            'Sharpe ratio computed using annualised return and volatility without risk-free adjustment.',
            color='#555577', fontsize=8, ha='center', va='bottom', style='italic')

    footer(fig, 9, TOTAL_PAGES)
    pdf.savefig(fig, facecolor=BG, bbox_inches='tight')
    plt.close(fig)

print('Portfolio_Risk_Report.pdf saved.')
