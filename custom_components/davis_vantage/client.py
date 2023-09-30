from typing import Any
from datetime import datetime
import logging
from pyvantagepro import VantagePro2
from pyvantagepro.parser import LoopDataParserRevB

from homeassistant.core import HomeAssistant

from .utils import *
from .const import RAIN_COLLECTOR_METRIC, PROTOCOL_NETWORK, PROTOCOL_SERIAL

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

class DavisVantageClient:
    def __init__(
        self,
        hass: HomeAssistant,
        protocol: str,
        link: str,
        rain_collector: str,
        windrose8: bool
    ) -> None:
        self._hass = hass
        self._protocol = protocol
        self._link = link
        self._windrose8 = windrose8
        self._rain_collector = rain_collector
        self._last_data = LoopDataParserRevB

    async def async_get_current_data(self) -> LoopDataParserRevB | None:
        """Get current date from weather station."""
        data = self._last_data
        try:
            vantagepro2 = VantagePro2.from_url(self.get_link()) # type: ignore
            # vantagepro2.link.open() # type: ignore
            data = vantagepro2.get_current_data()
            if data:
                self.add_additional_info(data)
                self.convert_values(data)
                data['LastError'] = "No error"
                self._last_data = data
            else:
                data['LastError'] = "Couldn't acquire data"
        except Exception as e:
            _LOGGER.warning(f"Couldn't acquire data from {self._link}")
            data['LastError'] = f"Couldn't acquire data: {e}" # type: ignore
        # finally:
            # vantagepro2.link.close() # type: ignore
        return data # type: ignore

    async def async_get_davis_time(self) -> datetime | None:
        """Get time from weather station."""
        data = None
        try:
            vantagepro2 = VantagePro2.from_url(self.get_link()) # type: ignore
            # vantagepro2.link.open() # type: ignore
            data = vantagepro2.gettime()
        except Exception:
            _LOGGER.warning(f"Couldn't acquire data from {self._link}")
        # finally:
        #     vantagepro2.link.close() # type: ignore
        return data
    
    def add_additional_info(self, data: dict[str, Any]) -> None:
        data['HeatIndex'] = calc_heat_index(data['TempOut'], data['HumOut'])
        data['WindChill'] = calc_wind_chill(data['TempOut'], data['WindSpeed'])
        data['FeelsLike'] = calc_feels_like(data['TempOut'], data['HumOut'], data['WindSpeed'])
        data['WindDirRose'] = get_wind_rose(data['WindDir'], self._windrose8)
        data['DewPoint'] = calc_dew_point(data['TempOut'], data['HumOut'])
        data['WindSpeedBft'] = convert_kmh_to_bft(convert_to_kmh(data['WindSpeed10Min']))
        data['IsRaining'] = data['RainRate'] > 0

    def convert_values(self, data: dict[str, Any]) -> None:
        data['Datetime'] = convert_to_iso_datetime(data['Datetime'], ZoneInfo(self._hass.config.time_zone))
        data['BarTrend'] = get_baro_trend(data['BarTrend'])
        data['UV'] = get_uv(data['UV'])
        data['ForecastRuleNo'] = get_forecast_string(data['ForecastRuleNo'])
        data['RainCollector'] = self._rain_collector
        data['WindRoseSetup'] = 8 if self._windrose8 else 16
        if data['RainCollector'] == RAIN_COLLECTOR_METRIC:
            self.correct_rain_values(data)

    def correct_rain_values(self, data: dict[str, Any]):
        data['RainDay'] *= 2/2.54
        data['RainMonth'] *= 2/2.54
        data['RainYear'] *= 2/2.54
        data['RainRate'] *= 2/2.54

    def get_link(self) -> str | None:
        if self._protocol == PROTOCOL_NETWORK:
            return f"tcp:{self._link}"
        if self._protocol == PROTOCOL_SERIAL:
            return f"serial:{self._link}:19200:8N1"
