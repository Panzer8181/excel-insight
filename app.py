"""Flask web workflow for uploading and analyzing sales workbooks."""

from collections import OrderedDict
from io import BytesIO
import secrets
import threading
import zipfile

from flask import Flask, abort, render_template, request, send_file

from business_insight import generate_business_insights
from data_processor import DataValidationError, load_sales_data
from data_quality import analyze_data_quality
from order_metrics import count_unique_order_ids
from report_export import build_analysis_report
from visualization import build_sales_visualizations

app = Flask(__name__)

# 限制上传请求最大为5MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
MAX_XLSX_ARCHIVE_ENTRIES = 10_000
MAX_XLSX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_CACHED_REPORTS = 8
_REPORT_CACHE = OrderedDict()
_REPORT_CACHE_LOCK = threading.Lock()


def _cache_report(report_content):
    """Keep a bounded set of in-memory reports for the download links."""
    report_id = secrets.token_urlsafe(24)
    with _REPORT_CACHE_LOCK:
        _REPORT_CACHE[report_id] = report_content
        while len(_REPORT_CACHE) > MAX_CACHED_REPORTS:
            _REPORT_CACHE.popitem(last=False)
    return report_id


def is_valid_xlsx_structure(file_stream):
    """Check that an uploaded stream is a ZIP-based XLSX workbook."""
    try:
        file_stream.seek(0)

        # 第一层：是不是ZIP文件
        if not zipfile.is_zipfile(file_stream):
            return False

        file_stream.seek(0)

        # 第二层：检查Excel必需的内部结构
        with zipfile.ZipFile(file_stream) as z:
            entries = z.infolist()
            if len(entries) > MAX_XLSX_ARCHIVE_ENTRIES:
                return False
            if sum(entry.file_size for entry in entries) > MAX_XLSX_UNCOMPRESSED_BYTES:
                return False

            file_names = {entry.filename for entry in entries}

            required_files = {
                "[Content_Types].xml",
                "xl/workbook.xml"
            }

            return required_files.issubset(file_names)

    except (OSError, zipfile.BadZipFile):
        return False

    finally:
        file_stream.seek(0)


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
                if not is_valid_xlsx_structure(file.stream):
                    error = "文件内容不是有效的Excel"
                else:
                    file.stream.seek(0)

                    df = load_sales_data(file)
                    data_quality = analyze_data_quality(df)

                    # 基于标准化字段计算销售额，供指标和图表复用。
                    df["sales_amount"] = (
                        df["quantity"] * df["unit_price"]
                    )
                    insights = generate_business_insights(df)

                    orders, empty_order_ids = count_unique_order_ids(df["order_id"])
                    total_sales = float(df["sales_amount"].sum())

                    analysis_result = {
                        "orders": orders,
                        "row_count": len(df),
                        "empty_order_ids": empty_order_ids,
                        "total_sales": total_sales,
                        "average_order_sales": (
                            round(total_sales / orders, 2)
                            if orders
                            else 0.0
                        ),
                        "data_quality": data_quality,
                        "insights": insights,
                        "charts": build_sales_visualizations(df),
                        "table_rows": df.to_dict(orient="records")
                    }
                    report_content = build_analysis_report(analysis_result)
                    analysis_result["report_id"] = _cache_report(report_content)
                    result = analysis_result

            except DataValidationError as e:
                detail = e.args[0]

                # 兼容结构化校验错误和普通校验提示
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


@app.route("/download-report/<report_id>", methods=["GET"])
def download_report(report_id):
    with _REPORT_CACHE_LOCK:
        report_content = _REPORT_CACHE.get(report_id)
    if report_content is None:
        abort(404)

    return send_file(
        BytesIO(report_content),
        as_attachment=True,
        download_name="excel_insight_analysis_report.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.errorhandler(413)
def handle_large_file(error):
    return render_template(
        "index.html",
        result=None,
        error="文件大小不能超过5MB"
    ), 413


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
