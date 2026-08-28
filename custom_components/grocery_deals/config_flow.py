"""Config flow for Grocery Deals integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    BooleanSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_AUTO_DETECT_PROVIDERS,
    CONF_ENABLED_PROVIDERS,
    CONF_PRODUCT_FILTERS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    SUPPORTED_INTEGRATIONS,
)

_LOGGER = logging.getLogger(__name__)


class GroceryDealsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grocery Deals."""

    VERSION = 1

    def _get_detected_integrations(self) -> tuple[list[str], list[str]]:
        """Return lists of detected and missing supermarket integrations."""
        detected: list[str] = []
        missing: list[str] = []

        for domain in SUPPORTED_INTEGRATIONS:
            entries = self.hass.config_entries.async_entries(domain)
            if entries:
                detected.append(domain)
            else:
                missing.append(domain)

        return detected, missing

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id("grocery_deals_hub")
        self._abort_if_unique_id_configured()

        detected, missing = self._get_detected_integrations()

        if user_input is not None:
            raw_filters = user_input.get(CONF_PRODUCT_FILTERS, [])
            if isinstance(raw_filters, str):
                product_filters = [
                    f.strip()
                    for f in raw_filters.replace("\n", ",").split(",")
                    if f.strip()
                ]
            elif isinstance(raw_filters, list):
                product_filters = [
                    str(f).strip() for f in raw_filters if str(f).strip()
                ]
            else:
                product_filters = []

            return self.async_create_entry(
                title="Grocery Deals",
                data={
                    CONF_PRODUCT_FILTERS: product_filters,
                    CONF_UPDATE_INTERVAL: int(
                        user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                    ),
                    CONF_AUTO_DETECT_PROVIDERS: bool(
                        user_input.get(CONF_AUTO_DETECT_PROVIDERS, True)
                    ),
                    CONF_ENABLED_PROVIDERS: user_input.get(
                        CONF_ENABLED_PROVIDERS, detected
                    ),
                },
            )

        # Build informative placeholders with GitHub links
        detected_text = (
            "\n".join(
                f"✅ **[{SUPPORTED_INTEGRATIONS[d]['name']}]({SUPPORTED_INTEGRATIONS[d]['github']})** ({len(self.hass.config_entries.async_entries(d))} store(s) configured)"
                for d in detected
            )
            or "_None detected yet._"
        )

        missing_text = (
            "\n".join(
                f"❌ **[{SUPPORTED_INTEGRATIONS[d]['name']}]({SUPPORTED_INTEGRATIONS[d]['github']})** - {SUPPORTED_INTEGRATIONS[d]['description']}"
                for d in missing
            )
            or "_All supported supermarket integrations are installed!_"
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PRODUCT_FILTERS, default=["Monster Energy", "Butter", "Kaffee"]
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            "Monster Energy",
                            "Butter",
                            "Kaffee",
                            "Milch",
                            "Bier",
                            "Schokolade",
                        ],
                        multiple=True,
                        custom_value=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_UPDATE_INTERVAL,
                        max=MAX_UPDATE_INTERVAL,
                        step=1,
                        unit_of_measurement="hours",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_AUTO_DETECT_PROVIDERS, default=True): BooleanSelector(
                    BooleanSelectorConfig()
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "detected_integrations": detected_text,
                "missing_integrations": missing_text,
                "detected_count": str(len(detected)),
            },
        )

    async def async_step_integration_discovery(
        self, discovery_info: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle automatic discovery when >= 2 supermarket integrations exist."""
        await self.async_set_unique_id("grocery_deals_hub")
        self._abort_if_unique_id_configured()

        detected, missing = self._get_detected_integrations()
        if len(detected) < 2:
            return self.async_abort(reason="insufficient_supermarkets")

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirm auto-discovery entry creation."""
        detected, _ = self._get_detected_integrations()
        if user_input is not None:
            return self.async_create_entry(
                title="Grocery Deals",
                data={
                    CONF_PRODUCT_FILTERS: ["Monster Energy", "Butter", "Kaffee"],
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL,
                    CONF_AUTO_DETECT_PROVIDERS: True,
                    CONF_ENABLED_PROVIDERS: detected,
                },
            )

        detected_names = ", ".join(SUPPORTED_INTEGRATIONS[d]["name"] for d in detected)
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={
                "detected_count": str(len(detected)),
                "detected_stores": detected_names,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GroceryDealsOptionsFlowHandler:
        """Return the options flow handler."""
        return GroceryDealsOptionsFlowHandler(config_entry)


class GroceryDealsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Grocery Deals."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            raw_filters = user_input.get(CONF_PRODUCT_FILTERS, [])
            if isinstance(raw_filters, str):
                product_filters = [
                    f.strip()
                    for f in raw_filters.replace("\n", ",").split(",")
                    if f.strip()
                ]
            elif isinstance(raw_filters, list):
                product_filters = [
                    str(f).strip() for f in raw_filters if str(f).strip()
                ]
            else:
                product_filters = []

            return self.async_create_entry(
                title="",
                data={
                    CONF_PRODUCT_FILTERS: product_filters,
                    CONF_UPDATE_INTERVAL: int(
                        user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                    ),
                    CONF_AUTO_DETECT_PROVIDERS: bool(
                        user_input.get(CONF_AUTO_DETECT_PROVIDERS, True)
                    ),
                    CONF_ENABLED_PROVIDERS: user_input.get(
                        CONF_ENABLED_PROVIDERS, list(SUPPORTED_INTEGRATIONS.keys())
                    ),
                },
            )

        current_filters = self._config_entry.options.get(
            CONF_PRODUCT_FILTERS,
            self._config_entry.data.get(
                CONF_PRODUCT_FILTERS, ["Monster Energy", "Butter"]
            ),
        )
        current_interval = self._config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            self._config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )
        current_auto_detect = self._config_entry.options.get(
            CONF_AUTO_DETECT_PROVIDERS,
            self._config_entry.data.get(CONF_AUTO_DETECT_PROVIDERS, True),
        )
        current_enabled = self._config_entry.options.get(
            CONF_ENABLED_PROVIDERS,
            self._config_entry.data.get(
                CONF_ENABLED_PROVIDERS, list(SUPPORTED_INTEGRATIONS.keys())
            ),
        )

        detected = [
            d
            for d in SUPPORTED_INTEGRATIONS
            if self.hass.config_entries.async_entries(d)
        ]
        missing = [
            d
            for d in SUPPORTED_INTEGRATIONS
            if not self.hass.config_entries.async_entries(d)
        ]

        detected_text = (
            "\n".join(
                f"✅ **[{SUPPORTED_INTEGRATIONS[d]['name']}]({SUPPORTED_INTEGRATIONS[d]['github']})** ({len(self.hass.config_entries.async_entries(d))} store(s) configured)"
                for d in detected
            )
            or "_None detected yet._"
        )

        missing_text = (
            "\n".join(
                f"❌ **[{SUPPORTED_INTEGRATIONS[d]['name']}]({SUPPORTED_INTEGRATIONS[d]['github']})** - {SUPPORTED_INTEGRATIONS[d]['description']}"
                for d in missing
            )
            or "_All supported supermarket integrations are installed!_"
        )

        provider_options = {
            d: SUPPORTED_INTEGRATIONS[d]["name"] for d in SUPPORTED_INTEGRATIONS
        }

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PRODUCT_FILTERS, default=current_filters
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=current_filters,
                        multiple=True,
                        custom_value=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=current_interval
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_UPDATE_INTERVAL,
                        max=MAX_UPDATE_INTERVAL,
                        step=1,
                        unit_of_measurement="hours",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_AUTO_DETECT_PROVIDERS, default=current_auto_detect
                ): BooleanSelector(BooleanSelectorConfig()),
                vol.Optional(
                    CONF_ENABLED_PROVIDERS, default=current_enabled
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": k, "label": v}
                            for k, v in provider_options.items()
                        ],
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "detected_integrations": detected_text,
                "missing_integrations": missing_text,
            },
        )
