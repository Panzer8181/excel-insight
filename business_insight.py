"""Generate concise business insights from normalized sales data."""

import pandas as pd


def _format_amount(value):
    """Format a sales amount without unnecessary trailing decimal zeros."""
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


def generate_business_insights(df):
    """Build sales, product, and data-quality observations for a DataFrame.

    The input is expected to contain a precomputed ``sales_amount`` column.
    It is never modified by this function.
    """
    sales_insights = []
    product_insights = []
    data_warnings = []

    if "order_date" in df.columns and "sales_amount" in df.columns:
        sales = df[["order_date", "sales_amount"]].copy()
        sales["_sales_amount"] = pd.to_numeric(
            sales["sales_amount"], errors="coerce"
        )
        sales["_date"] = pd.to_datetime(
            sales["order_date"], errors="coerce", utc=True
        ).dt.strftime("%Y-%m-%d")

        daily_sales = (
            sales.dropna(subset=["_date"])
            .groupby("_date")["_sales_amount"]
            .sum(min_count=1)
            .dropna()
        )
        if not daily_sales.empty:
            highest_date = daily_sales.idxmax()
            highest_amount = _format_amount(daily_sales.loc[highest_date])
            sales_insights.append(
                f"{highest_date}销售额最高，达到{highest_amount}元"
            )

    if "product" in df.columns and "sales_amount" in df.columns:
        products = pd.DataFrame({
            "_product": df["product"].fillna("（空白）").astype(str),
            "_sales_amount": pd.to_numeric(
                df["sales_amount"], errors="coerce"
            ),
        })
        product_sales = (
            products.groupby("_product")["_sales_amount"]
            .sum(min_count=1)
            .dropna()
            .sort_values(ascending=False, kind="stable")
        )
        total_sales = product_sales.sum()
        if not product_sales.empty and total_sales > 0:
            leading_product = product_sales.index[0]
            leading_share = product_sales.iloc[0] / total_sales * 100
            if leading_share > 50:
                product_insights.append(
                    f"{leading_product}贡献{leading_share:.1f}%的销售额，是主要收入来源"
                )

    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    if missing_values > 0:
        data_warnings.append(
            f"发现{missing_values}个缺失值，需要进一步检查"
        )
    if duplicate_rows > 0:
        data_warnings.append(f"发现{duplicate_rows}条重复数据")

    return {
        "sales_insights": sales_insights,
        "product_insights": product_insights,
        "data_warnings": data_warnings,
    }
