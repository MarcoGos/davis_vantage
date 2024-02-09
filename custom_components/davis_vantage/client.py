"""All client function"""
from typing import Any
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import logging
import asyncio
import struct
import re
from pyvantagepro import VantagePro2
from pyvantagepro.parser import HighLowParserRevB, LoopDataParserRevB, DataParser
from pyvantagepro.utils import ListDict
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
from .const import RAIN_COLLECTOR_IMPERIAL, PROTOCOL_NETWORK

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DavisVantageClient:
    """Davis Vantage Client class"""

    _vantagepro2: VantagePro2 = None

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
        self._last_raw_data: DataParser = {}  # type: ignore

    def get_vantagepro2fromurl(self, url: str) -> VantagePro2 | None:
        try:
            vp = VantagePro2.from_url(url)
            vp.link.close()
            return vp
        except Exception as e:
            raise e

    async def async_get_vantagepro2fromurl(self, url: str) -> VantagePro2 | None:
        _LOGGER.debug("async_get_vantagepro2fromurl with url=%s", url)
        vp = None
        try:
            loop = asyncio.get_event_loop()
            vp = await loop.run_in_executor(None, self.get_vantagepro2fromurl, url)
        except Exception as e:
            _LOGGER.error("Error on opening device from url: %s: %s", url, e)
        return vp

    async def connect_to_station(self):
        self._vantagepro2 = await self.async_get_vantagepro2fromurl(self.get_link())

    def get_current_data(
        self,
    ) -> tuple[LoopDataParserRevB | None, ListDict | None, HighLowParserRevB | None]:
        """Get current date from weather station."""
        data = None
        archives = None
        hilows = None

        try:
            self._vantagepro2.link.open()
            data = self._vantagepro2.get_current_data()
        except Exception as e:
            self._vantagepro2.link.close()
            raise e

        try:
            hilows = self._vantagepro2.get_hilows()
        except Exception:
            pass

        try:
            end_datetime = datetime.now()
            start_datetime = end_datetime - timedelta(minutes=(self._vantagepro2.archive_period * 2))  # type: ignore
            archives = self._vantagepro2.get_archives(start_datetime, end_datetime)
        except Exception:
            pass
        finally:
            self._vantagepro2.link.close()

        return data, archives, hilows

    async def async_get_current_data(self) -> LoopDataParserRevB | None:
        """Get current date from weather station async."""
        data = self._last_data
        now = convert_to_iso_datetime(
            datetime.now(), ZoneInfo(self._hass.config.time_zone)
        )
        try:
            loop = asyncio.get_event_loop()
            new_data, archives, hilows = await loop.run_in_executor(
                None, self.get_current_data
            )
            if new_data:
                new_raw_data = self.__get_full_raw_data(new_data)
                self._last_raw_data = new_raw_data
                self.remove_all_incorrect_data(new_raw_data, new_data)
                self.add_additional_info(new_data)
                self.convert_values(new_data)
                if archives:
                    self.add_wind_gust(archives, new_data)
                if hilows:
                    new_raw_hilows = self.__get_full_raw_data_hilows(hilows)
                    self.remove_all_incorrect_hilows(new_raw_hilows, hilows)
                    self.add_hilows(hilows, new_data)
                data = new_data
                data["Datetime"] = now
                if contains_correct_raw_data(new_raw_data):
                    data["LastError"] = ""
                    data["LastSuccessTime"] = now
                else:
                    data["LastError"] = "Received partly incorrect data"
            else:
                data["LastError"] = "Couldn't acquire data, no data received"

        except Exception as e:
            _LOGGER.warning(f"Couldn't acquire data from {self.get_link()}: {e}")
            data["LastError"] = f"Couldn't acquire data: {e}"

        if data["LastError"]:
            data["LastErrorTime"] = now

        self._last_data = data
        return data

    def __get_full_raw_data(self, data: LoopDataParserRevB) -> DataParser:
        raw_data = DataParser(data.raw_bytes, LoopDataParserRevB.LOOP_FORMAT)
        raw_data["HumExtra"] = struct.unpack(b"7B", raw_data["HumExtra"])  # type: ignore
        raw_data["ExtraTemps"] = struct.unpack(b"7B", raw_data["ExtraTemps"])  # type: ignore
        raw_data["SoilMoist"] = struct.unpack(b"4B", raw_data["SoilMoist"])  # type: ignore
        raw_data["SoilTemps"] = struct.unpack(b"4B", raw_data["SoilTemps"])  # type: ignore
        raw_data["LeafWetness"] = struct.unpack(b"4B", raw_data["LeafWetness"])  # type: ignore
        raw_data["LeafTemps"] = struct.unpack(b"4B", raw_data["LeafTemps"])  # type: ignore
        raw_data.tuple_to_dict("ExtraTemps")
        raw_data.tuple_to_dict("LeafTemps")
        raw_data.tuple_to_dict("SoilTemps")
        raw_data.tuple_to_dict("HumExtra")
        raw_data.tuple_to_dict("LeafWetness")
        raw_data.tuple_to_dict("SoilMoist")
        return raw_data

    def __get_full_raw_data_hilows(self, data: HighLowParserRevB) -> DataParser:
        raw_data = DataParser(data.raw_bytes, HighLowParserRevB.HILOWS_FORMAT)
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

    def get_info(self) -> dict[str, Any] | None:
        try:
            self._vantagepro2.link.open()
            firmware_version = self._vantagepro2.firmware_version  # type: ignore
            firmware_date = self._vantagepro2.firmware_date  # type: ignore
            diagnostics = self._vantagepro2.diagnostics  # type: ignore
        except Exception as e:
            raise e
        finally:
            self._vantagepro2.link.close()
        return {
            "version": firmware_version,
            "date": firmware_date,
            "diagnostics": diagnostics,
        }

    async def async_get_info(self) -> dict[str, Any] | None:
        info = None
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self.get_info)
        except Exception as e:
            _LOGGER.error("Couldn't get firmware info: %s", e)
        return info

    def add_additional_info(self, data: dict[str, Any]) -> None:
        if data["TempOut"] is not None:
            if data["HumOut"] is not None:
                data["HeatIndex"] = calc_heat_index(data["TempOut"], data["HumOut"])
                data["DewPoint"] = calc_dew_point(data["TempOut"], data["HumOut"])
            if data["WindSpeed"] is not None:
                data["WindChill"] = calc_wind_chill(data["TempOut"], data["WindSpeed"])
                if data["HumOut"] is not None:
                    data["FeelsLike"] = calc_feels_like(
                        data["TempOut"], data["HumOut"], data["WindSpeed"]
                    )
        if data["WindDir"] is not None:
            data["WindDirRose"] = get_wind_rose(data["WindDir"], self._windrose8)
        if data["WindSpeed10Min"] is not None:
            data["WindSpeedBft"] = convert_kmh_to_bft(
                convert_to_kmh(data["WindSpeed10Min"])
            )
        if data["RainRate"] is not None:
            data["IsRaining"] = data["RainRate"] > 0
        data["ArchiveInterval"] = self._vantagepro2.archive_period

    def convert_values(self, data: dict[str, Any]) -> None:
        del data["Datetime"]
        if data["BarTrend"] is not None:
            data["BarTrend"] = get_baro_trend(data["BarTrend"])
        if data["UV"] is not None:
            data["UV"] = get_uv(data["UV"])
        if data["SolarRad"] is not None:
            data["SolarRad"] = get_solar_rad(data["SolarRad"])
        if data["ForecastRuleNo"] is not None:
            data["ForecastRuleNo"] = get_forecast_string(data["ForecastRuleNo"])
        data["RainCollector"] = self._rain_collector
        data["WindRoseSetup"] = 8 if self._windrose8 else 16
        if data["RainCollector"] != RAIN_COLLECTOR_IMPERIAL:
            self.correct_rain_values(data)

    def correct_rain_values(self, data: dict[str, Any]):
        if data["RainDay"] is not None:
            data["RainDay"] *= 2 / 2.54
        if data["RainMonth"] is not None:
            data["RainMonth"] *= 2 / 2.54
        if data["RainYear"] is not None:
            data["RainYear"] *= 2 / 2.54
        if data["RainRate"] is not None:
            data["RainRate"] *= 2 / 2.54
        if data["RainStorm"] is not None:
            data["RainStorm"] *= 2 / 2.54
        if "RainRateDay" in data:
            if data["RainRateDay"] is not None:
                data["RainRateDay"] *= 2 / 2.54

    def remove_all_incorrect_data(self, raw_data: DataParser, data: LoopDataParserRevB):
        data_info = {key: value for key, value in LoopDataParserRevB.LOOP_FORMAT}
        self.remove_incorrect_data(raw_data, data_info, data)

    def remove_all_incorrect_hilows(
        self, raw_data: DataParser, data: HighLowParserRevB
    ):
        data_info = {key: value for key, value in HighLowParserRevB.HILOWS_FORMAT}
        self.remove_incorrect_data(raw_data, data_info, data)

    def remove_incorrect_data(
        self, raw_data: DataParser, data_info: dict[str, str], data: dict[str, Any]
    ):
        for key in data.keys():  # type: ignore
            info_key = re.sub(r"\d+$", "", key)  # type: ignore
            data_type = data_info.get(info_key, "")
            raw_value = raw_data.get(info_key, 0)
            if self.is_incorrect_value(raw_value, data_type):
                data[key] = None  # type: ignore

    def is_incorrect_value(self, raw_value: int, data_type: str) -> bool:
        if (
            ((data_type in ["B", "7s"]) and (raw_value == 255))
            or ((data_type == "H") and (raw_value == 65535))
            or ((data_type == "h") and (abs(raw_value) == 32767))
        ):
            return True
        else:
            return False

    def add_wind_gust(self, archives: ListDict | None, data: dict[str, Any]):
        if not archives:
            return
        data["WindGust"] = archives[-1]["WindHi"]

    def add_hilows(self, hilows: HighLowParserRevB | None, data: dict[str, Any]):
        if not hilows:
            return
        data["TempOutHiDay"] = hilows["TempHiDay"]
        data["TempOutHiTime"] = self.strtotime(hilows["TempHiTime"])
        data["TempOutLowDay"] = hilows["TempLoDay"]
        data["TempOutLowTime"] = self.strtotime(hilows["TempLoTime"])

        data["DewPointHiDay"] = hilows["DewHiDay"]
        data["DewPointHiTime"] = self.strtotime(hilows["DewHiTime"])
        data["DewPointLowDay"] = hilows["DewLoDay"]
        data["DewPointLowTime"] = self.strtotime(hilows["DewLoTime"])

        data["RainRateDay"] = hilows["RainHiDay"]
        data["RainRateTime"] = self.strtotime(hilows["RainHiTime"])

        data["BarometerHiDay"] = hilows["BaroHiDay"]
        data["BarometerHiTime"] = self.strtotime(hilows["BaroHiTime"])
        data["BarometerLowDay"] = hilows["BaroLoDay"]
        data["BarometerLoTime"] = self.strtotime(hilows["BaroLoTime"])

        data["SolarRadDay"] = hilows["SolarHiDay"]
        data["SolarRadTime"] = self.strtotime(hilows["SolarHiTime"])

        data["UVDay"] = hilows["UVHiDay"]
        data["UVTime"] = self.strtotime(hilows["UVHiTime"])

        data["WindGustDay"] = hilows["WindHiDay"]
        data["WindGustTime"] = self.strtotime(hilows["WindHiTime"])

    def get_link(self) -> str | None:
        """Get device link for use with vproweather."""
        if self._protocol == PROTOCOL_NETWORK:
            return f"tcp:{self._link}"
        return f"serial:{self._link}:19200:8N1"

    def get_raw_data(self) -> DataParser:
        return self._last_raw_data

    def strtotime(self, time_str: str | None) -> time | None:
        if time_str is None:
            return None
        else:
            return datetime.strptime(time_str, "%H:%M").time()
