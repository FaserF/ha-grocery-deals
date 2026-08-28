"""Data Update Coordinator for Grocery Deals price aggregation."""

from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_AUTO_DETECT_PROVIDERS,
    CONF_ENABLED_PROVIDERS,
    CONF_PRODUCT_FILTERS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    SUPPORTED_INTEGRATIONS,
)

_LOGGER = logging.getLogger(__name__)


def parse_price_value(price_str: Any) -> float | None:
    """Extract numeric float value from formatted price strings like '1,49 €' or '0.99'."""
    if price_str is None:
        return None
    if isinstance(price_str, (int, float)):
        return float(price_str)

    text = str(price_str).replace("\xa0", " ").strip()
    # Find decimal patterns e.g. '1,49' or '1.49'
    match = re.search(r"(\d+(?:[.,]\d{1,2})?)", text)
    if match:
        val_str = match.group(1).replace(",", ".")
        try:
            return float(val_str)
        except ValueError:
            return None
    return None


class GroceryDealsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Aggregates and queries deal data across all configured supermarket integrations."""

    def __init__(self, hass: HomeAssistant, entry: config_entries.ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        config = {**entry.data, **entry.options}
        self.product_filters: list[str] = config.get(CONF_PRODUCT_FILTERS, [])
        self.auto_detect: bool = config.get(CONF_AUTO_DETECT_PROVIDERS, True)
        self.enabled_providers: list[str] = config.get(
            CONF_ENABLED_PROVIDERS, list(SUPPORTED_INTEGRATIONS.keys())
        )

        interval_hours = config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="Grocery Deals Coordinator",
            update_interval=timedelta(hours=interval_hours),
        )

    def get_configured_providers(self) -> dict[str, list[config_entries.ConfigEntry]]:
        """Return a mapping of detected domains to their active config entries."""
        providers: dict[str, list[config_entries.ConfigEntry]] = {}
        for domain in SUPPORTED_INTEGRATIONS:
            entries = self.hass.config_entries.async_entries(domain)
            loaded_entries = [
                e for e in entries if e.state == config_entries.ConfigEntryState.LOADED
            ]
            if loaded_entries:
                providers[domain] = loaded_entries
            elif entries:
                providers[domain] = entries
        return providers

    def _collect_all_store_offers(self) -> list[dict[str, Any]]:
        """Extract offer items from coordinators and states of all active integrations."""
        all_offers: list[dict[str, Any]] = []
        configured = self.get_configured_providers()

        for domain, entries in configured.items():
            if not self.auto_detect and domain not in self.enabled_providers:
                continue

            store_label = SUPPORTED_INTEGRATIONS.get(domain, {}).get(
                "name", domain.capitalize()
            )

            for entry in entries:
                entry_title = (
                    entry.title or f"{store_label} ({entry.data.get('market_id', '')})"
                )

                # 1. Inspect direct coordinator data from hass.data if available
                domain_data = self.hass.data.get(domain, {})
                coordinator = domain_data.get(entry.entry_id)

                offers_found = False
                if coordinator and getattr(coordinator, "data", None):
                    cdata = coordinator.data
                    if isinstance(cdata, dict):
                        # REWE, ALDI, EDEKA format
                        for key in ("discounts", "offers", "bonus_discounts"):
                            for item in cdata.get(key, []):
                                if isinstance(item, dict):
                                    all_offers.append(
                                        self._normalize_offer(
                                            item, domain, store_label, entry_title
                                        )
                                    )
                                    offers_found = True

                # 2. Inspect entity state attributes as fallback
                if not offers_found:
                    for state in self.hass.states.async_all("sensor"):
                        if (
                            state.entity_id.startswith(f"sensor.{domain}_")
                            or domain in state.entity_id
                        ):
                            discounts = state.attributes.get(
                                "discounts"
                            ) or state.attributes.get("offers")
                            if isinstance(discounts, list):
                                for item in discounts:
                                    if isinstance(item, dict):
                                        all_offers.append(
                                            self._normalize_offer(
                                                item, domain, store_label, entry_title
                                            )
                                        )

        return all_offers

    def _normalize_offer(
        self, raw: dict[str, Any], domain: str, store_name: str, entry_title: str
    ) -> dict[str, Any]:
        """Normalize various supermarket offer schemas to a standard format."""
        # Product title
        title = (
            raw.get("product")
            or raw.get("title")
            or raw.get("name")
            or raw.get("header")
            or ""
        )

        # Price
        price_raw = (
            raw.get("price")
            or raw.get("discount_price")
            or raw.get("discountPrice")
            or (
                raw.get("price_box", {}).get("price_val")
                if isinstance(raw.get("price_box"), dict)
                else None
            )
            or ""
        )

        # Base price / subtitle / weight
        base_price = (
            raw.get("base_price")
            or raw.get("subtitle")
            or raw.get("packaging")
            or raw.get("price_per_unit")
            or ""
        )

        # Image link
        picture = (
            raw.get("picture_link")
            or raw.get("picture")
            or raw.get("image_url")
            or raw.get("imageUrl")
            or ""
        )

        # Validity
        valid_until = (
            raw.get("valid_until")
            or raw.get("valid_to")
            or raw.get("end_validity_date")
            or raw.get("validUntil")
            or ""
        )

        # Category
        category = raw.get("category") or raw.get("category_title") or ""

        numeric_price = parse_price_value(price_raw)

        return {
            "title": str(title).strip(),
            "price_raw": str(price_raw).strip(),
            "price_numeric": numeric_price,
            "base_price": str(base_price).strip(),
            "picture": picture,
            "valid_until": valid_until,
            "category": category,
            "domain": domain,
            "store_name": store_name,
            "store_title": entry_title,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Perform aggregation across all active supermarket data sources."""
        all_offers = self._collect_all_store_offers()
        results_by_filter: dict[str, Any] = {}

        for filter_word in self.product_filters:
            clean_filter = filter_word.strip()
            if not clean_filter:
                continue

            search_terms = clean_filter.lower().split()
            matched_offers: list[dict[str, Any]] = []

            for offer in all_offers:
                title = offer["title"].lower()
                category = offer["category"].lower()
                base_price = offer["base_price"].lower()
                combined = f"{title} {category} {base_price}"

                if all(term in combined for term in search_terms):
                    matched_offers.append(offer)

            # Sort matched offers by lowest numeric price first
            valid_priced = [o for o in matched_offers if o["price_numeric"] is not None]
            valid_priced.sort(key=lambda x: x["price_numeric"])
            unpriced = [o for o in matched_offers if o["price_numeric"] is None]
            sorted_offers = valid_priced + unpriced

            # Best price & best store
            best_offer = sorted_offers[0] if sorted_offers else None
            best_price = best_offer["price_raw"] if best_offer else None
            best_store = best_offer["store_title"] if best_offer else None

            # On sale stores set
            on_sale_stores = sorted({o["store_name"] for o in sorted_offers})

            # Breakdown of all prices by store
            all_prices: dict[str, list[dict[str, Any]]] = {}
            for o in sorted_offers:
                sname = o["store_name"]
                all_prices.setdefault(sname, []).append(
                    {
                        "product": o["title"],
                        "price": o["price_raw"],
                        "base_price": o["base_price"],
                        "market": o["store_title"],
                    }
                )

            results_by_filter[clean_filter] = {
                "filter": clean_filter,
                "on_sale": len(sorted_offers) > 0,
                "match_count": len(sorted_offers),
                "best_price": best_price,
                "best_store": best_store,
                "best_offer": best_offer,
                "on_sale_stores": on_sale_stores,
                "all_prices": all_prices,
                "offers": sorted_offers,
            }

        return {
            "filters": results_by_filter,
            "total_offers_analyzed": len(all_offers),
            "providers_count": len(self.get_configured_providers()),
        }
