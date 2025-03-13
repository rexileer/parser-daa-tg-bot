def check_filters(ad, filters):
    """Проверяет, соответствует ли объявление фильтрам пользователя."""
    
    if filters["platform"] and ad["platform"] != filters["platform"]:
        return False

    if filters["price"]:
        price_min, price_max = map(int, filters["price"].split("-"))
        if not (price_min <= int(ad["price"]) <= price_max):
            return False

    if filters["brand"] and ad["brand"].lower() != filters["brand"].lower():
        return False

    if filters["engine"] and ad["engine"] != filters["engine"]:
        return False

    if filters["mileage"]:
        mileage_min, mileage_max = map(int, filters["mileage"].split("-"))
        if not (mileage_min <= int(ad["mileage"]) <= mileage_max):
            return False

    if filters["gearbox"] and ad["gearbox"] != filters["gearbox"]:
        return False

    if filters["owners"]:
        owners_list = list(map(int, filters["owners"].split(",")))
        if int(ad["owners"]) not in owners_list:
            return False

    if filters["condition"] and ad["condition"] != filters["condition"]:
        return False

    if filters["seller"] and ad["seller"] != filters["seller"]:
        return False

    if filters["city"] and ad["city"].lower() != filters["city"].lower():
        return False

    if filters["year"]:
        year_min, year_max = map(int, filters["year"].split("-"))
        if not (year_min <= int(ad["year"]) <= year_max):
            return False

    if filters["body_type"] and ad["body_type"] != filters["body_type"]:
        return False

    if filters["color"] and ad["color"] != filters["color"]:
        return False

    if filters["drive"] and ad["drive"] != filters["drive"]:
        return False

    if filters["steering"] and ad["steering"] != filters["steering"]:
        return False

    if filters["ad_type"] and ad["ad_type"] != filters["ad_type"]:
        return False

    return True
