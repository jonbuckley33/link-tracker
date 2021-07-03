#!/usr/bin/env python3
import onebusaway
from rgbdisplay import RgbDisplay
import time

COLUMBIA_CITY_NORTHBOUND_STOP_ID='1_55778'
COLUMBIA_CITY_SOUTHBOUND_STOP_ID='1_56039'

def main():
  northbound_arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_NORTHBOUND_STOP_ID)
  southbound_arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_SOUTHBOUND_STOP_ID)

  print("Northbound arrivals:")
  for arrival in northbound_arrivals:
    print(arrival.summary())

  print("Southbound arrivals:")
  for arrival in southbound_arrivals:
    print(arrival.summary())

  display = RgbDisplay()

  first_line = "Next train north: %s" % northbound_arrivals[0].eta.strftime("%X")
  second_line = "Next train south: %s" % southbound_arrivals[0].eta.strftime("%X")
  display.set_text(first_line, second_line)
  while True:
    display.update()
    time.sleep(0.05)


if __name__ == "__main__":
  main()