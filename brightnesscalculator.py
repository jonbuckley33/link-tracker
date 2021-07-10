import datetime
import logging
import onebusaway
import pytz
from suntime import Sun

def calculate_brightness_from_time(tracker_config):
  """Calculates what the brightness of the display should be right now [0.0, 1.0]"""
  stop = onebusaway.fetch_stop(tracker_config.northbound_station_stop_id)

  sun = Sun(stop.latitude, stop.longitude)

  now = pytz.utc.localize(datetime.datetime.utcnow())
  today = datetime.date.today()
  sunrise = sun.get_sunrise_time(today)
  # get_sunset_time inexplicably returns the sunset of the previous
  # day, so to get today's sunset, we have to pass in tomorrow.
  tomorrow = today + datetime.timedelta(days=1)
  sunset = sun.get_sunset_time(tomorrow)
 
  is_daytime = now > sunrise and now < sunset
  logging.info("It's currently {} (now = {}; sunrise = {}; sunset = {})"
    .format("daytime" if is_daytime else "nighttime", now, sunrise, sunset))

  if is_daytime:
    return tracker_config.display_config.daytime_display_brightness
  return tracker_config.display_config.nighttime_display_brightness

