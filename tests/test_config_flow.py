"""Tests for Grocery Deals config flow."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.grocery_deals.const import CONF_PRODUCT_FILTERS, DOMAIN


@pytest.mark.asyncio
async def test_config_flow_user_step(hass: HomeAssistant):
    """Test user step in config flow."""
    with patch(
        "custom_components.grocery_deals.config_flow.GroceryDealsConfigFlow._get_detected_integrations",
        return_value=(["rewe", "lidl"], ["edeka", "aldi", "norma"]),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "user"

        # Submit form
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_PRODUCT_FILTERS: ["Monster Energy", "Gurke"],
            },
        )
        assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result2["title"] == "Grocery Deals"
        assert result2["data"][CONF_PRODUCT_FILTERS] == ["Monster Energy", "Gurke"]


@pytest.mark.asyncio
async def test_config_flow_discovery(hass: HomeAssistant):
    """Test auto-discovery confirmation."""
    with patch(
        "custom_components.grocery_deals.config_flow.GroceryDealsConfigFlow._get_detected_integrations",
        return_value=(["rewe", "lidl"], ["edeka", "aldi", "norma"]),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
            data={"detected_domains": ["rewe", "lidl"]},
        )
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "discovery_confirm"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={},
        )
        assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result2["title"] == "Grocery Deals"
