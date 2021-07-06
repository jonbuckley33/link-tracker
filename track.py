#!/usr/bin/env python3
import onebusaway
import logging
from scrollingdisplay import ScrollingDisplay
import threading
import time

COLUMBIA_CITY_NORTHBOUND_STOP_ID='1_55778'
COLUMBIA_CITY_SOUTHBOUND_STOP_ID='1_56039'
PAINT_FPS = 30
FETCH_FPS = 0.05  # 1 fetch per 20 seconds

def run():
  display = ScrollingDisplay() 
  try:   
    paint_thread = threading.Thread(target=paint, args=(display,), daemon=True)
    update_arrivals_thread = threading.Thread(target=update_arrivals, args=(display,), daemon=True)
    
    paint_thread.start()
    update_arrivals_thread.start()

    while True:
      time.sleep(1.0)
  finally:
    display.clear()

def paint(display):
  while True:
    display.update()
    time.sleep(1.0 / PAINT_FPS)

def update_arrivals(display):
  while True:
    logging.info("fetching arrivals...")
    try:
      northbound_arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_NORTHBOUND_STOP_ID)
      southbound_arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_SOUTHBOUND_STOP_ID)

      logging.info("found %s northbound and %s southbound arrivals" % (len(northbound_arrivals), len(southbound_arrivals)))

      next_northbound_arrival = northbound_arrivals[0] if len(northbound_arrivals) > 0 else None
      next_southbound_arrival = southbound_arrivals[0] if len(southbound_arrivals) > 0 else None
      
      display.set_next_arrivals(next_northbound_arrival, next_southbound_arrival)
    except Exception:
      logging.exception("failed to fetch arrivals")
    finally:
      time.sleep(1.0 / FETCH_FPS)


if __name__ == "__main__":
  logging.basicConfig(level=logging.NOTSET)
  run()