import pandas as pd
import logging

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


class DataValidationError(ValueError):
    """Raised when uploaded sales data fails a business validation check."""


REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "product",
    "quantity",
    "unit_price"
]

def load_sales_data(file_path):
    df = pd.read_excel(file_path)

    if df.empty:
        raise DataValidationError("Excel文件没有数据")

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        logger.error(
            f"缺少必要字段: {missing_columns}"
        )
        raise DataValidationError(
            f"缺少必要字段: {missing_columns}"
        )

    # 检查数量是否为空
    if df["quantity"].isnull().any():
       error_rows = df[df["quantity"].isnull()]
       logger.error("quantity字段存在空值")
       raise DataValidationError({
       "status": "failed",
       "error_code": "EMPTY_QUANTITY",
       "message": "quantity字段存在空值",
       "rows": error_rows.index.tolist()
       })


    # 检查数量是否为数字
    if not pd.api.types.is_numeric_dtype(df["quantity"]):
        logger.error("quantity字段不是数字")
        raise DataValidationError("quantity字段必须是数字")

    # 检查价格是否为空
    if df["unit_price"].isnull().any():
        logger.error("unit_price字段存在空值")
        raise DataValidationError("unit_price字段存在空值")

    # 检查价格是否数字
    if not pd.api.types.is_numeric_dtype(df["unit_price"]):
        logger.error("unit_price字段不是数字")
        raise DataValidationError("unit_price字段必须是数字")

    return df
