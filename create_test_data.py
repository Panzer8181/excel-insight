"""Create deterministic synthetic XLSX workbooks for demos and testing."""

from pathlib import Path

import pandas as pd


def build_demo_datasets():
    """Return five synthetic workbooks covering supported and rejected input."""
    return {
        "standard_sales.xlsx": pd.DataFrame({
            "order_id": ["ORD001", "ORD002", "ORD003"],
            "order_date": ["2026-10-01", "2026-10-02", "2026-10-03"],
            "product": ["手机", "耳机", "键盘"],
            "quantity": [2, 3, 1],
            "unit_price": [3000, 200, 500],
        }),
        "mapped_fields_sales.xlsx": pd.DataFrame({
            "订单编号": ["ORD101", "ORD102"],
            "order_date": ["2026-10-04", "2026-10-05"],
            "product": ["显示器", "鼠标"],
            "购买数量": [2, 1],
            "成交价": [150, 40],
        }),
        "low_quality_sales.xlsx": pd.DataFrame({
            "order_id": ["ORD201", "ORD201", "ORD203"],
            "order_date": ["2026-10-06", "2026-10-06", "2026-10-07"],
            "product": ["手机", "手机", None],
            "quantity": [2, 2, 1],
            "unit_price": [100, 100, 50],
        }),
        "invalid_type_sales.xlsx": pd.DataFrame({
            "order_id": ["ORD301", "ORD302"],
            "order_date": ["2026-10-08", "2026-10-09"],
            "product": ["键盘", "鼠标"],
            "quantity": [1, "三"],
            "unit_price": [500, 40],
        }),
        "invalid_fields_sales.xlsx": pd.DataFrame({
            "客户": ["示例客户甲", "示例客户乙"],
            "交易金额": [120, 240],
        }),
    }


def create_demo_workbooks(output_dir="data/demo"):
    """Write all synthetic examples and return a mapping of names to paths."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {}
    for filename, dataframe in build_demo_datasets().items():
        output_path = output_dir / filename
        dataframe.to_excel(output_path, index=False)
        paths[filename] = output_path

    return paths


def create_test_workbook(output_path="data/sales_test.xlsx"):
    """Keep the earlier helper API for creating an invalid quantity workbook."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    build_demo_datasets()["invalid_type_sales.xlsx"].to_excel(
        output_path,
        index=False,
    )
    return output_path


if __name__ == "__main__":
    for workbook_path in create_demo_workbooks().values():
        print(f"已创建模拟演示数据：{workbook_path}")
