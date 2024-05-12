"""Constants for the Davis Vantage integration."""

NAME = "Davis Vantage"
DOMAIN = "davis_vantage"
MANUFACTURER = "Davis"
VERSION = "1.1.0"

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
