"""Grocery Deals – Home Assistant Supermarket Deals Aggregator."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries, core
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS, SUPPORTED_INTEGRATIONS
from .coordinator import GroceryDealsCoordinator

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: core.HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Grocery Deals integration."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    async def _check_and_discover(event: core.Event | None = None) -> None:
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
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
                    data={"detected_domains": detected_domains},
                )
            )

    if not domain_data.get("_discovery_registered"):
        domain_data["_discovery_registered"] = True
        if hass.is_running:
            hass.async_create_task(_check_and_discover())
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _check_and_discover)

    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up Grocery Deals from a config entry."""
    _LOGGER.debug("Setting up Grocery Deals entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})

    coordinator = GroceryDealsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_options(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
