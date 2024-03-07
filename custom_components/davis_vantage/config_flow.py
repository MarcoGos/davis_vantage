"""Config flow for Davis Vantage integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
import serial
import serial.tools.list_ports

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    NAME,
    DOMAIN,
    DEFAULT_SYNC_INTERVAL,
    RAIN_COLLECTOR_IMPERIAL,
    RAIN_COLLECTOR_METRIC,
    PROTOCOL_NETWORK,
    PROTOCOL_SERIAL,
    MODEL_VANTAGE_PRO2,
    MODEL_VANTAGE_PRO2PLUS,
    MODEL_VANTAGE_VUE,
    CONFIG_RAIN_COLLECTOR,
    CONFIG_STATION_MODEL,
    CONFIG_INTERVAL,
    CONFIG_PROTOCOL,
    CONFIG_LINK
)
from .client import DavisVantageClient

_LOGGER = logging.getLogger(__name__)


class PlaceholderHub:
    """Placeholder class to make tests pass."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self._hass = hass

    async def authenticate(self, protocol: str, link: str) -> bool:
        """Test if we can find data for the given link."""
        _LOGGER.info(f"authenticate called")
        client = DavisVantageClient(self._hass, protocol, link, "")
        await client.connect_to_station()
        return await client.async_get_davis_time() != None


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = PlaceholderHub(hass)
    if not await hub.authenticate(data[CONFIG_PROTOCOL], data[CONFIG_LINK]):
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": NAME}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Davis Vantage."""

    VERSION = 1
    protocol: str
    link: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self.protocol = user_input[CONFIG_PROTOCOL]
            if self.protocol == PROTOCOL_SERIAL:
                return await self.async_step_setup_serial()

            return await self.async_step_setup_network()

        list_of_types = [
            PROTOCOL_SERIAL,
            PROTOCOL_NETWORK
        ]
        schema = vol.Schema({vol.Required(CONFIG_PROTOCOL): vol.In(list_of_types)})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_setup_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            self.link = user_input[CONFIG_LINK]
            return await self.async_step_setup_other_info()

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = {
            port.device: f"{port}, s/n: {port.serial_number or 'n/a'}"
            + (f" - {port.manufacturer}" if port.manufacturer else "")
            for port in ports
        }

        STEP_USER_DATA_SCHEMA = vol.Schema(
            {vol.Required(CONFIG_LINK): vol.In(list_of_ports)}
        )

        return self.async_show_form(
            step_id="setup_serial", data_schema=STEP_USER_DATA_SCHEMA
        )

    async def async_step_setup_network(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            self.link = user_input[CONFIG_LINK]
            return await self.async_step_setup_other_info()

        STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONFIG_LINK): str})

        return self.async_show_form(
            step_id="setup_network", data_schema=STEP_USER_DATA_SCHEMA
        )

    async def async_step_setup_other_info(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            user_input[CONFIG_PROTOCOL] = self.protocol
            user_input[CONFIG_LINK] = self.link
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        list_of_rain_collector = [
            RAIN_COLLECTOR_IMPERIAL,
            RAIN_COLLECTOR_METRIC
        ]
        list_of_station_models = [
            MODEL_VANTAGE_PRO2,
            MODEL_VANTAGE_PRO2PLUS,
            # MODEL_VANTAGE_VUE
        ]
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONFIG_STATION_MODEL): vol.In(list_of_station_models),
                vol.Required(
                    CONFIG_INTERVAL, 
                    default=DEFAULT_SYNC_INTERVAL): vol.All(int, vol.Range(min=30) # type: ignore
                ),
                vol.Required(CONFIG_RAIN_COLLECTOR): vol.In(list_of_rain_collector)
            }
        )

        return self.async_show_form(
            step_id="setup_other_info", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
