import pandas as pd

from business_insight import generate_business_insights


def test_generate_business_insights_for_regular_sales_data():
    df = pd.DataFrame({
        "order_date": ["2026-10-01", "2026-10-01", "2026-10-02"],
        "product": ["手机", "耳机", "键盘"],
        "sales_amount": [7000, 5000, 4000],
    })

    result = generate_business_insights(df)

    assert result == {
        "sales_insights": ["2026-10-01销售额最高，达到12000元"],
        "product_insights": [],
        "data_warnings": [],
    }


def test_generate_business_insights_identifies_high_share_product():
    df = pd.DataFrame({
        "order_date": ["2026-10-01", "2026-10-02", "2026-10-02"],
        "product": ["手机", "耳机", "键盘"],
        "sales_amount": [12000, 2000, 1240],
    })

    result = generate_business_insights(df)

    assert result["product_insights"] == [
        "手机贡献78.7%的销售额，是主要收入来源"
    ]


def test_generate_business_insights_warns_about_missing_and_duplicate_rows():
    df = pd.DataFrame({
        "order_date": ["2026-10-01", "2026-10-01", "2026-10-02"],
        "product": ["手机", "手机", None],
        "sales_amount": [100, 100, 50],
    })

    result = generate_business_insights(df)

    assert result["data_warnings"] == [
        "发现1个缺失值，需要进一步检查",
        "发现1条重复数据",
    ]
