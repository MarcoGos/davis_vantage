"""Config flow for Davis Vantage integration."""

from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
import serial
import serial.tools.list_ports

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    NAME,
    DOMAIN,
    DEFAULT_SYNC_INTERVAL,
    PROTOCOL_NETWORK,
    PROTOCOL_SERIAL,
    MODEL_VANTAGE_PRO2,
    MODEL_VANTAGE_PRO2PLUS,
    MODEL_VANTAGE_VUE,
    CONFIG_STATION_MODEL,
    CONFIG_INTERVAL,
    CONFIG_MINIMAL_INTERVAL,
    CONFIG_PROTOCOL,
    CONFIG_LINK,
    CONFIG_PERSISTENT_CONNECTION,
)
from .client import DavisVantageClient

RECONFIGURE_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_LINK): str,
        vol.Required(CONFIG_INTERVAL, default=DEFAULT_SYNC_INTERVAL): vol.All(
            int, vol.Range(min=CONFIG_MINIMAL_INTERVAL)  # type: ignore
        ),
    }
)

_LOGGER = logging.getLogger(__name__)


class PlaceholderHub:
    """Placeholder class to make tests pass."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self._hass = hass

    async def authenticate(self, protocol: str, link: str) -> bool:
        """Test if we can find data for the given link."""
        _LOGGER.info("authenticate called")
        client = DavisVantageClient(self._hass, protocol, link, False)
        await client.connect_to_station()
        return (await client.async_get_davis_time()) is not None


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = PlaceholderHub(hass)
    if not await hub.authenticate(data[CONFIG_PROTOCOL], data[CONFIG_LINK]):
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": NAME}


class DavisVantageConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Davis Vantage."""

    VERSION = 1
    protocol: str
    link: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self.protocol = user_input[CONFIG_PROTOCOL]
            if self.protocol == PROTOCOL_SERIAL:
                return await self.async_step_setup_serial()

            return await self.async_step_setup_network()

        list_of_types = [PROTOCOL_SERIAL, PROTOCOL_NETWORK]
        schema = vol.Schema({vol.Required(CONFIG_PROTOCOL): vol.In(list_of_types)})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_setup_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self.link = user_input[CONFIG_LINK]
            return await self.async_step_setup_other_info()

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = {
            port.device: f"{port}, s/n: {port.serial_number or 'n/a'}"
            + (f" - {port.manufacturer}" if port.manufacturer else "")
            for port in ports
        }

        step_user_data_schema = vol.Schema(
            {vol.Required(CONFIG_LINK): vol.In(list_of_ports)}
        )

        return self.async_show_form(
            step_id="setup_serial", data_schema=step_user_data_schema
        )

    async def async_step_setup_network(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self.link = user_input[CONFIG_LINK]
            return await self.async_step_setup_other_info()

        step_user_data_schema = vol.Schema({vol.Required(CONFIG_LINK): str})

        return self.async_show_form(
            step_id="setup_network", data_schema=step_user_data_schema
        )

    async def async_step_setup_other_info(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] | None = {}
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

        step_user_data_schema = vol.Schema(
            {
                vol.Required(CONFIG_STATION_MODEL): vol.In(
                    [MODEL_VANTAGE_PRO2, MODEL_VANTAGE_PRO2PLUS, MODEL_VANTAGE_VUE]
                ),
                vol.Required(CONFIG_INTERVAL, default=DEFAULT_SYNC_INTERVAL): vol.All(
                    int, vol.Range(min=CONFIG_MINIMAL_INTERVAL)  # type: ignore
                ),
                vol.Required(CONFIG_PERSISTENT_CONNECTION, default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="setup_other_info", data_schema=step_user_data_schema, errors=errors
        )

    async def async_step_reconfigure(
        self, _: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a reconfiguration flow initialized by the user."""
        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        return await self.async_step_reconfigure_confirm()

    async def async_step_reconfigure_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a reconfiguration flow initialized by the user."""
        errors: dict[str, str] | None = {}

        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.entry, data=self.entry.data | user_input # type: ignore
            )
            await self.hass.config_entries.async_reload(self.entry.entry_id) # type: ignore
            return self.async_abort(reason="reconfigure_successful")

        step_user_data_schema = RECONFIGURE_SCHEMA
        if self.entry.data.get(CONFIG_PROTOCOL) == PROTOCOL_SERIAL: # type: ignore
            ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
            list_of_ports = {
                port.device: f"{port}, s/n: {port.serial_number or 'n/a'}"
                + (f" - {port.manufacturer}" if port.manufacturer else "")
                for port in ports
            }
            step_user_data_schema = RECONFIGURE_SCHEMA.extend(
                {vol.Required(CONFIG_LINK): vol.In(list_of_ports)},
                required=True
            )

        return self.async_show_form(
            step_id="reconfigure_confirm",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=step_user_data_schema,
                suggested_values=self.entry.data | (user_input or {}), # type: ignore
            ),
            description_placeholders={"name": self.entry.title}, # type: ignore
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
