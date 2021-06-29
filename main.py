import onebusaway

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

if __name__ == "__main__":
  main()