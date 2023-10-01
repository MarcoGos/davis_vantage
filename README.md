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

During the setup of the integration the serial port or the hostname of the weather station needs to be provided.

Example network host: 192.168.0.18:1111

![Setup](/assets/setup.png)

## What to expect

The following sensors will be registered:

![Sensors](/assets/sensors.png)

The sensor information is updated every 30 seconds.
