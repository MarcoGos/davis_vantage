"""The Davis Vantage integration."""
from __future__ import annotations
from typing import Any
import logging
import json
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import Platform
from .client import DavisVantageClient
from .const import (
    DOMAIN,
    NAME,
    MANUFACTURER,
    RAIN_COLLECTOR_IMPERIAL,
    SERVICE_SET_DAVIS_TIME,
    SERVICE_GET_DAVIS_TIME,
    SERVICE_GET_RAW_DATA,
    SERVICE_GET_INFO,
    CONFIG_RAIN_COLLECTOR,
    CONFIG_STATION_MODEL,
    CONFIG_INTERVAL,
    CONFIG_PROTOCOL,
    CONFIG_LINK,
    DATA_ARCHIVE_PERIOD
)
from .coordinator import DavisVantageDataUpdateCoordinator
from .utils import convert_to_iso_datetime

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

    _LOGGER.debug("entry.data: %s", entry.data)

    protocol = entry.data.get(CONFIG_PROTOCOL, "")
    link = entry.data.get(CONFIG_LINK, "")
    rain_collector = entry.data.get(CONFIG_RAIN_COLLECTOR, RAIN_COLLECTOR_IMPERIAL)

    hass.data[DOMAIN]['interval'] = entry.data.get(CONFIG_INTERVAL, 30)

    client = DavisVantageClient(hass, protocol, link, rain_collector)
    await client.connect_to_station()
    static_info = await client.async_get_static_info()
    firmware_version = static_info.get('version', None) if static_info is not None else None
    hass.data.setdefault(DATA_ARCHIVE_PERIOD, static_info.get('archive_period', None) if static_info is not None else None)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        name=NAME,
        model=entry.data.get(CONFIG_STATION_MODEL, "Unknown"),
        sw_version=firmware_version,
        hw_version=None
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator = DavisVantageDataUpdateCoordinator(
        hass=hass, client=client, device_info=device_info)

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    async def set_davis_time(call: ServiceCall) -> None:
        await client.async_set_davis_time()

    async def get_davis_time(call: ServiceCall) -> dict[str, Any]:
        davis_time = await client.async_get_davis_time()
        if davis_time is not None:
            return {
                "davis_time": convert_to_iso_datetime(davis_time, ZoneInfo(hass.config.time_zone)) 
            }
        else:
            return {
                "error": "Couldn't get davis time, please try again later"
            }

    async def get_raw_data(call: ServiceCall) -> dict[str, Any]:
        raw_data = client.get_raw_data()
        json_data = safe_serialize(raw_data)
        return json.loads(json_data)

    async def get_info(call: ServiceCall) -> dict[str, Any]:
        info = await client.async_get_info()
        if info is not None:
            return info
        else:
            return {
                "error": "Couldn't get firmware information from Davis weather station"
            }

    hass.services.async_register(
        DOMAIN, SERVICE_SET_DAVIS_TIME, set_davis_time
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET_DAVIS_TIME, get_davis_time, supports_response=SupportsResponse.ONLY
    )

    hass.services.async_register(
        DOMAIN, SERVICE_GET_RAW_DATA, get_raw_data, supports_response=SupportsResponse.ONLY
    )

    hass.services.async_register(
        DOMAIN, SERVICE_GET_INFO, get_info, supports_response=SupportsResponse.ONLY
    )

    def safe_serialize(obj: Any):
        default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>" # type: ignore
        return json.dumps(obj, default=default) # type: ignore

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
