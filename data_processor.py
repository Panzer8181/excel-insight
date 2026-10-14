"""Read, normalize, and validate uploaded sales workbooks."""

import logging
from pathlib import Path

import pandas as pd

from field_mapper import map_fields

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_DIR / "app.log"),
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
    """Read an Excel workbook, map supported aliases, and validate sales data."""
    df = pd.read_excel(file_path)

    if df.empty:
        raise DataValidationError("Excel文件没有数据")

    field_mapping = map_fields(df.columns)
    if isinstance(field_mapping, list):
        missing_columns = list(field_mapping)
        missing_columns.extend(
            col for col in ("order_date", "product")
            if col not in df.columns
        )
    else:
        df = df.rename(
            columns={source: standard for standard, source in field_mapping.items()}
        )
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

    # Keep row indexes in the structured error so callers can identify bad rows.
    if df["quantity"].isnull().any():
        error_rows = df[df["quantity"].isnull()]
        logger.error("quantity字段存在空值")
        raise DataValidationError({
            "status": "failed",
            "error_code": "EMPTY_QUANTITY",
            "message": "quantity字段存在空值",
            "rows": error_rows.index.tolist()
        })

    # Validate numeric types before the web layer calculates sales_amount.
    if not pd.api.types.is_numeric_dtype(df["quantity"]):
        logger.error("quantity字段不是数字")
        raise DataValidationError("quantity字段必须是数字")

    if df["unit_price"].isnull().any():
        logger.error("unit_price字段存在空值")
        raise DataValidationError("unit_price字段存在空值")

    if not pd.api.types.is_numeric_dtype(df["unit_price"]):
        logger.error("unit_price字段不是数字")
        raise DataValidationError("unit_price字段必须是数字")

    return df
