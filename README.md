![Version](https://img.shields.io/github/v/release/MarcoGos/davis_vantage?include_prereleases)

# Davis Vantage

This is a custom integration for the Davis Vantage Pro2 and Vue. Either use a serial port or use an ip adress to connect to your device. Tested with the Vantage Pro 2 combined with a Davis WeatherLink 6510SER serial port data logger (connected via a ser2usb converter to the ha server) and with a Vantage Vue combined with a WeatherLink IP. Probably works with the WeatherLink 6510USB as well. Other models unsure.

Every readout takes up about 20-25 seconds. So intervals smaller than 30 seconds are not available.

## Installation

Via HACS:

- Add the following custom repository as an integration:
    - MarcoGos/davis_vantage
- Restart Home Assistant
- Add the integration to Home Assistant

## Setup

During the setup of the integration the serial port or the hostname of the weather station needs to be provided.

Example network host: 192.168.0.18:1111

## What to expect?

The following entities will be created:

- Barometric Pressure:
    - Current barometric pressure
- Barometric Pressure High (Day): 
    - Today's highest barometric pressure
- Barometric Pressure High Time:
    - Time of today's highest barometric pressure
- Barometric Pressure Low (Day): 
    - Today's lowest barometric pressure
- Barometric Pressure Low Time:
    - Time of today's lowest barometric pressure
- Barometric Trend: 
    - Current barometric trend, being Stable, Rising Slowly, Rising Rapidly, Falling Slowly, Falling Rapidly
- Dew Point: 
    - Current dev point
- Dew Point High (Day)
    - Today's highest dew point
- Dew Point High Time
    - Time of today's highest dew point
- Dew Point Low (Day)
    - Today's lowest dew point
- Dew Point Low Time
    - Time of today's lowest dew point
- Feels Like: 
    - Current feels like temperature
- Forecast Rule: 
    - Current forecast rule
- Heat Index: 
    - Current heat index
- Humidity: 
    - Current outside relative humidify
- Humidity High (Day): 
    - Today's highest outside relative humididy
- Humidity Low (Day): 
    - Today's lowest outside relative humidity
- Is Raining: 
    - True if it's currently raining (based on rain rate)
- Rain (Day): 
    - Today's total precipitation
- Rain (Month): 
    - This months total precipitation
- Rain (Year): 
    - This year total precipitation
- Rain Rate: 
    - Current rain rate
- Rain Rate (Day): 
    - Today's highest rain rate
- Rain Rate Time:
    - Time of today's highest rain rate (or Unknown if no rain)
- Solar Radiation: 
    - Current solar radiation
- Solar Radiation (Day): 
    - Today's highest solar radiation
- Solar Radiation Time:
    - Time of today's highest solar radiation (or Unknown if dark day)
- Temperature: 
    - Current outside temperature
- Temperature High (Day): 
    - Today's highest outside temperature
- Temperature High Time: 
    - Time of today's highest outside temperature
- Temperature Low (Day): 
    - Today's lowest outside temperature
- Temperature Low Time: 
    - Time of today's lowest outside temperature
- UV Level: 
    - Current UV level
- UV Level (Day): 
    - Today's highest UV level
- UV Level Time: 
    - Time of today's highest UV level
- Wind Chill: 
    - Current wind chill
- Wind Direction: 
    - Current wind direction in degrees
- Wind Direction Rose: 
    - Current wind direction in cardinal directions (N, NE, E, etc.)
- Wind Gust: 
    - Current wind gust, based on the highest value within an Archive Interval
- Wind Gust (Day): 
    - Today's highest wind gust
- Wind Gust Time: 
    - Time of today's highest wind gust
- Wind Speed: 
    - Current wind speed
- Wind Speed (Avarage): 
    - 10 minutes average wind speed
- Wind Speed (Bft): 
    - 10 minutes average wind speed in Beaufort
- Extra Humidity 1-7: 
    - Current humidity extra sensor 1-7
- Extra Temperature 1-7:
    - Current temperature extra sensor 1-7
- Forecast Icon: 
    - Current forecast icon number
- Humidity (Inside): 
    - Current inside relative humidity
- Temperature (Inside): 
    - Current inside temperature

Diagnostic entities:
- Archive Interval: 
    - Archive data interval (usual around 10 minutes)
- Last Error Message: 
    - Last error message, if no error then empty
- Last Fetch Time: 
    - Last fetch time
- Battery Voltage: 
    - Current battery voltage
- Cardinal Directions: 
    - Number of cardinal direction 8 or 16 (set during setup)
- Last Error Time: 
    - Last error time
- Last Success Time: 
    - Last success time
- Rain Collector: 
    - Current rain collector setup (0.01" or 0.2 mm)

The entity information is updated every 30 seconds (default or other value is choosen otherwise during setup).

## Known problems

During first setup the communication to the weather station can be a bit tricky, resulting in an error saying the device didn't communicate. Please try again to set it up (can take up to 5 times).

Determining Wind Gust value is done by reading archive data of the weather station. Unfortunately this part of the library function is a bit unstable.