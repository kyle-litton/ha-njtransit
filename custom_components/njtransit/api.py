"""NJ Transit API client."""
from datetime import datetime
import logging
from typing import Any, Dict, List

import pytz
import requests

from .const import API_ENDPOINT

_LOGGER = logging.getLogger(__name__)

class NJTransitAPI:
    """NJ Transit API client."""

    def __init__(self, api_key: str, username: str) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._username = username
        self._session = requests.Session()
        self._session.headers.update({
            'x-api-key': self._api_key,
            'Authorization': self._username
        })

    def get_train_schedule(self, origin: str, destination: str, num_trips: int = 3) -> List[Dict[str, Any]]:
        """Get train schedule between stations."""
        params = {
            'station': origin,
            'direction': 'to',
            'destination': destination,
            'count': num_trips
        }

        try:
            response = self._session.get(API_ENDPOINT, params=params)
            response.raise_for_status()
            return self._format_train_data(response.json()['departures'])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching train schedule: %s", err)
            return []

    def _format_train_data(self, trains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format train data with calculated fields."""
        eastern = pytz.timezone('America/New_York')
        current_time = datetime.now(eastern)
        
        formatted_trains = []
        for train in trains:
            departure_time = datetime.fromisoformat(train['scheduledDepartureTime'])
            time_until = departure_time - current_time
            minutes_until = int(time_until.total_seconds() / 60)
            
            formatted_trains.append({
                'train_id': train['trainId'],
                'departure_time': departure_time.strftime('%I:%M %p'),
                'minutes_until': minutes_until,
                'status': train['status'],
                'track': train.get('track', 'TBA')
            })
        
        return formatted_trains