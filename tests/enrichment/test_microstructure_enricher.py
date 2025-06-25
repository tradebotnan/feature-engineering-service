import pytest

pd = pytest.importorskip("pandas")
from app.enrichment.microstructure_enricher import enrich_with_microstructure


def test_enrich_with_microstructure():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=3, freq="s"),
            "price": [1.0, 1.1, 1.1],
            "size": [10, 20, 30],
        }
    )
    enriched = enrich_with_microstructure(df)
    assert {"tick_direction", "price_diff", "vwap_1s"}.issubset(enriched.columns)
