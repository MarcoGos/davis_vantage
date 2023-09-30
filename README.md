![Version](https://img.shields.io/github/v/release/MarcoGos/davis_vantage?include_prereleases)

# Davis Vantage

This is a custom integration for the Davis Vantage Pro2 and Vue.

## Installation

Via HACS:

- Add the following custom repository as an integration:
    - MarcoGos/davis_vantage
- Restart Home Assistant
- Add the integration to Home Assistant

## Setup

During the setup of the integration the serial port of the weather station needs to be provided.

Examples:
- tcp:192.168.0.18:1111
- serial:/dev/ttyUSB0:19200:8N1

![Setup](/assets/setup.png)

## What to expect

The following sensors will be registered:

![Sensors](/assets/sensors.png)

The sensor information is updated every 30 seconds.
