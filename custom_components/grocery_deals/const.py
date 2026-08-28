"""Constants for the Grocery Deals integration."""

from __future__ import annotations

DOMAIN = "grocery_deals"
ATTRIBUTION = (
    "Aggregated from Supermarket integrations (REWE, EDEKA, Lidl, ALDI, Norma)"
)
PLATFORMS = ["sensor"]

# Configuration keys
CONF_PRODUCT_FILTERS = "product_filters"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_AUTO_DETECT_PROVIDERS = "auto_detect_providers"
CONF_ENABLED_PROVIDERS = "enabled_providers"

# Defaults
DEFAULT_UPDATE_INTERVAL = 6  # hours
MIN_UPDATE_INTERVAL = 1  # hours
MAX_UPDATE_INTERVAL = 24  # hours

# Supported supermarket integrations
SUPPORTED_INTEGRATIONS: dict[str, dict[str, str]] = {
    "rewe": {
        "name": "REWE",
        "github": "https://github.com/FaserF/ha-rewe",
        "description": "REWE weekly offers & digital coupons",
    },
    "edeka": {
        "name": "EDEKA",
        "github": "https://github.com/FaserF/ha-edeka",
        "description": "EDEKA weekly offers & market discounts",
    },
    "lidl": {
        "name": "Lidl",
        "github": "https://github.com/FaserF/ha-lidl",
        "description": "Lidl Plus weekly offers & brochures",
    },
    "aldi": {
        "name": "ALDI",
        "github": "https://github.com/FaserF/ha-aldi",
        "description": "ALDI Süd / Nord weekly flyers & brochures",
    },
    "norma": {
        "name": "Norma",
        "github": "https://github.com/FaserF/ha-norma",
        "description": "Norma weekly discounts & flyer offers",
    },
}

# Sensor attributes
ATTR_MATCH_COUNT = "match_count"
ATTR_BEST_PRICE = "best_price"
ATTR_BEST_STORE = "best_store"
ATTR_ON_SALE = "on_sale"
ATTR_ON_SALE_STORES = "on_sale_stores"
ATTR_OFFERS = "offers"
ATTR_ALL_PRICES = "all_prices"
ATTR_LAST_SEARCH = "last_search"
