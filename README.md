# NJ Transit for Home Assistant

This integration provides NJ Transit train schedules in Home Assistant. Not affiliated with NJTransit please follow the usage rules outlined on the [NJ Transit Developer Portal](https://developer.njtransit.com/registration/docs). 

## Features

- Real-time train schedules
- Next train departure times
- Station status and track information

## Installation

### HACS (Recommended)
1. Open HACS in Home Assistant
2. Click on tridot
3. Click the "Custom Respositories"
4. Paste this repo url
5. Select "Integration" type
6. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/njtransit` folder to your `custom_components` directory
2. Restart Home Assistant


### How To Use

For now, the data returned from the API is larger than what can be used in one state entity.
I will plan to split these out into seperate attributes. Im the meantime add a new template sensor as shown below in your configuration yaml.

```
template:
- sensor:
  - name: "NJ Transit Schedule"
    state: >
      {{ state_attr('sensor.nj_transit_<your station>_station', 'trips')[0].status }} to {{ state_attr('sensor.nj_transit_<your station>_station', 'trips')[0].destination }}
    attributes:
      next_trip: >
        {{ state_attr('sensor.nj_transit_<your station>_station', 'trips')[0] }}
      upcoming_trips: >
        {{ state_attr('sensor.nj_transit_<your station>_station', 'trips')[1:] }}
```

With this template, you can use the data on your dashboard in a Markdown style card. I have plans to update this further in the future to use some custom CSS and look a bit closer to the nj transit boards.

```
- type: markdown
    title: NJ Transit Schedules
    content: >
        ### Next Train **Status**: {{ state_attr('sensor.nj_transit_schedule',
        'next_trip')['status'] }}   **Time**: {{
        state_attr('sensor.nj_transit_schedule',
        'next_trip')['scheduled_date'] }}   **Destination**: {{
        state_attr('sensor.nj_transit_schedule', 'next_trip')['destination']
        }}   **Line**: {{ state_attr('sensor.nj_transit_schedule',
        'next_trip')['line'] }}   **Track**: {{
        state_attr('sensor.nj_transit_schedule', 'next_trip')['track'] }}  

        ### Upcoming Trips {% for trip in
        state_attr('sensor.nj_transit_schedule', 'upcoming_trips') %} -
        **Time**: {{ trip.scheduled_date }}  
        **Destination**: {{ trip.destination }}  
        **Line**: {{ trip.line }}  
        **Track**: {{ trip.track }}  
        **Status**: {{ trip.status or 'On Time' }}
        {% endfor %}
```

## Configuration

1. In Home Assistant, go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "NJ Transit"
4. Enter your NJ Transit API credentials:
   - API Key
   - Username

You can obtain API credentials from the [NJ Transit Developer Portal](https://developer.njtransit.com/registration/docs).

## Usage

After configuration, the integration will create a new sensors:
- `sensor.station`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.