"""The Davis Vantage integration."""

from __future__ import annotations
from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import Platform
from .client import DavisVantageClient
from .const import (
    DOMAIN,
    NAME,
    MANUFACTURER,
    CONFIG_STATION_MODEL,
    CONFIG_INTERVAL,
    CONFIG_PROTOCOL,
    CONFIG_LINK,
    CONFIG_PERSISTENT_CONNECTION,
)
from .coordinator import DavisVantageDataUpdateCoordinator
from .services import DavisServicesSetup

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

_LOGGER: logging.Logger = logging.getLogger(__package__)


@dataclass
class RuntimeData:
    """Class to hold your data."""
    coordinator: DavisVantageDataUpdateCoordinator

type DavisConfigEntry = ConfigEntry[RuntimeData]

async def async_setup_entry(
    hass: HomeAssistant, config_entry: DavisConfigEntry
) -> bool:
    """Set up Davis Vantage from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("entry.data: %s", config_entry.data)

    protocol = config_entry.data.get(CONFIG_PROTOCOL, "")
    link = config_entry.data.get(CONFIG_LINK, "")
    persistent_connection = config_entry.data.get(CONFIG_PERSISTENT_CONNECTION, False)

    hass.data[DOMAIN]["interval"] = config_entry.data.get(CONFIG_INTERVAL, 30)

    client = DavisVantageClient(hass, protocol, link, persistent_connection)
    await client.connect_to_station()
    await client.get_station_info()

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.entry_id)},
        manufacturer=MANUFACTURER,
        name=NAME,
        model=config_entry.data.get(CONFIG_STATION_MODEL, "Unknown"),
        sw_version=client.firmware_version,
        hw_version=None,
    )

    coordinator = (
        DavisVantageDataUpdateCoordinator(
            hass=hass, client=client, device_info=device_info, config_entry=config_entry
        )
    )

    await coordinator.async_config_entry_first_refresh()

    config_entry.runtime_data = RuntimeData(coordinator)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    config_entry.async_on_unload(
        config_entry.add_update_listener(async_reload_entry)
    )

    DavisServicesSetup(hass, config_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: DavisConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

async def async_reload_entry(hass: HomeAssistant, config_entry: DavisConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(config_entry.entry_id)
