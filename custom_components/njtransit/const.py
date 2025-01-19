"""Constants for NJ Transit integration."""
DOMAIN = "njtransit"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_STATION = "station"
CONF_STATION_CODE = "station_code"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# NJ Transit API endpoints
API_BASE_URL = "https://raildata.njtransit.com/api/TrainData"
AUTH_ENDPOINT = f"{API_BASE_URL}/getToken"
STATION_LIST_ENDPOINT = f"{API_BASE_URL}/getStationList"
SCHEDULE_ENDPOINT = f"{API_BASE_URL}/getTrainSchedule"