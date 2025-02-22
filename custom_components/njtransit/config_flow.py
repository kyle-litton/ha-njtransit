"""Config flow for NJ Transit integration."""

import voluptuous as vol
import aiohttp
import logging
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_STATION,
    CONF_STATION_CODE,
    AUTH_ENDPOINT,
    STATION_LIST_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class NJTransitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NJ Transit."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    # First authenticate to get token
                    auth_form = aiohttp.FormData()
                    auth_form.add_field("username", user_input[CONF_USERNAME])
                    auth_form.add_field("password", user_input[CONF_PASSWORD])

                    async with session.post(
                        AUTH_ENDPOINT,
                        data=auth_form,
                        headers={"accept": "application/json"},
                    ) as auth_response:
                        auth_response.raise_for_status()
                        auth_data = await auth_response.json()
                        token = auth_data.get("UserToken")

                    # Test token by fetching station list
                    station_form = aiohttp.FormData()
                    station_form.add_field("token", token)

                    async with session.post(
                        STATION_LIST_ENDPOINT,
                        data=station_form,
                        headers={
                            "accept": "application/json",
                            "authorization": f"Bearer {token}",
                        },
                    ) as stations_response:
                        stations_response.raise_for_status()
                        stations = await stations_response.json()

                        station_details = {
                            station["STATIONNAME"]: station for station in stations
                        }

                        # Validate station codes, and grab the station code
                        if user_input[CONF_STATION] not in station_details.keys():
                            errors["station"] = "invalid_station"

                        if not errors:
                            user_input[CONF_STATION_CODE] = station_details[
                                user_input[CONF_STATION]
                            ]["STATION_2CHAR"]
                            return self.async_create_entry(
                                title=f"NJ Transit: {user_input[CONF_STATION]} Station",
                                data=user_input,
                            )

            except aiohttp.ClientError as exception:
                _LOGGER.error("Error: %s", exception)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_STATION): str,
                }
            ),
            errors=errors,
        )
