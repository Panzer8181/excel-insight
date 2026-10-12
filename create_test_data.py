import pandas as pd
from pathlib import Path

data = {
    "order_id": ["ORD001", "ORD002", "ORD003"],
    "order_date": ["2026-10-01", "2026-10-02", "2026-10-03"],
    "product": ["手机", "耳机", "键盘"],
    "quantity": [2, ' ', 1],
    "unit_price": [3000, 200, 500]
}

df = pd.DataFrame(data)

folder = Path("data")
folder.mkdir(exist_ok=True)

df.to_excel("data/sales_test.xlsx", index=False)

print("Excel测试文件创建成功！")