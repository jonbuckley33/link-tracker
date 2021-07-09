from brightnesscalculator import calculate_brightness_from_time
import onebusaway
import logging
from densedisplay import DenseDisplay
import threading
import time

COLUMBIA_CITY_NORTHBOUND_STOP_ID='1_55778'
COLUMBIA_CITY_SOUTHBOUND_STOP_ID='1_56039'
PAINT_FPS = 30
FETCH_FPS = 0.05  # 1 fetch per 20 seconds
UPDATE_BRIGHTNESS_PERIOD_SECONDS = 60

class Tracker:
  def __init__(self):
    self.display = DenseDisplay()
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
      self.stopped.wait(1.0 / PAINT_FPS)

  def _update_arrivals(self):
    while not self.stopped.is_set():
      logging.info("fetching arrivals...")
      try:
        northbound_arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_NORTHBOUND_STOP_ID)
        southbound_arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_SOUTHBOUND_STOP_ID)

        logging.info("found %s northbound and %s southbound arrivals" % (len(northbound_arrivals), len(southbound_arrivals)))

        next_northbound_arrival = northbound_arrivals[0] if len(northbound_arrivals) > 0 else None
        next_southbound_arrival = southbound_arrivals[0] if len(southbound_arrivals) > 0 else None
        
        self.display.set_next_arrivals(next_northbound_arrival, next_southbound_arrival)
      except Exception:
        logging.exception("failed to fetch arrivals")
      finally:
        self.stopped.wait(1.0 / FETCH_FPS)

  def _update_brightness(self):
    while not self.stopped.is_set():
      brightness = calculate_brightness_from_time()
      logging.info("setting brightness level to %d", brightness)
      self.display.set_brightness(brightness)
      self.stopped.wait(UPDATE_BRIGHTNESS_PERIOD_SECONDS)

    