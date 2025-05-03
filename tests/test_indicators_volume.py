import pytest
import pandas as pd
from app.indicators.volume import add_vwap, add_price_vwap_ratio, add_volume_ema, add_volume_roc, detect_volume_anomalies


@pytest.fixture
def sample_volume_data():
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=10, freq="D"),
        "close": [100 + i for i in range(10)],
        "volume": [1000 + 100 * i for i in range(10)]
    })


def test_add_vwap(sample_volume_data):
    df = sample_volume_data.copy()
    df["high"] = df["close"] + 2
    df["low"] = df["close"] - 2
    df["open"] = df["close"] - 1
    df = add_vwap(df)
    assert "vwap" in df.columns
    assert not df["vwap"].isna().all()


def test_add_price_vwap_ratio(sample_volume_data):
    df = sample_volume_data.copy()
    df["vwap"] = df["close"] * 0.98
    df = add_price_vwap_ratio(df)
    assert "price_vwap_ratio" in df.columns
    assert all(df["price_vwap_ratio"].notna())


def test_add_volume_ema(sample_volume_data):
    df = sample_volume_data.copy()
    df = add_volume_ema(df, 3)
    assert "volume_ema_3" in df.columns
    assert df["volume_ema_3"].isna().sum() < len(df)


def test_add_volume_roc(sample_volume_data):
    df = sample_volume_data.copy()
    df = add_volume_roc(df, 3)
    assert "volume_roc_3" in df.columns
    assert df["volume_roc_3"].isna().sum() < len(df)

def test_detect_volume_anomalies(sample_volume_data):
    sample_volume_data["volume_anomaly"] = detect_volume_anomalies(sample_volume_data.copy(), threshold=1.0)
    assert "volume_anomaly" in sample_volume_data.columns
    assert set(sample_volume_data["volume_anomaly"].unique()).issubset({0, 1})
