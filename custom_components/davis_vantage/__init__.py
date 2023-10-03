"""The Davis Vantage integration."""
from __future__ import annotations
from typing import Any
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import Platform

from .client import DavisVantageClient
from .const import DOMAIN, NAME, VERSION, MANUFACTURER
from .coordinator import DavisVantageDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR
]

_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup(hass: HomeAssistant, config: Any) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Davis Vantage from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug(f"entry.data: {entry.data}")

    protocol = entry.data.get("protocol", "")
    link = entry.data.get("link", "")
    rain_collector = entry.data.get("rain_collector", "0.01""")
    windrose8 = entry.data.get("windrose8", False)
    
    hass.data[DOMAIN]['interval'] = entry.data.get("interval", 30)

    client = DavisVantageClient(hass, protocol, link, rain_collector, windrose8)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        name=NAME,
        sw_version=VERSION
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator = DavisVantageDataUpdateCoordinator(
        hass=hass, client=client, device_info=device_info)

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
