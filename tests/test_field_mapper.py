import pandas as pd
import pytest

from data_processor import load_sales_data
from field_mapper import map_fields


@pytest.mark.parametrize(
    ("source_columns", "expected_mapping"),
    [
        (["订单编号", "数量", "价格"], {
            "order_id": "订单编号",
            "quantity": "数量",
            "unit_price": "价格"
        }),
        (["订单号", "销售数量", "单价"], {
            "order_id": "订单号",
            "quantity": "销售数量",
            "unit_price": "单价"
        }),
        (["order", "购买数量", "售价"], {
            "order_id": "order",
            "quantity": "购买数量",
            "unit_price": "售价"
        }),
        (["id", "qty", "price"], {
            "order_id": "id",
            "quantity": "qty",
            "unit_price": "price"
        })
    ]
)
def test_map_supported_aliases(source_columns, expected_mapping):
    columns = pd.DataFrame(columns=source_columns).columns

    assert map_fields(columns) == expected_mapping


def test_map_canonical_column_names():
    columns = pd.DataFrame(
        columns=["order_id", "quantity", "unit_price"]
    ).columns

    assert map_fields(columns) == {
        "order_id": "order_id",
        "quantity": "quantity",
        "unit_price": "unit_price"
    }


def test_map_fields_returns_missing_standard_field_names():
    assert map_fields(["订单编号", "商品名称"]) == [
        "quantity",
        "unit_price"
    ]


def test_load_sales_data_renames_alias_columns(tmp_path):
    data = pd.DataFrame({
        "订单编号": ["ORD001"],
        "order_date": ["2026-10-13"],
        "product": ["键盘"],
        "购买数量": [2],
        "成交价": [300]
    })
    file_path = tmp_path / "aliased_sales.xlsx"
    data.to_excel(file_path, index=False)

    loaded = load_sales_data(file_path)

    assert loaded.loc[0, "order_id"] == "ORD001"
    assert loaded.loc[0, "quantity"] == 2
    assert loaded.loc[0, "unit_price"] == 300
