# Quantitative Risk & Portfolio Management

End-to-end quantitative risk and portfolio management system built in Python, using 10 large-cap European equities (2022–2025).

## Project Structure

| File | Description |
|------|-------------|
| `step1_data.py` | Download daily adjusted prices via yfinance |
| `step2_returns.py` | Log returns, annualised statistics, correlation matrix |
| `step3_VaR.py` | Historical, Parametric and Monte Carlo VaR (95%/99%) |
| `step4_cvar.py` | Conditional VaR / Expected Shortfall |
| `step5_backtest.py` | VaR model backtesting — Kupiec POF test |
| `step6_optimization.py` | Markowitz efficient frontier, 4 optimal portfolios, Capital Market Line |
| `step7_stress.py` | Stress testing: 2022 selloff, COVID-like, GFC-like scenarios |
| `step8_report.py` | Automated PDF report generation (9 pages) |

## Methodology

- **Returns**: Log returns `r_t = ln(P_t / P_{t-1})`, annualised ×252 / ×√252
- **VaR**: Three methods — Historical (empirical percentile), Parametric (normal), Monte Carlo
- **CVaR**: Mean of tail beyond VaR — Basel III / FRTB standard metric
- **Backtesting**: Kupiec likelihood-ratio test for breach frequency validation
- **Optimisation**: Markowitz Mean-Variance via SLSQP solver (scipy.optimize)
- **Stress Testing**: Actual 2022 data + hypothetical tail-shock scenarios

## Requirements

```
pip install pandas numpy matplotlib scipy yfinance
```

## Usage

Run steps in order:

```bash
python step1_data.py        # downloads prices.csv
python step2_returns.py     # generates returns.csv + chart
python step3_VaR.py
python step4_cvar.py
python step5_backtest.py
python step6_optimization.py
python step7_stress.py
python step8_report.py      # generates Portfolio_Risk_Report.pdf
```

## Results Summary

| Portfolio | Ann. Return | Ann. Volatility | Sharpe |
|-----------|-------------|-----------------|--------|
| Equal Weight | ~8% | ~18% | ~0.45 |
| Min Variance | ~3% | ~13% | ~0.25 |
| Max Sharpe | ~21% | ~20% | ~1.05 |
| Min VaR | ~8% | ~18% | ~0.44 |

Min Variance portfolio outperforms in all stress scenarios.
