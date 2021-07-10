#!/usr/bin/env python3
import logging
import signal
from tracker import Tracker
from tracker_config_pb2 import TrackerConfig, Color

if __name__ == "__main__":
  logging.basicConfig(level=logging.NOTSET)
  
  tracker_config = TrackerConfig()
  tracker_config.northbound_station_stop_id = '1_55778'
  tracker_config.southbound_station_stop_id = '1_56039'
  tracker_config.display_config.display_width_pixels = 64
  tracker_config.display_config.display_height_pixels = 32
  tracker_config.display_config.daytime_display_brightness = 1.0
  tracker_config.display_config.nighttime_display_brightness = 0.5
  tracker_config.display_config.gpio_slowdown = 4
  tracker_config.display_config.title_color.CopyFrom(Color(r=243, g=139, b=0))
  tracker_config.display_config.north_label_color.CopyFrom(Color(r=255, g=0, b=0))
  tracker_config.display_config.south_label_color.CopyFrom(Color(r=255, g=255, b=255))
  tracker_config.display_config.predicted_time_color.CopyFrom(Color(r=52, g=168, b=83))
  tracker_config.display_config.scheduled_time_color.CopyFrom(Color(r=170, g=170, b=170))
  tracker_config.display_config.no_arrivals_color.CopyFrom(Color(r=170, g=170, b=170))

  tracker = Tracker(tracker_config)

  stop_tracker = lambda *args: tracker.stop()

  signal.signal(signal.SIGINT, stop_tracker)
  signal.signal(signal.SIGTERM, stop_tracker)

  tracker.start()
