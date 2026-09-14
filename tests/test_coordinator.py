"""Tests for Grocery Deals coordinator, aggregation and sensors."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.grocery_deals.const import CONF_PRODUCT_FILTERS
from custom_components.grocery_deals.coordinator import (
    GroceryDealsCoordinator,
    parse_price_value,
)


def test_parse_price_value():
    """Test price string parsing."""
    assert parse_price_value("1,49 €") == 1.49
    assert parse_price_value("0.88") == 0.88
    assert parse_price_value("3,99 € / 1 kg") == 3.99
    assert parse_price_value(None) is None
    assert parse_price_value("Knaller") is None


@pytest.mark.asyncio
async def test_coordinator_aggregation(hass: HomeAssistant):
    """Test offer collection and price comparison."""
    entry = MagicMock()
    entry.data = {
        CONF_PRODUCT_FILTERS: ["Monster Energy", "Butter"],
    }
    entry.options = {}

    with patch("homeassistant.helpers.storage.Store.async_load", return_value=None):
        coordinator = GroceryDealsCoordinator(hass, entry)

    mock_rewe_entry = MagicMock()
    mock_rewe_entry.entry_id = "rewe_1"
    mock_rewe_entry.title = "REWE Markt Zorneding"
    mock_rewe_entry.state = "loaded"

    mock_lidl_entry = MagicMock()
    mock_lidl_entry.entry_id = "lidl_1"
    mock_lidl_entry.title = "Lidl Filiale"
    mock_lidl_entry.state = "loaded"

    with patch.object(
        coordinator,
        "get_configured_providers",
        return_value={"rewe": [mock_rewe_entry], "lidl": [mock_lidl_entry]},
    ):
        mock_rewe_coord = MagicMock()
        mock_rewe_coord.data = {
            "discounts": [
                {
                    "product": "Monster Energy Drink 0,5l",
                    "price": "1,19 €",
                    "base_price": "1 l = 2,38 €",
                    "category": "Getränke",
                },
                {
                    "product": "Kerrygold Butter 250g",
                    "price": "1,79 €",
                    "base_price": "1 kg = 7,16 €",
                    "category": "Molkerei",
                },
            ]
        }

        mock_lidl_coord = MagicMock()
        mock_lidl_coord.data = {
            "offers": [
                {
                    "title": "Monster Energy Dose",
                    "price": "0,88 €",
                    "subtitle": "500ml",
                    "category": "Aktion",
                }
            ]
        }

        hass.data = {
            "rewe": {"rewe_1": mock_rewe_coord},
            "lidl": {"lidl_1": mock_lidl_coord},
        }

        data = await coordinator._async_update_data()

        assert "filters" in data
        monster_deal = data["filters"]["Monster Energy"]
        assert monster_deal["on_sale"] is True
        assert monster_deal["match_count"] == 2
        # Lidl is cheapest (0.88 vs 1.19)
        assert monster_deal["best_price"] == "0,88 €"
        assert monster_deal["best_store"] == "Lidl Filiale"
        assert set(monster_deal["on_sale_stores"]) == {"Lidl", "REWE"}

        butter_deal = data["filters"]["Butter"]
        assert butter_deal["on_sale"] is True
        assert butter_deal["match_count"] == 1
        assert butter_deal["best_price"] == "1,79 €"
        assert butter_deal["best_store"] == "REWE Markt Zorneding"


@pytest.mark.asyncio
async def test_coordinator_aggregation_with_penny(hass: HomeAssistant):
    """Test offer collection including PENNY digital receipt items."""
    entry = MagicMock()
    entry.data = {
        CONF_PRODUCT_FILTERS: ["Pepsi"],
    }
    entry.options = {}

    with patch("homeassistant.helpers.storage.Store.async_load", return_value=None):
        coordinator = GroceryDealsCoordinator(hass, entry)

    mock_penny_entry = MagicMock()
    mock_penny_entry.entry_id = "penny_1"
    mock_penny_entry.title = "PENNY Markt"
    mock_penny_entry.state = "loaded"

    with patch.object(
        coordinator,
        "get_configured_providers",
        return_value={"penny": [mock_penny_entry]},
    ):
        mock_penny_coord = MagicMock()
        mock_penny_coord.data = {
            "last_receipt": {
                "items": [
                    {
                        "name": "Pepsi Cola Zero",
                        "price": 8.94,
                        "tax_code": "A",
                        "quantity": 2,
                        "unit_price": 4.47,
                    }
                ]
            }
        }

        hass.data = {
            "penny": {"penny_1": mock_penny_coord},
        }

        data = await coordinator._async_update_data()
        assert "filters" in data
        pepsi_deal = data["filters"]["Pepsi"]
        assert pepsi_deal["on_sale"] is True
        assert pepsi_deal["match_count"] == 1
        assert pepsi_deal["best_store"] == "PENNY Markt"
