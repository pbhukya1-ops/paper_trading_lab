# Paper Trading Lab

Read-only evaluation of completed paper trades. This documentation does not authorize live trading or order placement.

## Evaluation Report API

Module: `app.evaluation`

### Create a report

```python
from app.evaluation import evaluate_trades
report = evaluate_trades(completed_trades)
```

Pass an iterable of completed `Trade` instances. Invalid items raise `TypeError`.

### Report fields

| Field | Meaning |
|---|---|
| `completed_trade_count` | Number of completed trades |
| `winning_trade_count` | Trades with positive realized P&L |
| `losing_trade_count` | Trades with negative realized P&L |
| `breakeven_trade_count` | Trades with zero realized P&L |
| `realized_pnl` | Total realized P&L |
| `win_rate` | Winning trades as a percentage |
| `gross_profit` | Sum of positive realized P&L |
| `gross_loss` | Absolute sum of negative realized P&L |
| `profit_factor` | Gross profit divided by gross loss; `0.0` when gross loss is zero |
| `average_realized_pnl` | Average realized P&L per completed trade |

For empty input, all counts and numeric fields are zero.

### Dictionary export

```python
from app.evaluation import evaluation_report_to_dict
payload = evaluation_report_to_dict(report)
```

Returns a new dictionary. Invalid report types raise `TypeError`.

### Strict JSON export

```python
from app.evaluation import evaluation_report_to_json
json_text = evaluation_report_to_json(report)
```

Returns JSON text with sorted keys. `allow_nan=False` rejects NaN and positive or negative infinity with `ValueError`.

## Safety

These APIs evaluate completed trade records; they do not place orders or enable live trading. Keep paper-only and order-placement safety settings unchanged.
