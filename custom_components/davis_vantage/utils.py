import math
from datetime import datetime
import re
from zoneinfo import ZoneInfo
from typing import Any

def convert_to_celcius(value: float) -> float:
    return round((value - 32.0) * (5.0/9.0), 1)

def convert_celcius_to_fahrenheit(value_c: float) -> float:
    return round(value_c * 1.8 + 32, 1)

def convert_to_kmh(value: float) -> float:
    return round(value * 1.609344, 1)

def convert_to_ms(value: float) -> float:
    return convert_kmh_to_ms(convert_to_kmh(value))

def convert_to_mbar(value: float) -> float:
    return round(value * 33.8637526, 1)

def convert_to_mm(value: float) -> float:
    return round(value * 20.0, 1) # Use metric tipping bucket modification

def convert_kmh_to_ms(windspeed: float) -> float:
    return round(windspeed / 3.6, 1)

def convert_ms_to_bft(windspeed: float) -> int:
    if windspeed < 0.2:
        return 0
    elif windspeed < 1.6:
        return 1
    elif windspeed < 3.4:
        return 2
    elif windspeed < 5.5:
        return 3
    elif windspeed < 8.0:
        return 4
    elif windspeed < 10.8:
        return 5
    elif windspeed < 13.9: 
        return 6
    elif windspeed < 17.2:
        return 7
    elif windspeed < 20.8:
        return 8
    elif windspeed < 24.5:
        return 9
    elif windspeed < 28.5:
        return 10
    elif windspeed < 32.7:
        return 11
    else:
        return 12

def convert_kmh_to_bft(windspeed_kmh: float) -> int:
    return convert_ms_to_bft(convert_kmh_to_ms(windspeed_kmh))

def contains_correct_raw_data(raw_data: dict[str, Any]) -> None:
    return raw_data['TempOut'] != 32767 \
        and raw_data['RainRate'] != 32767 \
        and raw_data['WindSpeed'] != 255 \
        and raw_data['HumOut'] != 255 \
        and raw_data['WindSpeed10Min'] != 255

def calc_heat_index(temperature_f: float, humidity: float) -> float:
    if temperature_f < 80.0 or humidity < 40.0:
        return temperature_f
    else:
        heat_index_f: float = \
            -42.379 \
            + (2.04901523 * temperature_f) \
            + (10.14333127 * humidity) \
            - (0.22475541 * temperature_f * humidity) \
            - (0.00683783 * pow(temperature_f, 2)) \
            - (0.05481717 * pow(humidity, 2)) \
            + (0.00122874 * pow(temperature_f, 2) * humidity) \
            + (0.00085282 * temperature_f * pow(humidity, 2)) \
            - (0.00000199 * pow(temperature_f, 2) * pow(humidity, 2))
    return max(heat_index_f, temperature_f)

def calc_wind_chill(temperature_f: float, windspeed: float) -> float:
    if windspeed == 0:
        wind_chill_f = temperature_f
    else:
        wind_chill_f = \
            35.74 \
            + (0.6215 * temperature_f) \
            - (35.75 * pow(windspeed,0.16)) \
            + (0.4275 * temperature_f * pow(windspeed, 0.16))
    return min(wind_chill_f, temperature_f)

def calc_feels_like(temperature_f: float, humidity: float, windspeed_mph: float) -> float:
    if windspeed_mph == 0:
        windspeed_mph = 1
    feels_like_f = temperature_f
    if temperature_f <= 50 and humidity >= 3:
        feels_like_f = \
            35.74 \
            + (0.6215 * temperature_f) \
            - (35.75 * pow(windspeed_mph, 0.16)) \
            + (0.4275 * temperature_f * pow(windspeed_mph, 0.16))

    if feels_like_f == temperature_f and temperature_f >= 80:
        feels_like_f = \
            0.5 * (temperature_f + 61 + ((temperature_f - 68) * 1.2) \
            + (humidity * 0.094) )

    if feels_like_f >= 80:
        feels_like_f = \
            -42.379 \
            + (2.04901523 * temperature_f) \
            + (10.14333127 * humidity) \
            - (0.22475541 * temperature_f * humidity) \
            - (0.00683783 * pow(temperature_f, 2)) \
            - (0.05481717 * pow(humidity, 2)) \
            + (0.00122874 * pow(temperature_f, 2) * humidity) \
            + (0.00085282 * temperature_f * pow(humidity, 2)) \
            - (0.00000199 * pow(temperature_f, 2) * pow(humidity, 2))

    if humidity < 13 and temperature_f >= 80 and temperature_f <= 112:
        feels_like_f = feels_like_f - ((13 - humidity) / 4) * math.sqrt((17 - math.fabs(temperature_f - 95.0)) / 17)

    if humidity > 85 and temperature_f >= 80 and temperature_f <= 87:
        feels_like_f = feels_like_f + ((humidity - 85) / 10) * ((87 - temperature_f) / 5)
    return feels_like_f

def convert_to_iso_datetime(value: datetime, tzinfo: ZoneInfo) -> datetime:
    return value.replace(tzinfo=tzinfo)

def get_wind_rose(bearing: int) -> str:
    directions = [ 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw' ]
    index = round(bearing / 45) % 8
    return directions[index]

def has_correct_value(value: float) -> bool:
    return value != 255 and value != 32767

def round_to_one_decimal(value: float) -> float:
    return round(value, 1)

def get_baro_trend(trend: int) -> str | None:
    if trend in [-60,196]:
        return "falling_rapidly"
    elif trend in [-20,236]:
        return "falling_slowly"
    elif trend == 0:
        return "steady"
    elif trend == 20:
        return "rising_slowly"
    elif trend == 60:
        return "rising_rapidly"
    else:
        return None

def get_uv(value: int) -> float:
    return round(value, 1)

def get_solar_rad(value: int) -> float:
    return value

def calc_dew_point(temperature_f: float, humidity: float) -> float:
    temperature_c = convert_to_celcius(temperature_f)
    a = math.log(humidity / 100) + (17.62 * temperature_c / (243.12 + temperature_c))
    return convert_celcius_to_fahrenheit(243.12 * a / (17.62 - a))

def make_safe_entity_id(entity_id: str) -> str:
    return re.sub(r"[()]", "", entity_id).replace(" ", "_").lower()
