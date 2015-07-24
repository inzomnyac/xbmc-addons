# Introduction #

All the information processed by Weather Plus can be accessed through Infolabels of the **weather window**.

_(Weather.Location, Weather.Conditions, Weather.FanartCode no longer available)_

example) Current temperature = $INFO[[Window(Weather).Property(Current.Temperature)]]

# Properties #

_FanartCode is usually used for animated icons. (folder name)_

## Default Properties ##

These are standard properties of XBMC.

| **Property** | **Content (Eden)** | **Content (Dharma)** |
|:-------------|:-------------------|:---------------------|
|Locations     |number of configured locations|_same_                |
|Location%d    |name of location (%d=1,2,3,...)|_same_                |
|Location      |name of current location|_same_                |
|Updated       |last update time    |_same_                |
| WeatherProvider |name of weather provider|_same_                |
|Current.Condition|current weather condition in words|_same_                |
|Current.Temperature|current temperature |_same_                |
|Current.FeelsLike|current feels like temperature|_same_                |
|Current.Wind  |current wind converted by XBMC (From DIRECTION at SPEED)|_same (converted by addon)_|
|Current.WindDirection|current wind direction|_N/A_                 |
|Current.OutlookIcon|path of current condition icon|_same_                |
|Current.FanartCode|number of current condition icon|_same_                |
|Current.Humidity|current humidity    |_same_                |
|Current.DewPoint|current dew point   |_same_                |
|Current.UVIndex|current UV index    |_same_                |

## Weather-Plus-Only Properties ##

These are properties provided only by Weather Plus.

_(Another weather addon may have same names of properties.)_

### Current Weather Information ###

| **Property** | **Content** |
|:-------------|:------------|
|Current.Pressure|current pressure|
|Current.Visibility|current visibility (distance)|
|Current.Sunrise|today's sunrise time|
|Current.Sunset|today's sunset time|
|Current.ConditionIcon|path of current weather icon (same as Current.OutlookIcon)|

### 36 Hour Forecast ###

%d = (1-3)

| **Property** | **Content** |
|:-------------|:------------|
|36hour.%d.Heading|title of each forecast (Today, Tonight, Tomorrow or Tomorrow Night)|
|36Hour.%d.OutlookIcon|path of outlook icon|
|36Hour.%d.FanartCode|number of outlook icon|
|36Hour.%d.Outlook|Brief Outlook text (e.g., Sunny)|
|36Hour.%d.TemperatureColor|"low" or "high"|
|36Hour.%d.TemperatureHeading|"Low or "High" in localized string|
|36Hour.%d.Temperature|predicted lowest or highest temperature|
|36Hour.%d.Precipitation|chance(%) of precipitation|
|36Hour.%d.Forecast|detailed forecast in text|
|36Hour.%d.DaylightTitle|"Sunrise" or "Sunset" in localized string|
|36Hour.%d.DaylightTime|sunrise or sunset time|
|36Hour.%d.DaylightType|"sunrise" or "sunset"|
|36Hour.IsFetched|"true" if 36 hour forecast information has been fetched|

### Extended Forecast (up to 10 days) ###

%d = (1,2,...,up to 10)

| **Property** | **Content** |
|:-------------|:------------|
|Daily.%d.LongDay|long formation of day in localized string (e.g., Monday)|
|Daily.%d.ShortDay|short formation of day in localized string (e.g., Mon)|
|Daily.%d.LongDate|long formation of date in localized string (e.g., November 27)|
|Daily.%d.ShortDate|short formation of date in localized string (e.g., Nov 27)|
|Daily.%d.OutlookIcon|path of outlook icon|
|Daily.%d.FanartCode|number of outlook icon|
|Daily.%d.Outlook|brief outlook|
|Daily.%d.HighTemperature|predicted highest temperature|
|Daily.%d.LowTemperature|predicted lowest temperature|
|Daily.%d.Precipitation|chance(%) of precipitation|
|Daily.%d.WindDirection|wind direction (e.g., From North or North)|
|Daily.%d.WindSpeed|wind speed (e.g., 15 mph)|
|Daily.%d.ShortWindDirection|short formation of wind direction (e.g., NW)|
|Daily.IsFetched|"true" if extended forecast information has been fetched|

### Hourly Forecast ###

%d = (1,2,...,up to 12)

