"""Sensor setup for our Integration."""

import logging
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription
)
from homeassistant.components.sensor.const import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorStateClass
)

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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DavisConfigEntry
from .const import (
    DEFAULT_NAME,
    RAIN_COLLECTOR_IMPERIAL,
    RAIN_COLLECTOR_METRIC,
    RAIN_COLLECTOR_METRIC_0_1,
    CONFIG_STATION_MODEL,
    MODEL_VANTAGE_PRO2PLUS,
)
from .coordinator import DavisVantageDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

@dataclass(kw_only=True, frozen=True)
class DavisSensorEntityDescription(SensorEntityDescription):
    """Describes Davis sensor entity."""
    entity_name: str | None = None


def get_sensor_descriptions(model: str) -> list[DavisSensorEntityDescription]:
    """Return the sensor descriptions for the specified model."""
    return [
        DavisSensorEntityDescription(
            key="Datetime",
            translation_key="last_fetch_time",
            entity_name="Last Fetch Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        DavisSensorEntityDescription(
            key="LastSuccessTime",
            translation_key="last_success_time",
            entity_name="Last Success Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        DavisSensorEntityDescription(
            key="LastErrorTime",
            translation_key="last_error_time",
            entity_name="Last Error Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="LastError",
            translation_key="last_error_message",
            entity_name="Last Error Message",
            icon="mdi:message-alert-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        DavisSensorEntityDescription(
            key="ArchiveInterval",
            translation_key="archive_interval",
            entity_name="Archive Interval",
            icon="mdi:archive-clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=UnitOfTime.MINUTES,
        ),
        DavisSensorEntityDescription(
            key="TempOut",
            translation_key="temperature",
            entity_name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="TempOutHiDay",
            translation_key="temperature_high_day",
            entity_name="Temperature High (Day)",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-up",
        ),
        DavisSensorEntityDescription(
            key="TempOutHiTime",
            translation_key="temperature_high_time",
            entity_name="Temperature High Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="TempOutLowDay",
            translation_key="temperature_low_day",
            entity_name="Temperature Low (Day)",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-down",
        ),
        DavisSensorEntityDescription(
            key="TempOutLowTime",
            translation_key="temperature_low_time",
            entity_name="Temperature Low Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="TempIn",
            translation_key="temperature_inside",
            entity_name="Temperature (Inside)",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="HeatIndex",
            translation_key="heat_index",
            entity_name="Heat Index",
            icon="mdi:sun-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="WindChill",
            translation_key="wind_chill",
            entity_name="Wind Chill",
            icon="mdi:snowflake-thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="FeelsLike",
            translation_key="feels_like",
            entity_name="Feels Like",
            icon="mdi:download-circle-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="DewPoint",
            translation_key="dew_point",
            entity_name="Dew Point",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="DewPointHiDay",
            translation_key="dew_point_high_day",
            entity_name="Dew Point High (Day)",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="DewPointHiTime",
            translation_key="dew_point_high_time",
            entity_name="Dew Point High Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="DewPointLowDay",
            translation_key="dew_point_low_day",
            entity_name="Dew Point Low (Day)",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="DewPointLowTime",
            translation_key="dew_point_low_time",
            entity_name="Dew Point Low Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="Barometer",
            translation_key="barometric_pressure",
            entity_name="Barometric Pressure",
            device_class=SensorDeviceClass.PRESSURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="BarometerHiDay",
            translation_key="barometric_pressure_high_day",
            entity_name="Barometric Pressure High (Day)",
            device_class=SensorDeviceClass.PRESSURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="BarometerHiTime",
            translation_key="barometric_pressure_high_time",
            entity_name="Barometric Pressure High Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="BarometerLowDay",
            translation_key="barometric_pressure_low_day",
            entity_name="Barometric Pressure Low (Day)",
            device_class=SensorDeviceClass.PRESSURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="BarometerLoTime",
            translation_key="barometric_pressure_low_time",
            entity_name="Barometric Pressure Low Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="BarTrend",
            translation_key="barometric_trend",
            entity_name="Barometric Trend",
            device_class=SensorDeviceClass.ENUM,
            options=[
                "falling_rapidly",
                "falling_slowly",
                "steady",
                "rising_slowly",
                "rising_rapidly"
            ],
        ),
        DavisSensorEntityDescription(
            key="HumIn",
            translation_key="humidity_inside",
            entity_name="Humidity (Inside)",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="HumOut",
            translation_key="humidity",
            entity_name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
        ),
        DavisSensorEntityDescription(
            key="WindSpeed",
            translation_key="wind_speed",
            entity_name="Wind Speed",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="WindSpeed10Min",
            translation_key="wind_speed_average_10min",
            entity_name="Wind Speed (Average)",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="WindSpeedAvg",
            translation_key="wind_speed_average",
            entity_name="Wind Speed (Average) (AI)",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="WindGust",
            translation_key="wind_gust",
            entity_name="Wind Gust",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="WindGustDay",
            translation_key="wind_gust_day",
            entity_name="Wind Gust (Day)",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="WindGustTime",
            translation_key="wind_gust_time",
            entity_name="Wind Gust Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="WindDir",
            translation_key="wind_direction",
            entity_name="Wind Direction",
            icon="mdi:compass-outline",
            device_class=SensorDeviceClass.WIND_DIRECTION,
            state_class=SensorStateClass.MEASUREMENT_ANGLE,
            native_unit_of_measurement=DEGREE,
            suggested_display_precision=0,
        ),
        DavisSensorEntityDescription(
            key="WindAvgDir",
            translation_key="wind_direction_average",
            entity_name="Wind Direction (Average)",
            icon="mdi:compass-outline",
            device_class=SensorDeviceClass.WIND_DIRECTION,
            state_class=SensorStateClass.MEASUREMENT_ANGLE,
            native_unit_of_measurement=DEGREE,
            suggested_display_precision=0,
        ),
        DavisSensorEntityDescription(
            key="WindDirRose",
            translation_key="wind_direction_rose",
            entity_name="Wind Direction Rose",
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
            ],
        ),
        DavisSensorEntityDescription(
            key="WindAvgDirRose",
            translation_key="wind_direction_rose_average",
            entity_name="Wind Direction Rose (Average)",
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
            ],
        ),
        DavisSensorEntityDescription(
            key="WindSpeedBft",
            translation_key="wind_speed_bft",
            entity_name="Wind Speed (Bft)",
            icon="mdi:weather-windy",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.ENUM,
        ),
        DavisSensorEntityDescription(
            key="RainDay",
            translation_key="rain_day",
            entity_name="Rain (Day)",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="RainMonth",
            translation_key="rain_month",
            entity_name="Rain (Month)",
            icon="mdi:water-outline",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="RainYear",
            translation_key="rain_year",
            entity_name="Rain (Year)",
            icon="mdi:water-outline",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="RainRate",
            translation_key="rain_rate",
            entity_name="Rain Rate",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="RainRateDay",
            translation_key="rain_rate_day",
            entity_name="Rain Rate (Day)",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=2,
        ),
        DavisSensorEntityDescription(
            key="RainRateTime",
            translation_key="rain_rate_time",
            entity_name="Rain Rate Time",
            icon="mdi:clock-in",
        ),
        DavisSensorEntityDescription(
            key="UV",
            translation_key="uv_level",
            entity_name="UV Level",
            icon="mdi:sun-wireless-outline",
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
        ),
        DavisSensorEntityDescription(
            key="UVDay",
            translation_key="uv_level_day",
            entity_name="UV Level (Day)",
            icon="mdi:sun-wireless-outline",
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
        ),
        DavisSensorEntityDescription(
            key="UVTime",
            translation_key="uv_level_time",
            entity_name="UV Level Time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
        ),
        DavisSensorEntityDescription(
            key="SolarRad",
            translation_key="solar_radiation",
            entity_name="Solar Radiation",
            icon="mdi:sun-wireless-outline",
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        ),
        DavisSensorEntityDescription(
            key="SolarRadDay",
            translation_key="solar_radiation_day",
            entity_name="Solar Radiation (Day)",
            icon="mdi:sun-wireless-outline",
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        ),
        DavisSensorEntityDescription(
            key="SolarRadTime",
            translation_key="solar_radiation_time",
            entity_name="Solar Radiation Time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
        ),
        DavisSensorEntityDescription(
            key="BatteryVolts",
            translation_key="battery_voltage",
            entity_name="Battery Voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            entity_category=EntityCategory.DIAGNOSTIC,
            suggested_display_precision=1,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="ForecastIcon",
            translation_key="forecast_icon",
            entity_name="Forecast Icon",
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="ForecastRuleNo",
            translation_key="forecast_rule",
            entity_name="Forecast Rule",
            icon="mdi:binoculars",
        ),
        DavisSensorEntityDescription(
            key="RainCollector",
            translation_key="rain_collector",
            entity_name="Rain Collector",
            icon="mdi:bucket-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.ENUM,
            options=[
                RAIN_COLLECTOR_IMPERIAL,
                RAIN_COLLECTOR_METRIC,
                RAIN_COLLECTOR_METRIC_0_1
            ],
        ),
        DavisSensorEntityDescription(
            key="RainStorm",
            translation_key="rain_storm",
            entity_name="Rain Storm",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1,
        ),
        DavisSensorEntityDescription(
            key="StormStartDate",
            translation_key="rain_storm_start_date",
            entity_name="Rain Storm Start Date",
            icon="mdi:calendar-outline",
            device_class=SensorDeviceClass.DATE,
        ),
        *[
            DavisSensorEntityDescription(
                key=f"ExtraTemps0{probe}",
                translation_key=f"extra_temperature_{probe}",
                entity_name=f"Extra Temperature {probe}",
                native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                entity_registry_enabled_default=False,
                suggested_display_precision=1,
            )
            for probe in range(1, 8)
        ],
        *[
            DavisSensorEntityDescription(
                key=f"HumExtra0{probe}",
                translation_key=f"extra_humidity_{probe}",
                entity_name=f"Extra Humidity {probe}",
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=PERCENTAGE,
                suggested_display_precision=0,
                entity_registry_enabled_default=False,
            )
            for probe in range(1, 8)
        ],
        DavisSensorEntityDescription(
            key="Latitude",
            translation_key="latitude",
            entity_name="Latitude",
            icon="mdi:latitude",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=DEGREE,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="Longitude",
            translation_key="longitude",
            entity_name="Longitude",
            icon="mdi:longitude",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=DEGREE,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="Elevation",
            translation_key="elevation",
            entity_name="Elevation",
            device_class=SensorDeviceClass.DISTANCE,
            icon="mdi:image-filter-hdr-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=UnitOfLength.FEET,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="LastReadoutDuration",
            translation_key="last_readout_duration",
            entity_name="Last Readout Duration",
            icon="mdi:timer-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_display_precision=1,
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="SunRise",
            translation_key="sunrise",
            entity_name="Sunrise",
            icon="mdi:sun-clock-outline",
            entity_registry_enabled_default=False,
        ),
        DavisSensorEntityDescription(
            key="SunSet",
            translation_key="sunset",
            entity_name="Sunset",
            icon="mdi:sun-clock-outline",
            entity_registry_enabled_default=False,
        ),
    ]

async def async_setup_entry(
    _,
    config_entry: DavisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Davis Vantage sensors based on a config entry."""
    coordinator = config_entry.runtime_data.coordinator
    model = config_entry.data.get(CONFIG_STATION_MODEL, '')
    entities = [
        DavisVantageSensor(
            coordinator=coordinator,
            entry_id=config_entry.entry_id,
            description=desc,
        )
        for desc in get_sensor_descriptions(model)
    ]
    async_add_entities(entities)

class DavisVantageSensor(CoordinatorEntity[DavisVantageDataUpdateCoordinator], SensorEntity):
    """Defines a Davis Vantage sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DavisVantageDataUpdateCoordinator,
        entry_id: str,
        description: DavisSensorEntityDescription,
    ) -> None:
        """Initialize Davis Vantage sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME} {description.entity_name}".lower()
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {description.entity_name}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:  # type: ignore
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
