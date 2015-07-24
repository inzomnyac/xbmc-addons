# Frequently asked questions #

## Map Pack ##

### "What is the Map Pack?" ###
It's a package of thumbnail images of maps.

### "Do I need it?" ###
It'll appear as a map thumbnail when choosing a map.

If you don't have the map pack, you will see just blank or default images.

However, if your skin doesn't have a map selection panel, you **definitely don't** need it.

### "How can I get this?" ###

Settings > Weather > Settings > General tab -> Install Map Pack > Select size -> Choose a path you want to install it -> That's it!

## Icons ##

### "I don't see current weather icon.",  "I don't see animated icons." ###
There are two possibilities.

  * Your skin's issue
  * Addon's bug

First of all, you can ask a skinner developing and maintaining your skin by posting a question to the [XBMC forum](http://forum.xbmc.org).

If it's revealed that it's not skin's issue, you can post your problem to the [Weather Plus thread](http://forum.xbmc.org/showthread.php?t=95329).

(In case of Dharma) : If you'd like to explore xml files of your skin and you're willing to modify something in those, try to find and remove "Weather.IsFetched". And give one more try to find "$INFO[Window(weather).Property(Current.Temperature)]" and add  "$INFO[System.TemperatureUnits]" in the end.


## Unit (Metric vs. English) ##

### "How can I get temperatures in Fahrenheit or Celsius?" ###

Temperature unit depends on XBMC's international region setting.

Settings > Appearance > International > Region > Set where you live