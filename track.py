#!/usr/bin/env python3
import argparse
from google.protobuf import text_format
import logging
import signal
from tracker import Tracker
from tracker_config_pb2 import TrackerConfig, Color

if __name__ == "__main__":
  logging.basicConfig(level=logging.NOTSET)

  parser = argparse.ArgumentParser(description='Display LINK departure times.')
  parser.add_argument('--config-file', 
    default="/etc/link_tracker/tracker_config.textproto", 
    help='File containing TrackerConfig textproto (default = /etc/link_tracker/tracker_config.textproto)')
  args = parser.parse_args()

  config_file = open(args.config_file, "r")
  tracker_config = text_format.Parse(config_file.read(), TrackerConfig())

  tracker = Tracker(tracker_config)

  stop_tracker = lambda *args: tracker.stop()

  signal.signal(signal.SIGINT, stop_tracker)
  signal.signal(signal.SIGTERM, stop_tracker)

  tracker.start()
