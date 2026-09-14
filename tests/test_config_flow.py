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


@pytest.mark.asyncio
async def test_config_flow_user_with_penny_warning(hass: HomeAssistant):
    """Test user step shows warning when PENNY is configured."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    penny_entry = MockConfigEntry(domain="penny", data={"rewe_id": "test_penny"})
    penny_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert "PENNY" in result["description_placeholders"]["ignored_section"]
    assert "no structured weekly offers REST API" in result["description_placeholders"]["ignored_section"]


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant):
    """Test options flow."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PRODUCT_FILTERS: ["Monster Energy"]},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_PRODUCT_FILTERS: ["Monster Energy", "Milch"],
        },
    )
    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_PRODUCT_FILTERS] == ["Monster Energy", "Milch"]
