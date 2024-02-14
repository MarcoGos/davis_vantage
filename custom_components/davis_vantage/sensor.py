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
            name="Last Fetch Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastSuccessTime",
            name="Last Success Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastErrorTime",
            name="Last Error Time",
            icon="mdi:clock-outline",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="LastError",
            name="Last Error Message",
            icon="mdi:message-alert-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ArchiveInterval",
            name="Archive Interval",
            icon="mdi:archive-clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            native_unit_of_measurement=UnitOfTime.MINUTES
        ),
        SensorEntityDescription(
            key="TempOut",
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="TempOutHiDay",
            name="Temperature High (Day)",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-up"
        ),
        SensorEntityDescription(
            key="TempOutHiTime",
            name="Temperature High Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="TempOutLowDay",
            name="Temperature Low (Day)",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            icon="mdi:thermometer-chevron-down"
        ),
        SensorEntityDescription(
            key="TempOutLowTime",
            name="Temperature Low Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="TempIn",
            name="Temperature (Inside)",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HeatIndex",
            name="Heat Index",
            icon="mdi:sun-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindChill",
            name="Wind Chill",
            icon="mdi:snowflake-thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="FeelsLike",
            name="Feels Like",
            icon="mdi:download-circle-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPoint",
            name="Dew Point",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointHiDay",
            name="Dew Point High (Day)",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointHiTime",
            name="Dew Point High Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="DewPointLowDay",
            name="Dew Point Low (Day)",
            icon="mdi:water-thermometer-outline",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="DewPointLowTime",
            name="Dew Point Low Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="Barometer",
            name="Barometric Pressure",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerHiDay",
            name="Barometric Pressure High (Day)",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerHiTime",
            name="Barometric Pressure High Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="BarometerLowDay",
            name="Barometric Pressure Low (Day)",
            device_class=SensorDeviceClass.PRESSURE,
            state_class="measurement",
            native_unit_of_measurement=UnitOfPressure.INHG,
            suggested_display_precision=2
        ),
        SensorEntityDescription(
            key="BarometerLoTime",
            name="Barometric Pressure Low Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="BarTrend",
            name="Barometric Trend",
            device_class=SensorDeviceClass.ENUM,
            translation_key="davis_vantage_barometric_trend",
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
            name="Humidity (Inside)",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumOut",
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class="measurement",
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0
        ),
        SensorEntityDescription(
            key="WindSpeed",
            name="Wind Speed",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindSpeed10Min",
            name="Wind Speed (Average)",
            icon="mdi:weather-windy",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGust",
            name="Wind Gust",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGustDay",
            name="Wind Gust (Day)",
            icon="mdi:windsock",
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class="measurement",
            native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="WindGustTime",
            name="Wind Gust Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="WindDir",
            name="Wind Direction",
            icon="mdi:compass-outline",
            state_class="measurement",
            native_unit_of_measurement=DEGREE,
            suggested_display_precision=0
        ),
        SensorEntityDescription(
            key="WindDirRose",
            name="Wind Direction Rose",
            device_class=SensorDeviceClass.ENUM,
            translation_key="wind_direction_rose",
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
            name="Wind Speed (Bft)",
            icon="mdi:weather-windy",
            state_class="measurement",
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="RainDay",
            name="Rain (Day)",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class="measurement",
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="RainMonth",
            name="Rain (Month)",
            icon="mdi:water-outline",
            state_class="measurement",
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="RainYear",
            name="Rain (Year)",
            icon="mdi:water-outline",
            state_class="measurement",
            device_class=SensorDeviceClass.PRECIPITATION,
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="RainRate",
            name="Rain Rate",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class="measurement",
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="RainRateDay",
            name="Rain Rate (Day)",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
            state_class="measurement",
            native_unit_of_measurement=UnitOfVolumetricFlux.INCHES_PER_HOUR,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="RainRateTime",
            name="Rain Rate Time",
            icon="mdi:clock-in"
        ),
        SensorEntityDescription(
            key="UV",
            name="UV Level",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="UVDay",
            name="UV Level (Day)",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="UVTime",
            name="UV Level Time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="SolarRad",
            name="Solar Radiation",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER
        ),
        SensorEntityDescription(
            key="SolarRadDay",
            name="Solar Radiation (Day)",
            icon="mdi:sun-wireless-outline",
            state_class="measurement",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS,
            native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER
        ),
        SensorEntityDescription(
            key="SolarRadTime",
            name="Solar Radiation Time",
            icon="mdi:clock-in",
            entity_registry_enabled_default=model==MODEL_VANTAGE_PRO2PLUS
        ),
        SensorEntityDescription(
            key="BatteryVolts",
            name="Battery Voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            entity_category=EntityCategory.DIAGNOSTIC,
            suggested_display_precision=1,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ForecastIcon",
            name="Forecast Icon",
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="ForecastRuleNo",
            name="Forecast Rule",
            icon="mdi:binoculars"
        ),
        SensorEntityDescription(
            key="RainCollector",
            name="Rain Collector",
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
            name="Rain Storm",
            icon="mdi:water-outline",
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class="measurement",
            native_unit_of_measurement=UnitOfLength.INCHES,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="StormStartDate",
            name="Rain Storm Start Date",
            icon="mdi:calendar-outline",
            device_class=SensorDeviceClass.DATE
        ),
        SensorEntityDescription(
            key="ExtraTemps01",
            name="Extra Temperature 1",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps02",
            name="Extra Temperature 2",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps03",
            name="Extra Temperature 3",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps04",
            name="Extra Temperature 4",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps05",
            name="Extra Temperature 5",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps06",
            name="Extra Temperature 6",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="ExtraTemps07",
            name="Extra Temperature 7",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class="measurement",
            entity_registry_enabled_default=False,
            suggested_display_precision=1
        ),
        SensorEntityDescription(
            key="HumExtra01",
            name="Extra Humidity 1",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra02",
            name="Extra Humidity 2",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra03",
            name="Extra Humidity 3",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra04",
            name="Extra Humidity 4",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra05",
            name="Extra Humidity 5",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra06",
            name="Extra Humidity 6",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            suggested_display_precision=0,
            entity_registry_enabled_default=False
        ),
        SensorEntityDescription(
            key="HumExtra07",
            name="Extra Humidity 7",
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

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{description.name}".lower()
        )
        self.entity_description = description
        self._attr_name = description.name # type: ignore
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {self.name}"
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
