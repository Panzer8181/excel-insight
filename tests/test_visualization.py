import pandas as pd

from visualization import build_sales_visualizations


def test_build_sales_visualizations_aggregates_uploaded_rows():
    sales = pd.DataFrame({
        "order_date": ["2026-10-02", "2026-10-01", "2026-10-01", "2026-10-03"],
        "product": ["手机", "耳机", "手机", "键盘"],
        "quantity": [1, 3, 1, 1],
        "unit_price": [3000, 200, 1000, 500],
        "sales_amount": [3000, 600, 1000, 500],
    })

    charts = build_sales_visualizations(sales)

    trend = charts["sales_trend"]["data"][0]
    assert trend["x"] == ["2026-10-01", "2026-10-02", "2026-10-03"]
    assert trend["y"] == [1600, 3000, 500]

    top10 = charts["product_top10"]["data"][0]
    assert top10["x"] == ["手机", "耳机", "键盘"]
    assert top10["y"] == [4000, 600, 500]

    share = charts["product_share"]["data"][0]
    assert share["labels"] == ["手机", "耳机", "键盘"]
    assert share["values"] == [4000, 600, 500]


def test_product_top10_chart_limits_to_ten_products():
    sales = pd.DataFrame({
        "order_date": ["2026-10-01"] * 12,
        "product": [f"商品{number}" for number in range(12)],
        "sales_amount": list(range(12, 0, -1)),
    })

    charts = build_sales_visualizations(sales)
    top10 = charts["product_top10"]["data"][0]

    assert len(top10["x"]) == 10
    assert top10["x"][0] == "商品0"
    assert top10["x"][-1] == "商品9"
