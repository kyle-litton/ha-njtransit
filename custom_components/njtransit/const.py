"""Constants for NJ Transit integration."""
DOMAIN = "njtransit"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_FROM_STATION = "from_station"
CONF_TO_STATION = "to_station"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# NJ Transit API endpoints
API_BASE_URL = "https://testraildata.njtransit.com/api"
AUTH_ENDPOINT = f"{API_BASE_URL}/TrainData/getToken"
STATION_LIST_ENDPOINT = f"{API_BASE_URL}/TrainData/getStationList"
SCHEDULE_ENDPOINT = f"{API_BASE_URL}/TrainData/getTrainSchedule"