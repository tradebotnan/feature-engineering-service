import pandas as pd
from app.enrichment.trade_side_inference import infer_trade_side


def test_infer_trade_side():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=3, freq="s"),
            "price": [1.0, 1.1, 1.0],
        }
    )
    enriched = infer_trade_side(df)
    assert "trade_side" in enriched.columns
