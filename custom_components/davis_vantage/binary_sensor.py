"""Binary sensor setup for our Integration."""

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DavisConfigEntry
from .const import DEFAULT_NAME, KEY_TO_NAME
from .coordinator import DavisVantageDataUpdateCoordinator

DESCRIPTIONS: list[BinarySensorEntityDescription] = [
    BinarySensorEntityDescription(key="IsRaining", translation_key="is_raining")
]


async def async_setup_entry(
    _,
    config_entry: DavisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Davis Vantage sensors based on a config entry."""
    coordinator = config_entry.runtime_data.coordinator

    entities: list[DavisVantageBinarySensor] = []

    # Add all binary sensors described above.
    for description in DESCRIPTIONS:
        entities.append(
            DavisVantageBinarySensor(
                coordinator=coordinator,
                entry_id=config_entry.entry_id,
                description=description,
            )
        )

    async_add_entities(entities)


class DavisVantageBinarySensor(
    CoordinatorEntity[DavisVantageDataUpdateCoordinator], BinarySensorEntity
):
    """Defines a Davis Vantage sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DavisVantageDataUpdateCoordinator,
        entry_id: str,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize Davis Vantage sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self.entity_id = (
            f"{BINARY_SENSOR_DOMAIN}.{DEFAULT_NAME} {KEY_TO_NAME[description.key]}".lower()
        )
        self._attr_unique_id = (
            f"{entry_id}-{DEFAULT_NAME} {KEY_TO_NAME[description.key]}"
        )
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:  # type: ignore
        """Return the is_on of the sensor."""
        key = self.entity_description.key
        data = self.coordinator.data
        if key not in data:
            return None
        return data.get(key, False)  # type: ignore
