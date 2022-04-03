from brightnesscalculator import calculate_brightness_from_time
import onebusaway
import logging
from densedisplay import DenseDisplay
import threading
import time

class Tracker:
  def __init__(self, tracker_config):
    self.tracker_config = tracker_config
    self.display = DenseDisplay(tracker_config.display_config)
    self.stopped = threading.Event()

  def start(self):
    paint_thread = threading.Thread(target=self._paint)
    update_arrivals_thread = threading.Thread(target=self._update_arrivals)
    update_brightness_thread = threading.Thread(target=self._update_brightness)
    paint_thread.start()
    update_arrivals_thread.start()
    update_brightness_thread.start()

  def stop(self):
    self.stopped.set()

  def _paint(self):
    while not self.stopped.is_set():
      self.display.update()
      self.stopped.wait(1.0 / self.tracker_config.display_config.paint_fps)

  def _update_arrivals(self):
    while not self.stopped.is_set():
      logging.info("fetching arrivals...")
      try:
        northbound_arrivals = onebusaway.fetch_arrivals(self.tracker_config.northbound_station_stop_id)
        southbound_arrivals = onebusaway.fetch_arrivals(self.tracker_config.southbound_station_stop_id)

        logging.info(f"found {len(northbound_arrivals)} northbound and {len(southbound_arrivals)} southbound arrivals")

        next_northbound_arrival = northbound_arrivals[0] if len(northbound_arrivals) > 0 else None
        next_southbound_arrival = southbound_arrivals[0] if len(southbound_arrivals) > 0 else None
        
        self.display.set_next_arrivals(next_northbound_arrival, next_southbound_arrival)
      except Exception:
        logging.exception("failed to fetch arrivals")
      finally:
        self.stopped.wait(self.tracker_config.depature_fetch_interval_seconds)

  def _update_brightness(self):
    while not self.stopped.is_set():
      try:
        brightness = calculate_brightness_from_time(self.tracker_config)
        logging.info(f"setting brightness level to {brightness}")
        self.display.set_brightness(brightness)
      except Exception:
        logging.exception("failed to calculate and set brightness")
      finally:
        self.stopped.wait(self.tracker_config.display_config.recalculate_brightness_interval_seconds)

    