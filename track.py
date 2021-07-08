#!/usr/bin/env python3
import logging
import signal
from tracker import Tracker

if __name__ == "__main__":
  logging.basicConfig(level=logging.NOTSET)
  
  tracker = Tracker()

  stop_tracker = lambda *args: tracker.stop()

  signal.signal(signal.SIGINT, stop_tracker)
  signal.signal(signal.SIGTERM, stop_tracker)

  tracker.start()
