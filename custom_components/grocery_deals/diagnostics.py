"""Diagnostics support for Grocery Deals integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import GroceryDealsCoordinator

REDACT_CONFIG: set[str] = set()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a Grocery Deals config entry."""
    coordinator: GroceryDealsCoordinator | None = hass.data.get(DOMAIN, {}).get(
        entry.entry_id
    )

    diag_data: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "domain": entry.domain,
            "data": async_redact_data(dict(entry.data), REDACT_CONFIG),
            "options": async_redact_data(dict(entry.options), REDACT_CONFIG),
        },
    }

    if coordinator:
        filters_data = coordinator.data.get("filters", {}) if coordinator.data else {}
        providers = coordinator.get_configured_providers()

        diag_data["coordinator"] = {
            "product_filters": coordinator.product_filters,
            "auto_detect": coordinator.auto_detect,
            "enabled_providers": coordinator.enabled_providers,
            "detected_providers": list(providers.keys()),
            "total_filters": len(filters_data),
            "total_offers_analyzed": coordinator.data.get("total_offers_analyzed", 0)
            if coordinator.data
            else 0,
            "filters_summary": {
                f_name: {
                    "on_sale": info.get("on_sale", False),
                    "match_count": info.get("match_count", 0),
                    "best_price": info.get("best_price"),
                    "best_store": info.get("best_store"),
                    "on_sale_stores": info.get("on_sale_stores", []),
                }
                for f_name, info in filters_data.items()
            },
        }

    return diag_data
