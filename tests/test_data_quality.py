import pandas as pd
import pytest

from data_quality import analyze_data_quality


def test_analyze_data_quality_for_complete_unique_data():
    df = pd.DataFrame({"product": ["手机", "耳机"], "quantity": [2, 1]})

    result = analyze_data_quality(df)

    assert result == {
        "rows": 2,
        "columns": 2,
        "missing_values": 0,
        "duplicate_rows": 0,
        "completeness": 1.0,
        "quality_score": 100.0,
    }


def test_analyze_data_quality_penalizes_missing_values():
    df = pd.DataFrame({"product": ["手机", None], "quantity": [2, 1]})

    result = analyze_data_quality(df)

    assert result["missing_values"] == 1
    assert result["completeness"] == 0.75
    assert result["quality_score"] == 75.0


def test_analyze_data_quality_penalizes_duplicate_rows():
    df = pd.DataFrame({
        "product": ["手机", "手机", "耳机"],
        "quantity": [2, 2, 1],
    })

    result = analyze_data_quality(df)

    assert result["duplicate_rows"] == 1
    assert result["completeness"] == 1.0
    assert result["quality_score"] == pytest.approx(100 - 100 / 3)


def test_analyze_data_quality_for_empty_dataframe():
    result = analyze_data_quality(pd.DataFrame())

    assert result == {
        "rows": 0,
        "columns": 0,
        "missing_values": 0,
        "duplicate_rows": 0,
        "completeness": 1.0,
        "quality_score": 100.0,
    }
