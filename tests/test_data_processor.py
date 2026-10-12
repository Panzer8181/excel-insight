import pandas as pd
import pytest

from data_processor import load_sales_data


def test_valid_excel(tmp_path):
    # 第一步：准备模拟销售数据
    data = {
        "order_id": ["ORD001", "ORD002", "ORD003"],
        "order_date": [
            "2026-10-01",
            "2026-10-02",
            "2026-10-03"
        ],
        "product": ["手机", "耳机", "键盘"],
        "quantity": [2, 3, 1],
        "unit_price": [3000, 200, 500]
    }

    # 第二步：创建测试Excel
    file_path = tmp_path / "test_sales.xlsx"
    pd.DataFrame(data).to_excel(file_path, index=False)

    # 第三步：调用我们之前写的函数
    df = load_sales_data(file_path)

    # 第四步：检查结果
    assert len(df) == 3

    total_sales = (
        df["quantity"] * df["unit_price"]
    ).sum()

    assert total_sales == 7100

def test_missing_column(tmp_path):
    # 1. 准备缺少 unit_price 的数据
    data = {
        "order_id": ["ORD001"],
        "order_date": ["2026-10-01"],
        "product": ["手机"],
        "quantity": [2]
    }

    # 2. 生成测试 Excel
    file_path = tmp_path / "missing_column.xlsx"
    pd.DataFrame(data).to_excel(file_path, index=False)

    # 3. 检查程序是否按预期抛出异常
    with pytest.raises(ValueError, match="缺少必要字段"):
        load_sales_data(file_path)

def test_empty_quantity(tmp_path):
    data = {
        "order_id": ["ORD001", "ORD002"],
        "order_date": ["2026-10-01", "2026-10-02"],
        "product": ["手机", "耳机"],
        "quantity": [2, None],
        "unit_price": [3000, 200]
    }

    file_path = tmp_path / "empty_quantity.xlsx"
    pd.DataFrame(data).to_excel(file_path, index=False)

    with pytest.raises(ValueError) as exc_info:
        load_sales_data(file_path)

    error_info = exc_info.value.args[0]

    assert error_info["error_code"] == "EMPTY_QUANTITY"
    assert error_info["rows"] == [1]

def test_invalid_quantity(tmp_path):
    data = {
        "order_id": ["ORD001", "ORD002", "ORD003"],
        "order_date": [
            "2026-10-01",
            "2026-10-02",
            "2026-10-03"
        ],
        "product": ["手机", "耳机", "键盘"],
        "quantity": [2, "三", 1],
        "unit_price": [3000, 200, 500]
    }

    file_path = tmp_path / "invalid_quantity.xlsx"
    pd.DataFrame(data).to_excel(file_path, index=False)

    with pytest.raises(
        ValueError,
        match="quantity字段必须是数字"
    ):
        load_sales_data(file_path)