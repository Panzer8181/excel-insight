"""Shared order identifier counting rules for KPIs and charts."""

import pandas as pd


def _normalize_order_ids(order_ids):
    normalized = order_ids.astype("string").str.strip()
    blank_mask = normalized.isna() | normalized.eq("").fillna(False)
    return normalized.mask(blank_mask), int(blank_mask.sum())


def count_unique_order_ids(order_ids):
    """Return the number of unique nonblank IDs and the number of blank IDs."""
    normalized, blank_count = _normalize_order_ids(order_ids)
    return int(normalized.nunique(dropna=True)), blank_count


def daily_unique_order_counts(order_ids, order_dates):
    """Return per-date distinct order counts using the same ID rules as KPIs."""
    normalized, _ = _normalize_order_ids(order_ids)
    dates = pd.to_datetime(order_dates, errors="coerce", utc=True).dt.strftime(
        "%Y-%m-%d"
    )
    dated_orders = pd.DataFrame({"date": dates, "order_id": normalized})
    counts = (
        dated_orders.dropna(subset=["date"])
        .groupby("date")["order_id"]
        .nunique(dropna=True)
    )
    return counts.to_dict()
