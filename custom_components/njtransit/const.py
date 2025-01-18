"""Constants for the NJ Transit integration."""
DOMAIN = "njtransit"

# Configuration
CONF_API_KEY = "api_key"
CONF_USERNAME = "username"

# Station codes
STATION_CHATHAM = "CM"
STATION_HOBOKEN = "HB"

# Service endpoints
API_ENDPOINT = "https://api.njtransit.com/departureboard/v1/station"

# Default values
DEFAULT_NAME = "NJ Transit"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# Sensor attributes
ATTR_TRAIN_ID = "train_id"
ATTR_DEPARTURE_TIME = "departure_time"
ATTR_MINUTES_UNTIL = "minutes_until"
ATTR_STATUS = "status"
ATTR_TRACK = "track"
ATTR_NEXT_TRAINS = "next_trains"
ATTR_LAST_UPDATED = "last_updated"