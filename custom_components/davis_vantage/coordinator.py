import logging
from datetime import timedelta
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyvantagepro.parser import LoopDataParserRevB

from .client import DavisVantageClient
from .const import (
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DavisVantageDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the weather station."""

    def __init__(
        self, hass: HomeAssistant, client: DavisVantageClient, device_info: DeviceInfo, config_entry: config_entries.ConfigEntry,
    ) -> None:
        """Initialize."""
        self.client: DavisVantageClient = client
        self.platforms: list[str] = []
        self.last_updated = None
        self.device_info = device_info
        self._station_info_loaded = False
        self._entry_id = config_entry.entry_id
        interval = hass.data[DOMAIN].get("interval", 30)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
            config_entry=config_entry,
        )

    @callback
    def _async_update_device_sw_version(self, sw_version: str) -> None:
        """Update integration device software version in the device registry."""
        self.device_info["sw_version"] = sw_version
        device_registry = dr.async_get(self.hass)
        if hasattr(device_registry, "async_get_device_by_identifier"):
            device = device_registry.async_get_device_by_identifier((DOMAIN, self._entry_id), self._entry_id)  # type: ignore[attr-defined]
        else:
            device = device_registry.async_get_device(identifiers={(DOMAIN, self._entry_id)})
        if device is not None:
            device_registry.async_update_device(device.id, sw_version=sw_version)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            await self.client.ensure_connected()
            if not self._station_info_loaded:
                await self.client.get_station_info()
                self._station_info_loaded = True
                firmware_version = self.client.firmware_version
                if firmware_version:
                    self._async_update_device_sw_version(firmware_version)
            data: LoopDataParserRevB = await self.client.async_get_current_data()  # type: ignore
            return data
        except Exception as exception:
            _LOGGER.error(
                "Error DavisVantageDataUpdateCoordinator _async_update_data: %s", exception
            )
            raise UpdateFailed() from exception
