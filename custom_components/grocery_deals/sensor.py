"""Sensor platform for Grocery Deals integration."""

from __future__ import annotations

import logging
import re
from typing import Any

from homeassistant import config_entries
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ALL_PRICES,
    ATTR_BEST_PRICE,
    ATTR_BEST_STORE,
    ATTR_MATCH_COUNT,
    ATTR_OFFERS,
    ATTR_ON_SALE,
    ATTR_ON_SALE_STORES,
    ATTRIBUTION,
    DOMAIN,
)
from .coordinator import GroceryDealsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Grocery Deals sensor platform."""
    coordinator: GroceryDealsCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        GroceryDealsOverviewSensor(coordinator),
    ]

    for filter_word in coordinator.product_filters:
        if filter_word.strip():
            entities.append(GroceryDealsFilterSensor(coordinator, filter_word.strip()))

    async_add_entities(entities, update_before_add=False)


class GroceryDealsOverviewSensor(
    CoordinatorEntity[GroceryDealsCoordinator], SensorEntity
):
    """Overview sensor for Grocery Deals aggregator."""

    _attr_icon = "mdi:shopping"
    _attr_has_entity_name = True
    _attr_name = "Active Deals"
    _unrecorded_attributes = frozenset({"all_matched_deals", "active_providers"})

    def __init__(self, coordinator: GroceryDealsCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "grocery_deals_overview"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "grocery_deals_hub")},
            name="Grocery Deals Hub",
            manufacturer="FaserF",
            model="Supermarket Deals Aggregator",
            configuration_url="https://github.com/FaserF/ha-grocery-deals",
        )

    @property
    def native_value(self) -> int | None:
        """Return total count of matches across all configured filters."""
        if not self.coordinator.data:
            return 0
        filters_data = self.coordinator.data.get("filters", {})
        return sum(f.get("match_count", 0) for f in filters_data.values())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return aggregate statistics."""
        data = self.coordinator.data or {}
        filters_data = data.get("filters", {})
        providers = self.coordinator.get_configured_providers()

        active_filters_on_sale = [
            f_name for f_name, info in filters_data.items() if info.get("on_sale")
        ]

        return {
            "total_filters": len(filters_data),
            "filters_on_sale": active_filters_on_sale,
            "connected_supermarket_integrations": list(providers.keys()),
            "total_offers_analyzed": data.get("total_offers_analyzed", 0),
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }


class GroceryDealsFilterSensor(
    CoordinatorEntity[GroceryDealsCoordinator], SensorEntity
):
    """Sensor representing a specific product search filter across all supermarkets."""

    _attr_icon = "mdi:tag-multiple"
    _attr_has_entity_name = True
    _unrecorded_attributes = frozenset({ATTR_OFFERS, ATTR_ALL_PRICES})

    def __init__(
        self, coordinator: GroceryDealsCoordinator, product_filter: str
    ) -> None:
        super().__init__(coordinator)
        self._product_filter = product_filter
        slug = (
            re.sub(r"[^a-zA-Z0-9_]+", "_", product_filter.lower()).strip("_") or "deal"
        )
        self._attr_unique_id = f"grocery_deals_filter_{slug}"
        self._attr_name = f"Deal {product_filter}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "grocery_deals_hub")},
            name="Grocery Deals Hub",
            manufacturer="FaserF",
            model="Supermarket Deals Aggregator",
            configuration_url="https://github.com/FaserF/ha-grocery-deals",
        )

    @property
    def _filter_data(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("filters", {}).get(self._product_filter, {})

    @property
    def native_value(self) -> str | None:
        """Return best price or status."""
        fdata = self._filter_data
        if not fdata or not fdata.get("on_sale"):
            return "Nicht im Angebot"

        best_price = fdata.get("best_price")
        best_store = fdata.get("best_store")
        if best_price and best_store:
            return f"{best_price} ({best_store.split(' ')[0]})"
        if best_price:
            return str(best_price)
        return "Im Angebot"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed price breakdown and deal attributes."""
        fdata = self._filter_data
        best_offer = fdata.get("best_offer") or {}

        return {
            "filter": self._product_filter,
            ATTR_ON_SALE: bool(fdata.get("on_sale", False)),
            ATTR_MATCH_COUNT: fdata.get("match_count", 0),
            ATTR_BEST_PRICE: fdata.get("best_price"),
            ATTR_BEST_STORE: fdata.get("best_store"),
            "best_product": best_offer.get("title"),
            "best_base_price": best_offer.get("base_price"),
            "picture_link": best_offer.get("picture"),
            "valid_until": best_offer.get("valid_until"),
            ATTR_ON_SALE_STORES: fdata.get("on_sale_stores", []),
            ATTR_ALL_PRICES: fdata.get("all_prices", {}),
            ATTR_OFFERS: fdata.get("offers", []),
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
