
from flask import Flask, render_template, request
from data_processor import load_sales_data

app = Flask(__name__)

# 限制上传请求最大为5MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        file = request.files.get("file")

        if file is None or file.filename == "":
            error = "请先选择Excel文件"

        elif not file.filename.lower().endswith(".xlsx"):
            error = "目前只支持.xlsx格式"

        else:
            try:
                # 复用之前写好的数据读取与校验函数
                df = load_sales_data(file)

                # 计算销售额
                df["sales_amount"] = (
                    df["quantity"] * df["unit_price"]
                )

                result = {
                    "orders": len(df),
                    "total_sales": float(df["sales_amount"].sum()),
                    "preview": df.head(5).to_dict(orient="records")
                }

            except ValueError as e:
                detail = e.args[0]

                # 兼容之前的结构化错误和普通错误
                if isinstance(detail, dict):
                    error = detail.get("message", "数据校验失败")
                else:
                    error = str(detail)

            except Exception:
                app.logger.exception("Excel处理发生意外错误")
                error = "文件无法处理，请确认Excel格式正确"

    return render_template(
        "index.html",
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
