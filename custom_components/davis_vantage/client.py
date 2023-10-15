"""All client function"""
from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import asyncio
import struct
import re
from pyvantagepro import VantagePro2
from pyvantagepro.parser import LoopDataParserRevB, DataParser
from homeassistant.core import HomeAssistant

from .utils import (
    calc_dew_point,
    calc_feels_like,
    calc_wind_chill,
    contains_correct_raw_data,
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
        self._last_data: LoopDataParserRevB = {} # type: ignore
        self._last_raw_data: DataParser = {}
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
            new_raw_data = self.__get_full_raw_data(new_data)
            now = convert_to_iso_datetime(datetime.now(), ZoneInfo(self._hass.config.time_zone))
            if new_data:
                self.remove_all_incorrect_data(new_raw_data, new_data)
                self.add_additional_info(new_data)
                self.convert_values(new_data)
                data = new_data
                data['Datetime'] = now
                if contains_correct_raw_data(new_raw_data):
                    data['LastError'] = ""
                    data['LastSuccessTime'] = now
                else:
                    data['LastError'] = "Received partly incorrect data"
            else:
                data["LastError"] = "Couldn't acquire data, no data received"
        except Exception as e:
            _LOGGER.warning(f"Couldn't acquire data from {self.get_link()}")
            data['LastError'] = f"Couldn't acquire data: {e}"

        if data['LastError']:
            data['LastErrorTime'] = now

        self._last_data = data
        self._last_raw_data = new_raw_data
        return data

    def __get_full_raw_data(self, data: LoopDataParserRevB) -> DataParser:
        raw_data = DataParser(data.raw_bytes, LoopDataParserRevB.LOOP_FORMAT)
        raw_data['HumExtra'] = struct.unpack(b'7B', raw_data['HumExtra'])
        raw_data['ExtraTemps'] = struct.unpack(b'7B', raw_data['ExtraTemps'])
        raw_data['SoilMoist'] = struct.unpack(b'4B', raw_data['SoilMoist'])
        raw_data['SoilTemps'] = struct.unpack(b'4B', raw_data['SoilTemps'])
        raw_data['LeafWetness'] = struct.unpack(b'4B', raw_data['LeafWetness'])
        raw_data['LeafTemps'] = struct.unpack(b'4B', raw_data['LeafTemps'])
        raw_data.tuple_to_dict("ExtraTemps")
        raw_data.tuple_to_dict("LeafTemps")
        raw_data.tuple_to_dict("SoilTemps")
        raw_data.tuple_to_dict("HumExtra")
        raw_data.tuple_to_dict("LeafWetness")
        raw_data.tuple_to_dict("SoilMoist")
        return raw_data

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
        if data['TempOut'] and data['HumOut']:
            data['HeatIndex'] = calc_heat_index(data['TempOut'], data['HumOut'])
        if data['TempOut'] and data['WindSpeed']:
            data['WindChill'] = calc_wind_chill(data['TempOut'], data['WindSpeed'])
        if data['TempOut'] and data['HumOut'] and data['WindSpeed']:
            data['FeelsLike'] = calc_feels_like(data['TempOut'], data['HumOut'], data['WindSpeed'])
        if data['WindDir']:
            data['WindDirRose'] = get_wind_rose(data['WindDir'], self._windrose8)
        if data['TempOut'] and data['HumOut']:
            data['DewPoint'] = calc_dew_point(data['TempOut'], data['HumOut'])
        if data['WindSpeed10Min']:
            data['WindSpeedBft'] = convert_kmh_to_bft(convert_to_kmh(data['WindSpeed10Min']))
        if data['RainRate']:
            data['IsRaining'] = data['RainRate'] > 0

    def convert_values(self, data: dict[str, Any]) -> None:
        del data['Datetime']
        if data['BarTrend']:
            data['BarTrend'] = get_baro_trend(data['BarTrend'])
        if data['UV']:
            data['UV'] = get_uv(data['UV'])
        if data['SolarRad']:
            data['SolarRad'] = get_solar_rad(data['SolarRad'])
        if data['ForecastRuleNo']:
            data['ForecastRuleNo'] = get_forecast_string(data['ForecastRuleNo'])
        data['RainCollector'] = self._rain_collector
        data['WindRoseSetup'] = 8 if self._windrose8 else 16
        if data['RainCollector'] == RAIN_COLLECTOR_METRIC:
            self.correct_rain_values(data)

    def correct_rain_values(self, data: dict[str, Any]):
        if data['RainDay']:
            data['RainDay'] *= 2/2.54
        if data['RainMonth']:
            data['RainMonth'] *= 2/2.54
        if data['RainYear']:
            data['RainYear'] *= 2/2.54
        if data['RainRate']:
            data['RainRate'] *= 2/2.54

    def remove_all_incorrect_data(self, raw_data: DataParser, data: LoopDataParserRevB):
        data_info = { key: value for key, value in LoopDataParserRevB.LOOP_FORMAT }
        for key in data.keys():
            info_key = re.sub(r'\d+$', '', key)
            if data_info.get(info_key, '') in ["B", "7s"]:
                if raw_data.get(key, 0) == 255:
                    data[key] = None
            if data_info.get(key, '') == 'H':
                if raw_data.get(key, '') == 32767 or raw_data.get(key, '') == 65535:
                    data[key] = None

    def get_link(self) -> str | None:
        """Get device link for use with vproweather."""
        if self._protocol == PROTOCOL_NETWORK:
            return f"tcp:{self._link}"
        return f"serial:{self._link}:19200:8N1"

    def get_raw_data(self) -> DataParser:
        return self._last_raw_data
