import datetime
import logging
import pytz
from suntime import Sun

SEATTLE_LATITUDE = 47.55971
SEATTLE_LONGITUDE = -122.29247

NIGHT_BRIGHTNESS = 50
DAY_BRIGHTNESS = 100

def calculate_brightness_from_time():
  sun = Sun(SEATTLE_LATITUDE, SEATTLE_LONGITUDE)

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
    return DAY_BRIGHTNESS
  return NIGHT_BRIGHTNESS

