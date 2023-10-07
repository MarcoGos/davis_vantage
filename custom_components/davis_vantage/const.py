"""Constants for the Davis Vantage integration."""

NAME = "Davis Vantage"
DOMAIN = "davis_vantage"
MANUFACTURER = "Davis"
MODEL = "Vantage Pro2/Vue"
VERSION = "1.0.4"

DEFAULT_SYNC_INTERVAL = 30  # seconds
DEFAULT_NAME = NAME

RAIN_COLLECTOR_IMPERIAL = '0.01"'
RAIN_COLLECTOR_METRIC = '0.2 mm'

PROTOCOL_NETWORK = 'Network'
PROTOCOL_SERIAL = 'Serial'

SERVICE_SET_DAVIS_TIME = 'set_davis_time'
SERVICE_GET_DAVIS_TIME = 'get_davis_time'
