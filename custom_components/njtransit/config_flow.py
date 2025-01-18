"""Config flow for NJ Transit integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_API_KEY, CONF_USERNAME

class NJTransitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NJ Transit."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the credentials here
                return self.async_create_entry(
                    title="NJ Transit",
                    data={
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_USERNAME: user_input[CONF_USERNAME],
                    },
                )
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_USERNAME): str,
                }
            ),
            errors=errors,
        )