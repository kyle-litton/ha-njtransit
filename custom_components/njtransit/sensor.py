"""NJ Transit sensor platform."""
from __future__ import annotations

import logging
import aiohttp
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
    CONF_STATION_CODE,
    CONF_STATION,
    AUTH_ENDPOINT,
    SCHEDULE_ENDPOINT,
)

SCAN_INTERVAL = timedelta(minutes=5)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the NJ Transit sensor from config entry."""
    config = config_entry.data
    
    sensor = NJTransitSensor(
        f"NJ Transit {config[CONF_STATION]} Station",
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
        config[CONF_STATION],
        config[CONF_STATION_CODE]
    )
    
    async_add_entities([sensor], True)

class NJTransitSensor(SensorEntity):
    """Implementation of a NJ Transit sensor."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "trips"
    _attr_scan_interval = SCAN_INTERVAL

    def __init__(
        self,
        name: str,
        username: str,
        password: str,
        station: str,
        station_code: str
    ) -> None:
        """Initialize the sensor."""
        self._attr_name = name
        self._username = username
        self._password = password
        self._station = station
        self._station_code = station_code
        self._attr_unique_id = f"njtransit__{station}"
        
        self._token: str | None = None
        self._token_expires: datetime | None = None
        self._attr_native_value: StateType | datetime = None
        self._attr_extra_state_attributes: dict[str, Any] = {}

    async def _get_token(self) -> str | None:
        """Get authentication token."""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token

        try:
            async with aiohttp.ClientSession() as session:
                auth_form = aiohttp.FormData()
                auth_form.add_field("username", self._username)
                auth_form.add_field("password", self._password)

                async with session.post(
                    AUTH_ENDPOINT,
                    data=auth_form,
                    headers={"accept": "application/json"},
                    timeout=10
                ) as response:
                    response.raise_for_status()
                    auth_data = await response.json()
                    
                    self._token = auth_data.get("UserToken")
                    self._token_expires = datetime.now() + timedelta(hours=12)
                    
                    return self._token

        except aiohttp.ClientError as error:
            _LOGGER.error("Error authenticating with NJ Transit API: %s", error)
            raise ConfigEntryAuthFailed from error

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:train"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            token = await self._get_token()
            if not token:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {}
                return

            headers = {
                "accept": "application/json",
            }

            # Get schedule for station
            params = aiohttp.FormData()
            params.add_field("token", token)
            params.add_field("station", self._station_code)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SCHEDULE_ENDPOINT,
                    data=params,
                    headers=headers,
                    timeout=10
                ) as response:
                    response.raise_for_status()
                    station_data = await response.json()

            trips = []
            for trip in station_data.get("ITEMS", [])[:5]:
                trips.append({
                    "status": trip.get("STATUS", "Unknown"),
                    "scheduled_date": trip.get("SCHED_DEP_DATE"),
                    "destination": trip.get("DESTINATION"),
                    "line": trip.get("LINEABBREVIATION"),
                    "track": trip.get("TRACK", "Unknown")
                })

            self._attr_native_value = len(trips)
            self._attr_extra_state_attributes = {
                "trips": trips,
                "last_updated": datetime.now().isoformat(),
                "station": self._station,
            }

        except aiohttp.ClientError as error:
            _LOGGER.error("Error fetching data from NJ Transit API: %s", error)
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
            if "401" in str(error) or "403" in str(error):
                raise ConfigEntryAuthFailed from error