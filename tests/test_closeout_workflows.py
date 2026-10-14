import io
import zipfile

import pandas as pd
import pytest

from app import (
    MAX_XLSX_UNCOMPRESSED_BYTES,
    app as flask_app,
    is_valid_xlsx_structure,
)
from create_test_data import create_demo_workbooks
from visualization import build_sales_visualizations


def _upload(client, workbook_path):
    workbook = io.BytesIO(workbook_path.read_bytes())
    return client.post(
        "/",
        data={"file": (workbook, workbook_path.name)},
        content_type="multipart/form-data",
    )


def test_demo_generator_creates_all_five_excel_scenarios(tmp_path):
    workbooks = create_demo_workbooks(tmp_path)

    assert set(workbooks) == {
        "standard_sales.xlsx",
        "mapped_fields_sales.xlsx",
        "low_quality_sales.xlsx",
        "invalid_type_sales.xlsx",
        "invalid_fields_sales.xlsx",
    }
    assert all(path.is_file() for path in workbooks.values())
    assert pd.read_excel(workbooks["standard_sales.xlsx"]).shape == (3, 5)
    assert "购买数量" in pd.read_excel(
        workbooks["mapped_fields_sales.xlsx"]
    ).columns
    assert pd.read_excel(workbooks["low_quality_sales.xlsx"]).isna().sum().sum() == 1
    assert pd.read_excel(workbooks["invalid_type_sales.xlsx"])[
        "quantity"
    ].dtype == object
    assert set(pd.read_excel(workbooks["invalid_fields_sales.xlsx"]).columns) == {
        "客户",
        "交易金额",
    }


@pytest.mark.parametrize(
    ("filename", "orders", "total", "average", "preview_id"),
    [
        ("standard_sales.xlsx", 3, "7100.00", "2366.67", "ORD001"),
        ("mapped_fields_sales.xlsx", 2, "340.00", "170.00", "ORD101"),
    ],
)
def test_standard_and_mapped_workbooks_show_consistent_results(
    tmp_path, filename, orders, total, average, preview_id
):
    workbooks = create_demo_workbooks(tmp_path)

    with flask_app.test_client() as client:
        response = _upload(client, workbooks[filename])

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "分析成功" in html
    assert f"订单数量：{orders}" in html
    assert total in html
    assert average in html
    assert preview_id in html
    assert "sales-trend-chart" in html
    assert "product-top10-chart" in html
    assert "product-share-chart" in html
    assert "销售数据预览（前5行）" in html


def test_low_quality_workbook_reports_quality_and_business_warnings(tmp_path):
    workbooks = create_demo_workbooks(tmp_path)

    with flask_app.test_client() as client:
        response = _upload(client, workbooks["low_quality_sales.xlsx"])

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "93.33%" in html
    assert "60.00 / 100" in html
    assert "发现1个缺失值，需要进一步检查" in html
    assert "发现1条重复数据" in html


@pytest.mark.parametrize(
    ("filename", "expected_message"),
    [
        ("invalid_type_sales.xlsx", "quantity字段必须是数字"),
        ("invalid_fields_sales.xlsx", "缺少必要字段"),
    ],
)
def test_invalid_workbooks_show_safe_validation_feedback(
    tmp_path, filename, expected_message
):
    workbooks = create_demo_workbooks(tmp_path)

    with flask_app.test_client() as client:
        response = _upload(client, workbooks[filename])

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "上传失败" in html
    assert expected_message in html
    assert "分析成功" not in html


def test_unknown_runtime_error_is_not_exposed(tmp_path, monkeypatch):
    workbook_path = create_demo_workbooks(tmp_path)["standard_sales.xlsx"]

    def fail_loader(_file):
        raise RuntimeError("internal detail: C:/private/runtime.xlsx")

    monkeypatch.setattr("app.load_sales_data", fail_loader)
    with flask_app.test_client() as client:
        response = _upload(client, workbook_path)

    html = response.get_data(as_text=True)
    assert "文件无法处理，请确认Excel格式正确" in html
    assert "C:/private/runtime.xlsx" not in html
    assert "RuntimeError" not in html


def test_product_chart_keeps_integer_quantity_annotations():
    sales = pd.DataFrame({
        "order_date": ["2026-10-01", "2026-10-01"],
        "product": ["手机", "手机"],
        "quantity": [2, 3],
        "sales_amount": [100, 150],
    })

    chart = build_sales_visualizations(sales)["product_share"]["data"][0]

    assert chart["labels"] == ["手机"]
    assert chart["customdata"] == [5]
    assert "销量：%{customdata:,.0f} 件" in chart["texttemplate"]
    assert "商品数量：%{customdata:,.0f} 件" in chart["hovertemplate"]


def test_xlsx_structure_check_rejects_large_expanded_archive():
    workbook = io.BytesIO()
    with zipfile.ZipFile(workbook, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("xl/workbook.xml", "<workbook/>")
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            b"A" * (MAX_XLSX_UNCOMPRESSED_BYTES + 1),
        )

    assert workbook.getbuffer().nbytes < flask_app.config["MAX_CONTENT_LENGTH"]
    workbook.seek(0)
    assert not is_valid_xlsx_structure(workbook)
