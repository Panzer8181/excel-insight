
import io
import pandas as pd

from app import app


def test_upload_valid_excel():
    # 1. 准备模拟销售数据
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

    # 2. 在内存中生成Excel文件
    excel_file = io.BytesIO()
    pd.DataFrame(data).to_excel(
        excel_file,
        index=False
    )
    excel_file.seek(0)

    # 3. 模拟浏览器上传Excel
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (excel_file, "sales.xlsx")
            },
            content_type="multipart/form-data"
        )

    # 4. 检查服务器响应
    assert response.status_code == 200

    # 5. 检查网页内容
    html = response.get_data(as_text=True)

    assert "分析成功" in html
    assert "7100.00" in html
    assert "ORD001" in html

def test_upload_missing_column():
    # 1. 故意创建缺少 unit_price 的数据
    data = {
        "order_id": ["ORD001"],
        "order_date": ["2026-10-01"],
        "product": ["手机"],
        "quantity": [2]
    }

    # 2. 在内存中生成Excel
    excel_file = io.BytesIO()

    pd.DataFrame(data).to_excel(
        excel_file,
        index=False
    )

    excel_file.seek(0)

    # 3. 模拟用户上传错误Excel
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (excel_file, "wrong.xlsx")
            },
            content_type="multipart/form-data"
        )

    # 4. 检查网页是否正确处理错误
    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "上传失败" in html
    assert "缺少必要字段" in html
    assert "unit_price" in html