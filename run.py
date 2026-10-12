from data_processor import load_sales_data

print("程序开始运行")

try:
    df = load_sales_data("data/sales_test.xlsx")

    print("Excel读取成功！")
    print(df)

    df["sales_amount"] = df["quantity"] * df["unit_price"]

    print("总销售额：", df["sales_amount"].sum())


except ValueError as e:
    error_info = e.args[0]
    print("上传失败！")
    print("错误代码：", error_info["error_code"])
    print("提示：", error_info["message"])
    print("错误行：", error_info["rows"])




