import onebusaway

COLUMBIA_CITY_NORTHBOUND_STOP_ID='1_55778'
COLUMBIA_CITY_SOUTHBOUND_STOP_ID='1_56039'

def main():
  arrivals = onebusaway.fetch_arrivals(COLUMBIA_CITY_NORTHBOUND_STOP_ID)

  for arrival in arrivals:
    print(arrival.summary())

if __name__ == "__main__":
  main()