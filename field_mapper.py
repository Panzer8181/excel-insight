FIELD_ALIASES = {
    "order_id": ("订单编号", "订单号", "order", "id"),
    "quantity": ("数量", "销售数量", "购买数量", "qty"),
    "unit_price": ("价格", "单价", "售价", "成交价", "price"),
}


def _normalize_column(column):
    if not isinstance(column, str):
        return None
    return column.strip().casefold()


def map_fields(columns):
    """Map source column names to standard fields, or return missing fields."""
    columns_by_normalized_name = {}
    for column in columns:
        normalized = _normalize_column(column)
        if normalized and normalized not in columns_by_normalized_name:
            columns_by_normalized_name[normalized] = column

    mapping = {}
    missing_fields = []

    for standard_field, aliases in FIELD_ALIASES.items():
        # Prefer the canonical column name when both it and an alias exist.
        candidates = (standard_field, *aliases)
        source_column = next(
            (
                columns_by_normalized_name[_normalize_column(candidate)]
                for candidate in candidates
                if _normalize_column(candidate) in columns_by_normalized_name
            ),
            None
        )

        if source_column is None:
            missing_fields.append(standard_field)
        else:
            mapping[standard_field] = source_column

    return missing_fields if missing_fields else mapping
