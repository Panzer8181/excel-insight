import io

import pandas as pd

from app import app


def test_success_page_displays_data_quality_metrics():
    data = pd.DataFrame({
        "order_id": ["ORD001", "ORD001", "ORD003"],
        "order_date": ["2026-10-01", "2026-10-01", "2026-10-03"],
        "product": ["手机", "手机", None],
        "quantity": [2, 2, 1],
        "unit_price": [3000, 3000, 500],
    })
    excel_file = io.BytesIO()
    data.to_excel(excel_file, index=False)
    excel_file.seek(0)

    with app.test_client() as client:
        response = client.post(
            "/",
            data={"file": (excel_file, "quality-check.xlsx")},
            content_type="multipart/form-data",
        )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "数据质量分析" in html
    assert "数据行数" in html
    assert "字段数量" in html
    assert "缺失值" in html
    assert "重复行" in html
    assert "数据完整率" in html
    assert "质量评分" in html
    assert "93.33%" in html
    assert "60.00 / 100" in html
