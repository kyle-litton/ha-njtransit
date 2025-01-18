"""NJ Transit sensor platform."""
from __future__ import annotations

import logging
import requests
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FROM_STATION,
    CONF_TO_STATION,
    AUTH_ENDPOINT,
    SCHEDULE_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the NJ Transit sensor from config entry."""
    config = config_entry.data
    
    sensor = NJTransitSensor(
        f"NJ Transit {config[CONF_FROM_STATION]} to {config[CONF_TO_STATION]}",
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
        config[CONF_FROM_STATION],
        config[CONF_TO_STATION]
    )
    
    async_add_entities([sensor], True)

class NJTransitSensor(SensorEntity):
    """Implementation of a NJ Transit sensor."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "trips"

    def __init__(
        self,
        name: str,
        username: str,
        password: str,
        from_station: str,
        to_station: str
    ) -> None:
        """Initialize the sensor."""
        self._attr_name = name
        self._username = username
        self._password = password
        self._from_station = from_station
        self._to_station = to_station
        self._attr_unique_id = f"njtransit_{from_station}_to_{to_station}"
        
        self._token: str | None = None
        self._token_expires: datetime | None = None
        self._attr_native_value: StateType | datetime = None
        self._attr_extra_state_attributes: dict[str, Any] = {}

    def _get_token(self) -> str | None:
        """Get authentication token."""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token

        try:
            response = requests.post(
                AUTH_ENDPOINT,
                json={
                    "username": self._username,
                    "password": self._password
                },
                headers={"accept": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            auth_data = response.json()
            
            self._token = auth_data.get("token")
            self._token_expires = datetime.now() + timedelta(hours=12)
            
            return self._token

        except requests.exceptions.RequestException as error:
            _LOGGER.error("Error authenticating with NJ Transit API: %s", error)
            raise ConfigEntryAuthFailed from error

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:train"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            token = self._get_token()
            if not token:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {}
                return

            headers = {
                "accept": "application/json",
            }

            # Get schedule for both directions
            params = {
                "token": token,
                "origin": self._from_station,
                "destination": self._to_station,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Get outbound schedule
            response = requests.post(
                SCHEDULE_ENDPOINT,
                json=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            outbound_data = response.json()

            # Get inbound schedule (swap origin and destination)
            params["origin"], params["destination"] = params["destination"], params["origin"]
            response = requests.post(
                SCHEDULE_ENDPOINT,
                json=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            inbound_data = response.json()
            _LOGGER.warning(inbound_data)
            # Process the next 3 trips in each direction
            outbound_trips = []
            inbound_trips = []
            
            # Parse outbound trips (from -> to)
            for trip in outbound_data.get("trips", [])[:3]:
                outbound_trips.append({
                    "departure_time": trip.get("departure_time"),
                    "arrival_time": trip.get("arrival_time"),
                    "train_id": trip.get("train_id"),
                    "line": trip.get("line"),
                    "status": trip.get("status", "Unknown")
                })

            # Parse inbound trips (to -> from)
            for trip in inbound_data.get("trips", [])[:3]:
                inbound_trips.append({
                    "departure_time": trip.get("departure_time"),
                    "arrival_time": trip.get("arrival_time"),
                    "train_id": trip.get("train_id"),
                    "line": trip.get("line"),
                    "status": trip.get("status", "Unknown")
                })

            # Update state and attributes
            self._attr_native_value = len(outbound_trips + inbound_trips)
            self._attr_extra_state_attributes = {
                "outbound_trips": outbound_trips,
                "inbound_trips": inbound_trips,
                "last_updated": datetime.now().isoformat(),
                "from_station": self._from_station,
                "to_station": self._to_station
            }

        except requests.exceptions.RequestException as error:
            _LOGGER.error("Error fetching data from NJ Transit API: %s", error)
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
            if "401" in str(error) or "403" in str(error):
                raise ConfigEntryAuthFailed from error