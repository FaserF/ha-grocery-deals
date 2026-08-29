"""Grocery Deals – Home Assistant Supermarket Deals Aggregator."""

from __future__ import annotations

import logging
import re
from typing import Any

from homeassistant import config_entries, core
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import CONF_PRODUCT_FILTERS, DOMAIN, PLATFORMS, SUPPORTED_INTEGRATIONS
from .coordinator import GroceryDealsCoordinator

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: core.HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Grocery Deals integration."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    async def _check_and_discover(*args: Any, **kwargs: Any) -> None:
        """Check if >=2 supermarket integrations are configured and trigger auto discovery."""
        if hass.config_entries.async_entries(DOMAIN):
            return

        detected_domains = [
            domain
            for domain in SUPPORTED_INTEGRATIONS
            if hass.config_entries.async_entries(domain)
        ]

        if len(detected_domains) >= 2:
            _LOGGER.info(
                "Grocery Deals auto-discovery: detected %d supermarket integrations (%s)",
                len(detected_domains),
                ", ".join(detected_domains),
            )
            # Avoid triggering duplicate flows if one is already in progress
            current_flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
            if not current_flows:
                hass.async_create_task(
                    hass.config_entries.flow.async_init(
                        DOMAIN,
                        context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
                        data={"detected_domains": detected_domains},
                    )
                )

    domain_data["check_and_discover"] = _check_and_discover

    if not domain_data.get("_discovery_registered"):
        domain_data["_discovery_registered"] = True
        if hass.is_running:
            hass.async_create_task(_check_and_discover())
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _check_and_discover)

        # Also listen whenever a new config entry is loaded / added
        hass.bus.async_listen("config_entry_updated", _check_and_discover)
        hass.bus.async_listen("component_loaded", _check_and_discover)

    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up Grocery Deals from a config entry."""
    _LOGGER.debug("Setting up Grocery Deals entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})

    coordinator = GroceryDealsCoordinator(hass, entry)
    await coordinator.async_load_cache()
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_options(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> None:
    """Remove stale filter entities and reload the entry when options change."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    old_filters: list[str] = []
    if coordinator is not None:
        old_filters = list(coordinator.product_filters)

    new_filters: list[str] = [
        f.strip() for f in entry.options.get(CONF_PRODUCT_FILTERS, []) if f.strip()
    ]
    removed_filters = [f for f in old_filters if f not in new_filters]

    if removed_filters:
        ent_reg = er.async_get(hass)
        for filter_word in removed_filters:
            slug = (
                re.sub(r"[^a-zA-Z0-9_]+", "_", filter_word.lower()).strip("_") or "deal"
            )
            unique_id = f"grocery_deals_filter_{slug}"
            entity_entry = ent_reg.async_get_entity_id("sensor", DOMAIN, unique_id)
            if entity_entry:
                ent_reg.async_remove(entity_entry)
                _LOGGER.debug(
                    "Removed stale filter entity for '%s' (unique_id=%s)",
                    filter_word,
                    unique_id,
                )

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
