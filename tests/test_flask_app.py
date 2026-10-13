
import io
import pandas as pd
import zipfile
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


def test_average_order_sales_is_displayed():
    data = {
        "order_id": ["ORD001", "ORD002", "ORD003"],
        "order_date": ["2026-10-01", "2026-10-02", "2026-10-03"],
        "product": ["手机", "耳机", "键盘"],
        "quantity": [2, 3, 1],
        "unit_price": [3000, 200, 500]
    }

    excel_file = io.BytesIO()
    pd.DataFrame(data).to_excel(excel_file, index=False)
    excel_file.seek(0)

    with app.test_client() as client:
        response = client.post(
            "/",
            data={"file": (excel_file, "sales.xlsx")},
            content_type="multipart/form-data"
        )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "平均每单销售额：2366.67 元" in html



def test_average_order_sales_is_zero_when_there_are_no_orders(monkeypatch):
    # 1. 准备一个空DataFrame，模拟0条订单
    empty_data = pd.DataFrame(
        columns=[
            "order_id",
            "order_date",
            "product",
            "quantity",
            "unit_price"
        ]
    )

    # 2. 创建一个真正的XLSX文件
    excel_file = io.BytesIO()
    empty_data.to_excel(excel_file, index=False)
    excel_file.seek(0)

    # 3. 模拟数据处理函数返回0条订单
    monkeypatch.setattr(
        "app.load_sales_data",
        lambda _file: empty_data
    )

    # 4. 模拟浏览器上传
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (excel_file, "sales.xlsx")
            },
            content_type="multipart/form-data"
        )

    # 5. 检查零订单情况下的计算结果
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "订单数量：0" in html
    assert "平均每单销售额：0.00 元" in html


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

def test_upload_empty_excel():
    # 创建有表头、但没有数据行的Excel
    columns = [
        "order_id",
        "order_date",
        "product",
        "quantity",
        "unit_price"
    ]

    excel_file = io.BytesIO()

    pd.DataFrame(columns=columns).to_excel(
        excel_file,
        index=False
    )

    excel_file.seek(0)

    # 模拟用户真实上传空Excel
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (excel_file, "empty.xlsx")
            },
            content_type="multipart/form-data"
        )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "上传失败" in html
    assert "Excel文件没有数据" in html

def test_upload_large_file():
    # 模拟一个6MB的文件
    large_file = io.BytesIO(
        b"x" * (6 * 1024 * 1024)
    )

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (large_file, "large.xlsx")
            },
            content_type="multipart/form-data"
        )

    assert response.status_code == 413

    html = response.get_data(as_text=True)

    assert "文件大小不能超过5MB" in html


def test_fake_excel_file():
    # 1. 创建一个假的Excel文件
    fake_file = io.BytesIO(
        b"This is not a real Excel file"
    )

    # 2. 假装用户上传了一个.xlsx文件
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (fake_file, "fake.xlsx")
            },
            content_type="multipart/form-data"
        )

    # 3. 获取网页返回内容
    html = response.get_data(as_text=True)

    # 4. 验证错误处理
    assert response.status_code == 200
    assert "上传失败" in html
    assert "文件内容不是有效的Excel" in html
    assert "分析成功" not in html


def test_fake_zip_as_excel():
    # 1. 创建一个真实的ZIP文件
    fake_excel = io.BytesIO()

    with zipfile.ZipFile(fake_excel, "w") as z:
        z.writestr("hello.txt", "This is not Excel")

    fake_excel.seek(0)

    # 2. 验证它确实是ZIP
    assert zipfile.is_zipfile(fake_excel)

    fake_excel.seek(0)

    # 3. 把ZIP伪装成XLSX上传
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (fake_excel, "fake.xlsx")
            },
            content_type="multipart/form-data"
        )

    # 4. 检查网站返回结果
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "上传失败" in html
    assert "文件内容不是有效的Excel" in html
    assert "分析成功" not in html


def test_internal_error_not_exposed(monkeypatch):
    # 1. 模拟数据处理函数出现内部异常
    def fake_loader(file):
        raise ValueError("内部路径: C:/private/data.xlsx")

    monkeypatch.setattr(
        "app.load_sales_data",
        fake_loader
    )

    # 2. 创建真正的XLSX文件，让它通过文件结构检查
    excel_file = io.BytesIO()

    pd.DataFrame({"test": [1]}).to_excel(
        excel_file,
        index=False
    )

    excel_file.seek(0)

    # 3. 模拟用户上传
    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "file": (excel_file, "test.xlsx")
            },
            content_type="multipart/form-data"
        )

    html = response.get_data(as_text=True)

    # 4. 不应该把内部路径展示给用户
    assert "C:/private/data.xlsx" not in html

    # 5. 应该返回通用错误提示
    assert "文件无法处理，请确认Excel格式正确" in html
