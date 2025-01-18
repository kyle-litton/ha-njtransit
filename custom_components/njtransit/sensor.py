"""Support for NJ Transit sensors."""
from datetime import timedelta
import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import NJTransitAPI
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_USERNAME,
    STATION_CHATHAM,
    STATION_HOBOKEN,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NJ Transit sensor based on a config entry."""
    api = NJTransitAPI(
        api_key=entry.data[CONF_API_KEY],
        username=entry.data[CONF_USERNAME],
    )

    async def async_update_data():
        """Fetch data from API."""
        return {
            "outbound": await hass.async_add_executor_job(
                api.get_train_schedule, STATION_CHATHAM, STATION_HOBOKEN
            ),
            "inbound": await hass.async_add_executor_job(
                api.get_train_schedule, STATION_HOBOKEN, STATION_CHATHAM
            ),
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="njtransit",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            NJTransitSensor(coordinator, "outbound", "Chatham to Hoboken"),
            NJTransitSensor(coordinator, "inbound", "Hoboken to Chatham"),
        ]
    )

class NJTransitSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NJ Transit sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        direction: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._direction = direction
        self._attr_name = name
        self._attr_unique_id = f"njtransit_{direction}"

    @property
    def native_value(self) -> Optional[str]:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get(self._direction):
            return None
        next_train = self.coordinator.data[self._direction][0]
        return f"{next_train['departure_time']} ({next_train['minutes_until']}min)"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get(self._direction):
            return {}
        return {
            "next_trains": self.coordinator.data[self._direction],
            "last_updated": self.coordinator.last_update_success_time,
        }

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:train"