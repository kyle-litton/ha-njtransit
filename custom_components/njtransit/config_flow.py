"""Config flow for NJ Transit integration."""
import voluptuous as vol
import requests
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FROM_STATION,
    CONF_TO_STATION,
    AUTH_ENDPOINT,
    STATION_LIST_ENDPOINT
)

class NJTransitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NJ Transit."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # First authenticate to get token
                auth_response = requests.post(
                    AUTH_ENDPOINT,
                    json={
                        "username": user_input[CONF_USERNAME],
                        "password": user_input[CONF_PASSWORD]
                    },
                    headers={"accept": "application/json"}
                )
                auth_response.raise_for_status()
                token = auth_response.json().get("UserToken")

                # Test token by fetching station list
                stations_response = requests.post(
                    STATION_LIST_ENDPOINT,
                    json={"token": token},
                    headers={
                        "accept": "application/json",
                        "authorization": f"Bearer {token}"
                    }
                )
                stations_response.raise_for_status()
                
                stations = stations_response.json()
                station_codes = [station["code"] for station in stations]
                
                # Validate station codes
                if user_input[CONF_FROM_STATION] not in station_codes:
                    errors["from_station"] = "invalid_station"
                if user_input[CONF_TO_STATION] not in station_codes:
                    errors["to_station"] = "invalid_station"
                
                if not errors:
                    return self.async_create_entry(
                        title=f"NJ Transit {user_input[CONF_FROM_STATION]} to {user_input[CONF_TO_STATION]}",
                        data=user_input,
                    )
                    
            except requests.exceptions.RequestException:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_FROM_STATION): str,
                    vol.Required(CONF_TO_STATION): str,
                }
            ),
            errors=errors,
        )