# Davis Vantage

[![hacs][hacs-badge]][hacs-url]
[![release][release-badge]][release-url]
![downloads][downloads-badge]

This is a custom integration for the Davis Vantage Pro2. Either use a serial port or use an ip adress to connect to your device.

Model | Compatible
---|:---:
Davis WeatherLink SER (6510SER) | Yes
Davis WeatherLink USB (6510USB) | Yes
Davis Weatherlink IP (6555IP) | Yes 
Vantage Vue | Yes
WeatherLink Live | No
Davis Weather Envoy8X (6318EU) | No
Other models | Unsure

Every readout takes up about 20-25 seconds. So intervals smaller than 30 seconds are not available.

## Installation

Via HACS, just search for Davis Vantage.

## Setup

During the setup of the integration the serial port or the hostname of the weather station needs to be provided.

Example network host: 192.168.0.18:22222

If you're not sure about the port number (usually port 22222), then browse to the ip address of the IP logger and look at the port number on the configuration page.

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
- Rain Storm:
    - Total rainfall during an extended period of rain
- Rain Storm Start Date:
    - Start date of current rain storm. The rain period starts with a minimal of 2 ticks of the precipitation meter (0.4mm or 2/100") and ends after 24h of no rain.
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
    - Time of today's highest UV level (or Unknown if dark day)
- Wind Chill: 
    - Current wind chill
- Wind Direction: 
    - Current wind direction in degrees
- Wind Direction Rose: 
    - Current wind direction in cardinal directions (N, NE, E, etc.)
- Wind Gust: 
    - Current wind gust, based on the highest value within an Archive Interval [^1]
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
    - Archive data interval (usual around 10 minutes). [^2]
- Last Error Message: 
    - Last error message, if no error then empty
- Last Fetch Time: 
    - Last fetch time
- Battery Voltage: 
    - Current battery voltage
- Last Error Time: 
    - Last error time
- Last Success Time: 
    - Last success time
- Rain Collector: 
    - Current rain collector setup (0.01" or 0.2 mm)

The entity information is updated every 30 seconds (default or other value is choosen otherwise during setup).

## Known problems

During first setup the communication to the weather station can be a bit tricky, resulting in an error saying the device didn't communicate. Please try again to set it up (can take up to 5 times).

<!-- Badges -->

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/MarcoGos/davis_vantage?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/MarcoGos/davis_vantage/total?style=flat-square

[release-url]: https://github.com/MarcoGos/davis_vantage/releases

[^1]: If Wind Gust doesn't show a value or "Unknown" make sure the Davis time is set correctly. You can check this by using action "Davis Vantage: Get Davis Time" and, if necessary, correct it by using action "Davis Vantage: Set Davis Time".
[^2]: This value can only be changed by using the original WeatherLink software.


