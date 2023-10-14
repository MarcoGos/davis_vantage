"""All client function"""
from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import asyncio
from pyvantagepro import VantagePro2
from pyvantagepro.parser import LoopDataParserRevB

from homeassistant.core import HomeAssistant

from .utils import (
    calc_dew_point,
    calc_feels_like,
    calc_wind_chill,
    contains_correct_data,
    calc_heat_index,
    convert_kmh_to_bft,
    convert_to_iso_datetime,
    convert_to_kmh,
    get_baro_trend,
    get_forecast_string,
    get_solar_rad,
    get_uv,
    get_wind_rose,
)
from .const import RAIN_COLLECTOR_METRIC, PROTOCOL_NETWORK

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DavisVantageClient:
    """Davis Vantage Client class"""
    def __init__(
        self,
        hass: HomeAssistant,
        protocol: str,
        link: str,
        rain_collector: str,
        windrose8: bool,
    ) -> None:
        self._hass = hass
        self._protocol = protocol
        self._link = link
        self._windrose8 = windrose8
        self._rain_collector = rain_collector
        self._last_data: LoopDataParserRevB = {}  # type: ignore
        self._vantagepro2 = VantagePro2.from_url(self.get_link())
        self._vantagepro2.link.close()

    def get_current_data(self) -> LoopDataParserRevB | None:
        """Get current date from weather station."""
        try:
            self._vantagepro2.link.open()
            data = self._vantagepro2.get_current_data()
        except Exception as e:
            raise e
        finally:
            self._vantagepro2.link.close()
        return data

    async def async_get_current_data(self) -> LoopDataParserRevB | None:
        """Get current date from weather station async."""
        data = self._last_data
        try:
            loop = asyncio.get_event_loop()
            new_data = await loop.run_in_executor(None, self.get_current_data)
            if new_data:
                if contains_correct_data(new_data):
                    self.add_additional_info(new_data)
                    self.convert_values(new_data)
                    data = new_data
                    data["LastError"] = "No error"
                else:
                    data["LastError"] = "Received incorrect data"
            else:
                data["LastError"] = "Couldn't acquire data, no data received"
        except Exception as e:
            _LOGGER.warning("Couldn't acquire data from %s", self.get_link())
            data["LastError"] = f"Couldn't acquire data: {e}"
        self._last_data = data
        return data

    def get_davis_time(self) -> datetime | None:
        """Get time from weather station."""
        data = None
        try:
            self._vantagepro2.link.open()
            data = self._vantagepro2.gettime()
        except Exception as e:
            raise e
        finally:
            self._vantagepro2.link.close()
        return data

    async def async_get_davis_time(self) -> datetime | None:
        """Get time from weather station async."""
        data = None
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.get_davis_time)
        except Exception as e:
            _LOGGER.error("Couldn't get davis time: %s", e)
        return data

    def set_davis_time(self, dtime: datetime) -> None:
        """Set time of weather station."""
        try:
            self._vantagepro2.link.open()
            self._vantagepro2.settime(dtime)
        except Exception as e:
            raise e
        finally:
            self._vantagepro2.link.close()

    async def async_set_davis_time(self) -> None:
        """Set time of weather station async."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.set_davis_time, datetime.now())
        except Exception as e:
            _LOGGER.error("Couldn't set davis time: %s", e)

    def add_additional_info(self, data: dict[str, Any]) -> None:
        """Add additional info like heatindex, windchill etc."""
        data["HeatIndex"] = calc_heat_index(data["TempOut"], data["HumOut"])
        data["WindChill"] = calc_wind_chill(data["TempOut"], data["WindSpeed"])
        data["FeelsLike"] = calc_feels_like(
            data["TempOut"], data["HumOut"], data["WindSpeed"]
        )
        data["WindDirRose"] = get_wind_rose(data["WindDir"], self._windrose8)
        data["DewPoint"] = calc_dew_point(data["TempOut"], data["HumOut"])
        data["WindSpeedBft"] = convert_kmh_to_bft(
            convert_to_kmh(data["WindSpeed10Min"])
        )
        data["IsRaining"] = data["RainRate"] > 0

    def convert_values(self, data: dict[str, Any]) -> None:
        """Convert values like date to iso, bartrend etc."""
        data["Datetime"] = convert_to_iso_datetime(
            data["Datetime"], ZoneInfo(self._hass.config.time_zone)
        )
        data["BarTrend"] = get_baro_trend(data["BarTrend"])
        data["UV"] = get_uv(data["UV"])
        data["SolarRad"] = get_solar_rad(data["SolarRad"])
        data["ForecastRuleNo"] = get_forecast_string(data["ForecastRuleNo"])
        data["RainCollector"] = self._rain_collector
        data["WindRoseSetup"] = 8 if self._windrose8 else 16
        if data["RainCollector"] == RAIN_COLLECTOR_METRIC:
            self.correct_rain_values(data)

    def correct_rain_values(self, data: dict[str, Any]):
        """Correct rain values when using matrix system."""
        data["RainDay"] *= 2 / 2.54
        data["RainMonth"] *= 2 / 2.54
        data["RainYear"] *= 2 / 2.54
        data["RainRate"] *= 2 / 2.54

    def get_link(self) -> str | None:
        """Get device link for use with vproweather."""
        if self._protocol == PROTOCOL_NETWORK:
            return f"tcp:{self._link}"
        return f"serial:{self._link}:19200:8N1"
