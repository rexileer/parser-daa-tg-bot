def check_filters(ad, filters):
    """Проверяет, соответствует ли объявление фильтрам пользователя."""

    # Для строковых фильтров проверяем, содержит ли объявление это значение
    def check_string_filter(ad_value, filter_value):
        return filter_value == "unknown" or (filter_value.lower() in ad_value.lower())

    # Для числовых фильтров проверяем, попадает ли значение в диапазон
    def check_numeric_filter(ad_value, filter_value):
        if filter_value == "unknown":
            return True
        try:
            min_value, max_value = map(int, filter_value.split("-"))
            return min_value <= int(ad_value) <= max_value
        except ValueError:
            return False  # Если значение не может быть преобразовано в диапазон, возвращаем False

    if filters["platform"] and not any(check_string_filter(ad["platform"], platform) for platform in filters["platform"]):
        return False

    if filters["price"] and not check_numeric_filter(ad["price"], filters["price"]):
        return False

    if filters["brand"] and not check_string_filter(ad["brand"], filters["brand"]):
        return False

    if filters["engine"] and not check_string_filter(ad["engine"], filters["engine"]):
        return False

    if filters["mileage"] and not check_numeric_filter(ad["mileage"], filters["mileage"]):
        return False

    if filters["gearbox"] and not check_string_filter(ad["gearbox"], filters["gearbox"]):
        return False

    if filters["owners"] and not check_numeric_filter(ad["owners"], filters["owners"]):
        return False

    if filters["condition"] and not check_string_filter(ad["condition"], filters["condition"]):
        return False

    if filters["seller"] and not check_string_filter(ad["seller"], filters["seller"]):
        return False

    if filters["city"] and not check_string_filter(ad["city"], filters["city"]):
        return False

    if filters["year"] and not check_numeric_filter(ad["year"], filters["year"]):
        return False

    if filters["body_type"] and not check_string_filter(ad["body_type"], filters["body_type"]):
        return False

    if filters["color"] and not check_string_filter(ad["color"], filters["color"]):
        return False

    if filters["drive"] and not check_string_filter(ad["drive"], filters["drive"]):
        return False

    if filters["steering"] and not check_string_filter(ad["steering"], filters["steering"]):
        return False

    if filters["ad_type"] and not check_string_filter(ad["ad_type"], filters["ad_type"]):
        return False

    return True
