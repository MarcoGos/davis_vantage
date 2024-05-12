import logging
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription,
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
    UnitOfTime
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    RAIN_COLLECTOR_IMPERIAL,
    RAIN_COLLECTOR_METRIC,
    CONFIG_STATION_MODEL,
    MODEL_VANTAGE_PRO2PLUS
)

from .coordinator import DavisVantageDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

def get_sensor_descriptions(model: str) -> list[SensorEntityDescription]:
    descriptions: list[SensorEntityDescription] = [
        SensorEntityDescription(
            key="Datetime",
            translation_key="Last Fetch Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastSuccessTime",
            translation_key="Last Success Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastErrorTime",
            translation_key="Last Error Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastError",
            translation_key="Last Error Message",
            icon="mdi:message-alert-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ArchiveInterval",
            translation_key="Archive Interval",
            icon="mdi:archive-clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            native_unit_of_measurement=UnitOfTime.MINUTES
        ),
        SensorEntityDescription(
            key="TempOut",
            translation_key="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="TempOutHiDay",
            translation_key="Temperature High (Day)",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-up"
        ),
        SensorEntityDescription(
            key="TempOutHiTime",
            translation_key="Temperature High Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="TempOutLowDay",
            translation_key="Temperature Low (Day)",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-down"
        ),
        SensorEntityDescription(
            key="TempOutLowTime",
            translation_key="Temperature Low Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="TempIn",
            translation_key="Temperature (Inside)",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HeatIndex",
            translation_key="Heat Index",
            icon="mdi:sun-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindChill",
            translation_key="Wind Chill",
            icon="mdi:snowflake-thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="FeelsLike",
            translation_key="Feels Like",
            icon="mdi:download-circle-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPoint",
            translation_key="Dew Point",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointHiDay",
            translation_key="Dew Point High (Day)",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointHiTime",
            translation_key="Dew Point High Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="DewPointLowDay",
            translation_key="Dew Point Low (Day)",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointLowTime",
            translation_key="Dew Point Low Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="Barometer",
            translation_key="Barometric Pressure",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerHiDay",
            translation_key="Barometric Pressure High (Day)",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerHiTime",
            translation_key="Barometric Pressure High Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="BarometerLowDay",
            translation_key="Barometric Pressure Low (Day)",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerLoTime",
            translation_key="Barometric Pressure Low Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="BarTrend",
            translation_key="Barometric Trend",
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
            translation_key="Humidity (Inside)",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumOut",
            translation_key="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class="measurement",
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0
        ),
        SensorEntityDescription(
            key="WindSpeed",
            translation_key="Wind Speed",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindSpeed10Min",
            translation_key="Wind Speed (Average)",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGust",
            translation_key="Wind Gust",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGustDay",
            translation_key="Wind Gust (Day)",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGustTime",
            translation_key="Wind Gust Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="WindDir",
            translation_key="Wind Direction",
            icon="mdi:compass-outline",
            state_class="measurement",
            native_unit_of_measurement=DEGREE,
            suggested_display_precision=0
        ),
        SensorEntityDescription(
            key="WindDirRose",
            translation_key="Wind Direction Rose",
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
            translation_key="Wind Speed (Bft)",
            icon="mdi:weather-windy",
            state_class="measurement",
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="RainDay",
            translation_key="Rain (Day)",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class="measurement",
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainMonth",
            translation_key="Rain (Month)",
            icon="mdi:water-outline",
            state_class="measurement",
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainYear",
            translation_key="Rain (Year)",
            icon="mdi:water-outline",
            state_class="measurement",
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainRate",
            translation_key="Rain Rate",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class="measurement",
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainRateDay",
            translation_key="Rain Rate (Day)",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class="measurement",
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="RainRateTime",
            translation_key="Rain Rate Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="UV",
            translation_key="UV Level",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="UVDay",
            translation_key="UV Level (Day)",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="UVTime",
            translation_key="UV Level Time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="SolarRad",
            translation_key="Solar Radiation",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER
        ),
        SensorEntityDescription(
            key="SolarRadDay",
            translation_key="Solar Radiation (Day)",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER
        ),
        SensorEntityDescription(
            key="SolarRadTime",
            translation_key="Solar Radiation Time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="BatteryVolts",
            translation_key="Battery Voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            entity_category=EntityCategory.DIAGNOSTIC,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ForecastIcon",
            translation_key="Forecast Icon",
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ForecastRuleNo",
            translation_key="Forecast Rule",
            icon="mdi:binoculars"
        ),
        SensorEntityDescription(
            key="RainCollector",
            translation_key="Rain Collector",
            icon="mdi:bucket-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            device_class=SensorDeviceClass.ENUM,
            options=[
                RAIN_COLLECTOR_IMPERIAL,
                RAIN_COLLECTOR_METRIC
            ]
        ),
        SensorEntityDescription(
            key="RainStorm",
            translation_key="Rain Storm",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class="measurement",
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="StormStartDate",
            translation_key="Rain Storm Start Date",
            icon="mdi:calendar-outline",
            device_class=SensorDeviceClass.DATE
        ),
        SensorEntityDescription(
            key="ExtraTemps01",
            translation_key="Extra Temperature 1",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps02",
            translation_key="Extra Temperature 2",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps03",
            translation_key="Extra Temperature 3",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps04",
            translation_key="Extra Temperature 4",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps05",
            translation_key="Extra Temperature 5",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps06",
            translation_key="Extra Temperature 6",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps07",
            translation_key="Extra Temperature 7",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="HumExtra01",
            translation_key="Extra Humidity 1",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra02",
            translation_key="Extra Humidity 2",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra03",
            translation_key="Extra Humidity 3",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra04",
            translation_key="Extra Humidity 4",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra05",
            translation_key="Extra Humidity 5",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra06",
            translation_key="Extra Humidity 6",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra07",
            translation_key="Extra Humidity 7",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
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
        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME} {description.translation_key}".lower()
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {description.translation_key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        key = self.entity_description.key
        data = self.coordinator.data
        if key not in data:
            return None
        if self.entity_description.native_unit_of_measurement is not None:
            default_value = 0
        else:
            default_value = '-'
        return data.get(key, default_value) # type: ignore
