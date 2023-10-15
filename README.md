![Version](https://img.shields.io/github/v/release/MarcoGos/davis_vantage?include_prereleases)

# Davis Vantage

This is a custom integration for the Davis Vantage Pro2 and Vue. Either use a serial port or use an ip adress to connect to your device. Tested with the Vantage Pro 2 combined with a Davis WeatherLink 6510SER serial port data logger (connected via a ser2usb converter to the ha server) and with a Vantage Vue combined with a WeatherLink IP. Probably works with the WeatherLink 6510USB as well. Other models unsure.

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

## Known problems

During first setup the communication to the weather station can be a bit tricky, resulting in an error saying the device didn't communicate. Please try again to set it up (can take up to 5 times).
