"""Constants for the Davis Vantage integration."""

NAME = "Davis Vantage"
DOMAIN = "davis_vantage"
MANUFACTURER = "Davis"
VERSION = "1.2.0"

DEFAULT_SYNC_INTERVAL = 30  # seconds
DEFAULT_NAME = NAME

DATA_ARCHIVE_PERIOD = 'archive_period'

RAIN_COLLECTOR_IMPERIAL = '0.01"'
RAIN_COLLECTOR_METRIC = '0.2 mm'

PROTOCOL_NETWORK = 'Network'
PROTOCOL_SERIAL = 'Serial'

SERVICE_SET_DAVIS_TIME = 'set_davis_time'
SERVICE_GET_DAVIS_TIME = 'get_davis_time'
SERVICE_GET_RAW_DATA = 'get_raw_data'
SERVICE_GET_INFO = 'get_info'

MODEL_VANTAGE_PRO2 = 'Vantage Pro2'
MODEL_VANTAGE_PRO2PLUS = 'Vantage Pro2 Plus'
MODEL_VANTAGE_VUE = 'Vantage Vue'

CONFIG_RAIN_COLLECTOR = "rain_collector"
CONFIG_STATION_MODEL = "station_model"
CONFIG_INTERVAL = "interval"
CONFIG_PROTOCOL = "protocol"
CONFIG_LINK = "link"

KEY_TO_NAME = {
    "Datetime": "Last Fetch Time",
    "LastSuccessTime": "Last Success Time",
    "LastErrorTime": "Last Error Time",
    "LastError": "Last Error Message",
    "ArchiveInterval": "Archive Interval",
    "TempOut": "Temperature",
    "TempOutHiDay": "Temperature High (Day)",
    "TempOutHiTime": "Temperature High Time",
    "TempOutLowDay": "Temperature Low (Day)",
    "TempOutLowTime": "Temperature Low Time",
    "TempIn": "Temperature (Inside)",
    "HeatIndex": "Heat Index",
    "WindChill": "Wind Chill",
    "FeelsLike": "Feels Like",
    "DewPoint": "Dew Point",
    "DewPointHiDay": "Dew Point High (Day)",
    "DewPointHiTime": "Dew Point High Time",
    "DewPointLowDay": "Dew Point Low (Day)",
    "DewPointLowTime": "Dew Point Low Time",
    "Barometer": "Barometric Pressure",
    "BarometerHiDay": "Barometric Pressure High (Day)",
    "BarometerHiTime": "Barometric Pressure High Time",
    "BarometerLowDay": "Barometric Pressure Low (Day)",
    "BarometerLoTime": "Barometric Pressure Low Time",
    "BarTrend": "Barometric Trend",
    "HumIn": "Humidity (Inside)",
    "HumOut": "Humidity",
    "WindSpeed": "Wind Speed",
    "WindSpeed10Min": "Wind Speed (Average)",
    "WindGust": "Wind Gust",
    "WindGustDay": "Wind Gust (Day)",
    "WindGustTime": "Wind Gust Time",
    "WindDir": "Wind Direction",
    "WindDirRose": "Wind Direction Rose",
    "WindSpeedBft": "Wind Speed (Bft)",
    "RainDay": "Rain (Day)",
    "RainMonth": "Rain (Month)",
    "RainYear": "Rain (Year)",
    "RainRate": "Rain Rate",
    "RainRateDay": "Rain Rate (Day)",
    "RainRateTime": "Rain Rate Time",
    "UV": "UV Level",
    "UVDay": "UV Level (Day)",
    "UVTime": "UV Level Time",
    "SolarRad": "Solar Radiation",
    "SolarRadDay": "Solar Radiation (Day)",
    "SolarRadTime": "Solar Radiation Time",
    "BatteryVolts": "Battery Voltage",
    "ForecastIcon": "Forecast Icon",
    "ForecastRuleNo": "Forecast Rule",
    "RainCollector": "Rain Collector",
    "RainStorm": "Rain Storm",
    "StormStartDate": "Rain Storm Start Date",
    "ExtraTemps01": "Extra Temperature 1",
    "ExtraTemps02": "Extra Temperature 2",
    "ExtraTemps03": "Extra Temperature 3",
    "ExtraTemps04": "Extra Temperature 4",
    "ExtraTemps05": "Extra Temperature 5",
    "ExtraTemps06": "Extra Temperature 6",
    "ExtraTemps07": "Extra Temperature 7",
    "HumExtra01": "Extra Humidity 1",
    "HumExtra02": "Extra Humidity 2",
    "HumExtra03": "Extra Humidity 3",
    "HumExtra04": "Extra Humidity 4",
    "HumExtra05": "Extra Humidity 5",
    "HumExtra06": "Extra Humidity 6",
    "HumExtra07": "Extra Humidity 7",
    "IsRaining": "Is Raining"
}