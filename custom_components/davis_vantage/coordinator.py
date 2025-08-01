from datetime import timedelta
from typing import Any
import logging

from homeassistant import config_entries
from homeassistant.helpers.update_coordinator import UpdateFailed, DataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant
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
        interval = hass.data[DOMAIN].get("interval", 30)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            data: LoopDataParserRevB = await self.client.async_get_current_data()  # type: ignore
            return data
        except Exception as exception:
            _LOGGER.error(
                "Error DavisVantageDataUpdateCoordinator _async_update_data: %s", exception
            )
            raise UpdateFailed() from exception
