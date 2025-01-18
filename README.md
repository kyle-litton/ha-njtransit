# NJ Transit for Home Assistant

This integration provides NJ Transit train schedules in Home Assistant.

## Features

- Real-time train schedules
- Next train departure times
- Train status and track information
- Automatic updates every 5 minutes
- Support for both directions

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

## Configuration

1. In Home Assistant, go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "NJ Transit"
4. Enter your NJ Transit API credentials:
   - API Key
   - Username

You can obtain API credentials from the [NJ Transit Developer Portal](https://developer.njtransit.com/registration/docs).

## Usage

After configuration, the integration will create two sensors:
- `sensor.source_to_destination`
- `sensor.destination_to_source`

Each sensor provides:
- Next departure time
- Minutes until departure
- Train status
- Track information
- Additional upcoming trains as attributes

### Example Lovelace Card

```yaml
type: entities
title: NJ Transit Trains
entities:
  - entity: sensor.source_to_destination
  - entity: sensor.destination_to_source
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.