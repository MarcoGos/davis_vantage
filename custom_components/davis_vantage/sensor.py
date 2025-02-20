import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription
)
from homeassistant.components.sensor.const import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    DEGREE,
    UnitOfSpeed,
    UnitOfLength,
    UnitOfVolumetricFlux,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfIrradiance,
    UnitOfTime,
    EntityCategory
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    RAIN_COLLECTOR_IMPERIAL,
    RAIN_COLLECTOR_METRIC,
    RAIN_COLLECTOR_METRIC_0_1,
    CONFIG_STATION_MODEL,
    MODEL_VANTAGE_PRO2PLUS,
    KEY_TO_NAME
)
from .coordinator import DavisVantageDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

def get_sensor_descriptions(model: str) -> list[SensorEntityDescription]:
    descriptions: list[SensorEntityDescription] = [
        SensorEntityDescription(
            key="Datetime",
            translation_key="last_fetch_time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        SensorEntityDescription(
            key="LastSuccessTime",
            translation_key="last_success_time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        SensorEntityDescription(
            key="LastErrorTime",
            translation_key="last_error_time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastError",
            translation_key="last_error_message",
            icon="mdi:message-alert-outline",
            entity_category=EntityCategory.DIAGNOSTIC
        ),
        SensorEntityDescription(
            key="ArchiveInterval",
            translation_key="archive_interval",
            icon="mdi:archive-clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=UnitOfTime.MINUTES
        ),
        SensorEntityDescription(
            key="TempOut",
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="TempOutHiDay",
            translation_key="temperature_high_day",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-up"
        ),
        SensorEntityDescription(
            key="TempOutHiTime",
            translation_key="temperature_high_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="TempOutLowDay",
            translation_key="temperature_low_day",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-down"
        ),
        SensorEntityDescription(
            key="TempOutLowTime",
            translation_key="temperature_low_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="TempIn",
            translation_key="temperature_inside",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HeatIndex",
            translation_key="heat_index",
            icon="mdi:sun-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindChill",
            translation_key="wind_chill",
            icon="mdi:snowflake-thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="FeelsLike",
            translation_key="feels_like",
            icon="mdi:download-circle-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPoint",
            translation_key="dew_point",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointHiDay",
            translation_key="dew_point_high_day",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointHiTime",
            translation_key="dew_point_high_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="DewPointLowDay",
            translation_key="dew_point_low_day",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointLowTime",
            translation_key="dew_point_low_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="Barometer",
            translation_key="barometric_pressure",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerHiDay",
            translation_key="barometric_pressure_high_day",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerHiTime",
            translation_key="barometric_pressure_high_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="BarometerLowDay",
            translation_key="barometric_pressure_low_day",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerLoTime",
            translation_key="barometric_pressure_low_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="BarTrend",
            translation_key="barometric_trend",
            device_class=SensorDeviceClass.ENUM,
            options=[
                "falling_rapidly",
                "falling_slowly",
                "steady",
                "rising_slowly",
                "rising_rapidly"
            ]
        ),
        SensorEntityDescription(
            key="HumIn",
            translation_key="humidity_inside",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumOut",
            translation_key="humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class="measurement",
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0
        ),
        SensorEntityDescription(
            key="WindSpeed",
            translation_key="wind_speed",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindSpeed10Min",
            translation_key="wind_speed_average",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGust",
            translation_key="wind_gust",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGustDay",
            translation_key="wind_gust_day",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGustTime",
            translation_key="wind_gust_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="WindDir",
            translation_key="wind_direction",
            icon="mdi:compass-outline",
            state_class="measurement",
            native_unit_of_measurement=DEGREE,
            suggested_display_precision=0
        ),
        SensorEntityDescription(
            key="WindDirRose",
            translation_key="wind_direction_rose",
            device_class=SensorDeviceClass.ENUM,
            options=[
                "n",
                "ne",
                "e",
                "se",
                "s",
                "sw",
                "w",
                "nw"
            ]
        ),
        SensorEntityDescription(
            key="WindSpeedBft",
            translation_key="wind_speed_bft",
            icon="mdi:weather-windy",
            state_class="measurement",
        ),
        SensorEntityDescription(
            key="RainDay",
            translation_key="rain_day",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class="measurement",
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainMonth",
            translation_key="rain_month",
            icon="mdi:water-outline",
            state_class="measurement",
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainYear",
            translation_key="rain_year",
            icon="mdi:water-outline",
            state_class="measurement",
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainRate",
            translation_key="rain_rate",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class="measurement",
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainRateDay",
            translation_key="rain_rate_day",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class="measurement",
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainRateTime",
            translation_key="rain_rate_time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="UV",
            translation_key="uv_level",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="UVDay",
            translation_key="uv_level_day",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="UVTime",
            translation_key="uv_level_time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="SolarRad",
            translation_key="solar_radiation",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER
        ),
        SensorEntityDescription(
            key="SolarRadDay",
            translation_key="solar_radiation_day",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER
        ),
        SensorEntityDescription(
            key="SolarRadTime",
            translation_key="solar_radiation_time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="BatteryVolts",
            translation_key="battery_voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            entity_category=EntityCategory.DIAGNOSTIC,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ForecastIcon",
            translation_key="forecast_icon",
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ForecastRuleNo",
            translation_key="forecast_rule",
            icon="mdi:binoculars"
        ),
        SensorEntityDescription(
            key="RainCollector",
            translation_key="rain_collector",
            icon="mdi:bucket-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.ENUM,
            options=[
                RAIN_COLLECTOR_IMPERIAL,
                RAIN_COLLECTOR_METRIC,
                RAIN_COLLECTOR_METRIC_0_1
            ]
        ),
        SensorEntityDescription(
            key="RainStorm",
            translation_key="rain_storm",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class="measurement",
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="StormStartDate",
            translation_key="rain_storm_start_date",
            icon="mdi:calendar-outline",
            device_class=SensorDeviceClass.DATE
        ),
        SensorEntityDescription(
            key="ExtraTemps01",
            translation_key="extra_temperature_1",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps02",
            translation_key="extra_temperature_2",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps03",
            translation_key="extra_temperature_3",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps04",
            translation_key="extra_temperature_4",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps05",
            translation_key="extra_temperature_5",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps06",
            translation_key="extra_temperature_6",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps07",
            translation_key="extra_temperature_7",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="HumExtra01",
            translation_key="extra_humidity_1",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra02",
            translation_key="extra_humidity_2",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra03",
            translation_key="extra_humidity_3",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra04",
            translation_key="extra_humidity_4",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra05",
            translation_key="extra_humidity_5",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra06",
            translation_key="extra_humidity_6",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra07",
            translation_key="extra_humidity_7",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="Latitude",
            translation_key="latitude",
            icon="mdi:latitude",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=DEGREE,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="Longitude",
            translation_key="longitude",
            icon="mdi:longitude",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=DEGREE,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="Elevation",
            translation_key="elevation",
            device_class=SensorDeviceClass.DISTANCE,
            icon="mdi:image-filter-hdr-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=UnitOfLength.FEET,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastReadoutDuration",
            translation_key="last_readout_duration",
            icon="mdi:timer-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="SunRise",
            translation_key="sunrise",
            icon="mdi:sun-clock-outline",
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="SunSet",
            translation_key="sunset",
            icon="mdi:sun-clock-outline",
            entity_registry_enabled_default=False
        )
    ]
    return descriptions

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Davis Vantage sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[DavisVantageSensor] = []
    model = entry.data.get(CONFIG_STATION_MODEL, '')

    # Add all meter sensors described above.
    for description in get_sensor_descriptions(model):
        entities.append(
            DavisVantageSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                description=description,
            )
        )

    async_add_entities(entities)


class DavisVantageSensor(CoordinatorEntity[DavisVantageDataUpdateCoordinator], SensorEntity):
    """Defines a Davis Vantage sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DavisVantageDataUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize Davis Vantage sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME} {KEY_TO_NAME[description.key]}".lower()
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {KEY_TO_NAME[description.key]}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType: # type: ignore
        """Return the state of the sensor."""
        key = self.entity_description.key
        data = self.coordinator.data # type: ignore
        if key not in data:
            return None
        if self.entity_description.native_unit_of_measurement is not None:
            default_value = 0
        else:
            default_value = '-'
        return data.get(key, default_value) # type: ignore