| **Property** | **Content** |
|:-------------|:------------|
|Hourly.%d.Time| time        |
|Hourly.%d.LongDate| long formation of date in localized string|
|Hourly%d.ShortDate| short formation of date in localized string|
|Hourly.%d.OutlookIcon| path of outlook icon|
|Hourly.%d.FanartCode| number of outlook icon|
|Hourly.%d.FeelsLike| feels like temperature|
|Hourly.%d.Temperature| temperature |
|Hourly.%d.Outlook| brief outlook|
|Hourly.%d.Precipitation|chance(%) of precipitation|
|Hourly.%d.Humidity|humidity     |
|Hourly.%d.WindDirection|wind direction|
|Hourly.%d.WindSpeed|wind speed   |
|Hourly.%d.ShortWindDirection|short formation of wind direction|
|Hourly.%d.Sunrise|sunrise time (Weather.com only)|
|Hourly.%d.Sunset|sunset time (Weather.com only)|
|Hourly.IsFetched|"true" if hourly forecast information has been fetched|

### Weekend Forecast ###

%d = (1=Friday, 2=Saturday, 3=Sunday)

| **Property** | **Content** |
|:-------------|:------------|
|Weekend.%d.Date| short formation of date |
|Weekend.%d.OutlookIcon| path of outlook icon|
|Weekend.%d.FanartCode| number of outlook icon|
|Weekend.%d.HighTemperature| highest temperature |
|Weekend.%d.LowTemperature| lowest temperature |
|Weekend.%d.Outlook| brief outlook|
|Weekend.%d.Precipitation|chance(%) of precipitation|
|Weekend.%d.Humidity|humidity     |
|Weekend.%d.UV |UV index     |
|Weekend.%d.Wind|current wind (From DIRECTION at SPEED) |
|Weekend.%d.ShortWindDirection|short formation of wind direction|
|Weekend.%d.Sunrise|sunrise time |
|Weekend.%d.Sunset|sunset time  |
|Weekend.%d.Forecast| detailed forecast in text|
|Weekend.%d.ObservedPrecipitation| observed precipitation amount|
|Weekend.%d.ObservedAvgHighTemperature| average highest temperature |
|Weekend.%d.ObservedAvgLowTemperature| average lowest temperature|
|Weekend.%d.ObservedAvgRecordTemperature| recorded highest temperature |
|Weekend.%d.ObservedAvgRecordTemperature| recorded lowest temperature |
|Weekend.%d.DepartureHigh|departure from normal, high|
|Weekend.%d.DepartureHighColor|"low" or "high"|
|Weekend.%d.DepartureLow|departure from normal, low|
|Weekend.%d.DepartureLowColor|"low" or "high"|
|Weekend.%d.Observed| "Observed:" if the information is from observed data, empty otherwise|
|Weekend.%d.ObservedPrecipitation|chance(%) of precipitation|
|Weekend.IsFetched|"true" if weekend forecast information has been fetched|

### Map ###

%c = (1-3), %d = (1-30)

| **Property** | **Content** |
|:-------------|:------------|
|Weather.CurrentMapUrl|url of current selected map|
|Weather.CurrentMap|label of current selected map|
|MapList.%c.MapLabel.%d|label of map |
|MapList.%c.MapIcon.%d|name of map pack icon|
|MapList.%c.MapOnClick.%d|

&lt;onclick&gt;

 for when selected|
|MapList.%c.LongTitle|long name of map category in localized string|
|MapList.%c.ShortTitle|short name of map category in localized string|
|MapStatus     |"loading", "error" or "loaded"|
|MapPath       |path of map images|
|LegendPath    |"weather.com plus/loading", "weather.com/error" or actual downloaded map images|

### Video ###

%d = (1-3)

| **Property** | **Content** |
|:-------------|:------------|
|Video         |url of video #1|
|Video.%d      |url of video #%d|
|Video.%d.Title|title of video #%d, empty if none|

### Alerts ###

| **Property** | **Content** |
|:-------------|:------------|
|Alerts        |detailed alert in text, empty if none|
|Alerts.RSS    |brief alert message, use with a fade label. must have a colors/defaults.xml with this name (rss\_headline)|
|Alerts.Color  |color you may use. must have a colors/defaults.xml with these names(red, orange, yellow, green, default)|
|Alerts.Count  |number of alerts if more than one alert, otherwise empty|
|Alerts.Label  |script localized string (Alert or Alerts)|