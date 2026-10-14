"""Calculate basic completeness and duplication metrics for a DataFrame."""


def analyze_data_quality(df):
    """Return row, column, missing, duplicate, and quality score metrics.

    Completeness is a fraction between 0 and 1. The quality score starts at
    100 and subtracts missing-cell and duplicate-row rates in percentage
    points. An empty table has no missing data and receives a full score.
    """
    rows, columns = df.shape
    rows = int(rows)
    columns = int(columns)
    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    total_cells = rows * columns
    missing_rate = missing_values / total_cells if total_cells else 0.0
    duplicate_rate = duplicate_rows / rows if rows else 0.0

    completeness = 1.0 - missing_rate
    quality_score = max(
        0.0,
        100.0 - missing_rate * 100.0 - duplicate_rate * 100.0,
    )

    return {
        "rows": rows,
        "columns": columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "completeness": completeness,
        "quality_score": quality_score,
    }
