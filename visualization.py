"""Build Plotly figures for uploaded sales data."""

import json

import pandas as pd
import plotly.graph_objects as go

from order_metrics import daily_unique_order_counts


def _figure_to_dict(figure):
    """Return a JSON-serializable Plotly figure for use in a template."""
    return json.loads(figure.to_json())


def build_sales_visualizations(df):
    """Build JSON-ready Plotly figures from normalized sales rows.

    The input DataFrame is copied so chart aggregation cannot mutate the data
    used for KPI calculations or the preview table.
    """
    sales = df[["order_date", "product", "sales_amount"]].copy()
    if "quantity" in df.columns:
        sales["quantity"] = df["quantity"]
    else:
        # Older chart callers may provide sales totals without quantity data.
        sales["quantity"] = 0
    sales["_sales_amount"] = pd.to_numeric(
        sales["sales_amount"], errors="coerce"
    )
    sales["_quantity"] = pd.to_numeric(
        sales["quantity"], errors="coerce"
    ).fillna(0)

    dates = pd.to_datetime(sales["order_date"], errors="coerce", utc=True)
    sales["_order_date"] = dates.dt.strftime("%Y-%m-%d")
    trend = (
        sales.dropna(subset=["_order_date"])
        .groupby("_order_date", as_index=False)["_sales_amount"]
        .sum()
        .sort_values("_order_date")
    )
    if "order_id" in df.columns:
        daily_order_counts = daily_unique_order_counts(
            df["order_id"], df["order_date"]
        )
        trend["_order_count"] = (
            trend["_order_date"].map(daily_order_counts).fillna(0).astype(int)
        )

    sales["_product"] = sales["product"].fillna("（空白）").astype(str)
    product_summary = (
        sales.groupby("_product")
        .agg(
            _sales_amount=("_sales_amount", "sum"),
            _quantity=("_quantity", "sum"),
        )
        .sort_values("_sales_amount", ascending=False)
    )
    top_products = product_summary.head(10)

    trend_figure = go.Figure(
        go.Scatter(
            x=trend["_order_date"].tolist(),
            y=trend["_sales_amount"].tolist(),
            mode="lines+markers+text",
            name="销售额",
            customdata=(
                trend["_order_count"].tolist()
                if "_order_count" in trend.columns
                else None
            ),
            texttemplate="%{y:,.2f} 元",
            textposition="top center",
            hovertemplate=(
                "%{x}<br>销售额：%{y:.2f} 元"
                + (
                    "<br>非空订单数：%{customdata} 笔"
                    if "_order_count" in trend.columns
                    else ""
                )
                + "<extra></extra>"
            ),
        )
    )
    trend_figure.update_layout(
        title="销售趋势",
        xaxis_title="订单日期",
        yaxis_title="销售额（元）",
    )

    top_figure = go.Figure(
        go.Bar(
            x=top_products.index.tolist(),
            y=top_products["_sales_amount"].tolist(),
            customdata=top_products["_quantity"].tolist(),
            name="销售额",
            texttemplate="%{y:,.2f} 元<br>销量：%{customdata:,.0f} 件",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "%{x}<br>销售额：%{y:.2f} 元<br>"
                "商品数量：%{customdata:,.0f} 件<extra></extra>"
            ),
        )
    )
    top_figure.update_layout(
        title="商品 Top10 销售额",
        xaxis_title="商品",
        yaxis_title="销售额（元）",
    )
    top_figure.update_xaxes(tickangle=-30)

    product_names = product_summary.index.tolist()
    product_quantities = product_summary["_quantity"].tolist()
    share_figure = go.Figure(
        go.Pie(
            labels=product_names,
            values=product_summary["_sales_amount"].tolist(),
            customdata=product_quantities,
            texttemplate=(
                "%{label}<br>销量：%{customdata:,.0f} 件<br>%{percent}"
            ),
            textposition="auto",
            hovertemplate=(
                "%{label}<br>销售额：%{value:,.2f} 元<br>"
                "商品数量：%{customdata:,.0f} 件<br>"
                "占比：%{percent}<extra></extra>"
            ),
        )
    )
    share_figure.update_layout(
        title="商品销售占比",
        legend_title_text="商品",
    )

    for figure in (trend_figure, top_figure, share_figure):
        figure.update_layout(
            template="plotly_white",
            autosize=True,
            margin={"l": 55, "r": 20, "t": 65, "b": 60},
        )

    return {
        "sales_trend": _figure_to_dict(trend_figure),
        "product_top10": _figure_to_dict(top_figure),
        "product_share": _figure_to_dict(share_figure),
    }
