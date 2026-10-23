"""Binary sensor setup for our Integration."""

from dataclasses import dataclass
from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DavisConfigEntry
from .const import DEFAULT_NAME
from .coordinator import DavisVantageDataUpdateCoordinator
from .utils import normalize_unique_id

@dataclass(frozen=True, kw_only=True)
class DavisVantageBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Davis Vantage binary sensor entity."""

    entity_name: str

DESCRIPTIONS: list[DavisVantageBinarySensorEntityDescription] = [
    DavisVantageBinarySensorEntityDescription(
        key="IsRaining", 
        translation_key="is_raining", 
        entity_name="Is Raining"),
    DavisVantageBinarySensorEntityDescription(
        key="TransmitterBatteryLow",
        translation_key="transmitter_battery_low",
        entity_name="Transmitter Battery Low",
        device_class=BinarySensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC),
]


async def async_setup_entry(
    _,
    config_entry: DavisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Davis Vantage sensors based on a config entry."""
    coordinator = config_entry.runtime_data.coordinator
    entity_registry = async_get_entity_registry(coordinator.hass)

    # Migrate old unique_ids with spaces or brackets to new ones with underscores and no brackets (preserve entity history)
    for desc in DESCRIPTIONS:
        if desc.entity_name:
            old_unique_id = f"{config_entry.entry_id}-{DEFAULT_NAME} {desc.entity_name}"
            new_unique_id = normalize_unique_id(old_unique_id)
            entity = entity_registry.async_get_entity_id(
                BINARY_SENSOR_DOMAIN, config_entry.domain, old_unique_id
            )
            if entity and not entity_registry.async_get_entity_id(
                BINARY_SENSOR_DOMAIN, config_entry.domain, new_unique_id
            ):
                entity_registry.async_update_entity(entity, new_unique_id=new_unique_id)

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
        description: DavisVantageBinarySensorEntityDescription,
    ) -> None:
        """Initialize Davis Vantage sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = normalize_unique_id(
            f"{entry_id}_{DEFAULT_NAME}_{description.entity_name}"
        )
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:  # type: ignore
        """Return the is_on of the sensor."""
        key = self.entity_description.key
        data = self.coordinator.data
        if not data:
            return None
        if key not in data:
            return None
        return data.get(key, False)  # type: ignore
