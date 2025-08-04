# Davis Vantage

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
![Install Stats][stats]

![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

This is a custom integration for the Davis Vantage Pro2. Either use a serial port or use an ip adress to connect to your device.

Model | Compatible
---|:---:
Davis WeatherLink SER (6510SER) | Yes
Davis WeatherLink USB (6510USB) | Yes
Davis WeatherlinkIP (6555IP) | Yes[^3]
Vantage Vue | Yes
WeatherLink Live | No
Davis Weather Envoy8X (6318EU) | No
Other models | Unsure

## Prerequirements

Make sure your Davis device is on the lastest firmware:

Model | Version
---|:---:
Vantage Pro2 Console (Wired/Cabled) | 3.88
Weather Envoy Wireless | 3.88
Weather Envoy Cabled | 3.12
WeatherLinkIP Data Logger | 1.1.5

## Installation

Via HACS, just search for Davis Vantage.

## Setup

### Protocol
During the setup of the integration the serial port or the hostname of the weather station needs to be provided. When choosing serial a list of possible ports are visible. 

When choosing network, provide a hostname or ip address and port number:

Example: 192.168.1.8:22222

If you're not sure about the port number (usually port 22222), then browse to the ip address of the IP logger and look at the port number on the configuration page.

### Interval
Interval between readouts. Every readout takes up about 1-2 seconds for WeatherLink USB and WeatherLink SER and about 5-6 seconds for WeatherLinkIP.

### Persistent connection
When getting errors like "Broken pipe", try enabling this setting. This keeps the connection to the console or Envoy open between readouts. This is a recommended setting when using the WeatherLinkIP.

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
- Extra Humidity 1-7: 
    - Current humidity extra sensor 1-7
- Extra Temperature 1-7:
    - Current temperature extra sensor 1-7
- Feels Like: 
    - Current feels like temperature
- Forecast Icon: 
    - Current forecast icon number
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
- Humidity (Inside): 
    - Current inside relative humidity
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
- Sun Rise
    - Time of sun rise
- Sun Set
    - Time of sun set
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
- Temperature (Inside): 
    - Current inside temperature
- UV Level: 
    - Current UV level
- UV Level (Day): 
    - Today's highest UV level
- UV Level Time: 
    - Time of today's highest UV level (or Unknown if dark day)
- Wind Chill: 
    - Current wind chill
- Wind Direction: 
    - Current wind direction in degrees [^4] [^5]
- Wind Direction (Average):
    - Average/dominant wind direction in degrees, based on Archive Interval [^1] [^4]
- Wind Direction Rose: 
    - Current wind direction in cardinal directions (N, NE, E, etc.) [^4]
- Wind Direction (Rose) (Average)
    - Average/dominant wind direction in cardinal directions (N, NE, E, etc.), based on Archive Interval [^1] [^4]
- Wind Gust:
    - Current wind gust, based on the highest value within an Archive Interval [^1]
- Wind Gust (Day): 
    - Today's highest wind gust
- Wind Gust Time: 
    - Time of today's highest wind gust
- Wind Speed: 
    - Current wind speed
- Wind Speed (10 min. Average):
    - 10 minutes average wind speed
- Wind Speed (Average):
    - Average wind speed, based on Archive Interval [^4]
- Wind Speed (Bft): 
    - Wind Speed (Average) in Beaufort

Diagnostic entities:
- Archive Interval: 
    - Archive data interval (usual around 10 minutes). [^2]
- Battery Voltage: 
    - Current battery voltage
- Elevation:
    - Elevation read from the console
- Latitude:
    - Latitude read from the console
- Last Error Message: 
    - Last error message, if no error then empty
- Last Error Time: 
    - Last error time
- Last Fetch Time: 
    - Last fetch time
- Last Success Time: 
    - Last success time
- Longitude:
    - Longitude read from the console
- Rain Collector: 
    - Current rain collector setup (0.01", 0.2 mm or 0.1 mm)

The entity information is updated every 30 seconds (default or other value if choosen during setup).

## Actions

The following actions are available:

- Davis Vantage: Set Davis Time
    - Set the time of the Davis weather station
- Davis Vantage: Get Davis Time
    - Get the time of the Davis weather station
- Davis Vantage: Get Raw Data
    - Get the raw, unprocessed data from the last fetch
- Davis Vantage: Get Information
    - Get information about firmware and diagnostics
- Davis Vantage: Set Yearly Rain
    - Change yearly rain in clicks (depending on setup one click =  0.01", 0.2 mm or 0.1 mm)
- Davis Vantage: Set Archive Period
    - Change archive period in minutes (accepted values: 1, 5, 10, 15, 30, 60, 120). WARNING: This will erase all archived data within the console/envoy.
- Davis Vantage: Set Rain Collector
    - Change rain collector (accepted values: 0.01", 0.2 mm or 0.1 mm)


## Known problems

During first setup the communication to the weather station can be a bit tricky, resulting in an error saying the device didn't communicate. Please try again to set it up (can take up to 5 times).

Due to the somewhat unstable hardware interface some communication runs result in an error like "Check ACK: BAD ('\n\r' != '')". This is normal behavior.

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/MarcoGos/davis_vantage?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/MarcoGos/davis_vantage/total?style=flat-square
[release-url]: https://github.com/MarcoGos/davis_vantage/releases

[^1]: If values show as "Unknown" make sure the Davis time is set correctly. You can check this by using action "Davis Vantage: Get Davis Time" and, if necessary, correct it by using action "Davis Vantage: Set Davis Time".

[^2]: The Archive Interval value can be set by action "Davis Vantage: Set Archive Period"

[^3]: Using WeatherLinkIP combined with sending information to weatherlink.com, may cause problems. It is recommended to disable sending information to weatherlink.com for best results.

[^4]: The Wind Direction and Wind Direction (Rose) will be Unknown when the Wind Speed is 0.0. Also the Wind Direction (Average) and Wind Direction (Rose) (Average) will be Unknown when the Wind Speed (Average) is 0.0. As the standard prescribes.

[^5]: As of version 1.5.0 the mean type of Wind Direction is changed. This means the existing long term statistics need to be removed from the database. Home Assistant will generate a repair warning for it.

[commits-shield]: https://img.shields.io/github/commit-activity/y/MarcoGos/davis_vantage.svg?style=for-the-badge
[commits]: https://github.com/MarcoGos/davis_vantage/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40MarcoGos-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/MarcoGos/davis_vantage.svg?style=for-the-badge
[releases]: https://github.com/MarcoGos/davis_vantage/releases
[stats]: https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.davis_vantage.total&style=for-the-badge
