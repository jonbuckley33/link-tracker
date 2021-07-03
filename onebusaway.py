import datetime
import requests
import time
  
ARRIVALS_AND_DEPARTURES_URL = 'http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/%s.json'
API_KEY='9e3fe27b-c722-4bbf-be38-ad7391dcf21d'
  
class Arrival:
  def __init__(self, json):
    self.num_stops_away = json["numberOfStopsAway"]
    self.eta = datetime.datetime.fromtimestamp(int(json['predictedArrivalTime']) / 1000)
  
  def summary(self):
    return "Estimated arrival time: %s (%s stops away)" % (self.eta.time().strftime("%X"), self.num_stops_away)


def fetch_arrivals(stop_id):
  response = requests.get(url = ARRIVALS_AND_DEPARTURES_URL % stop_id, params = {'key':API_KEY})
  
  data = response.json()

  if data['code'] != 200:
    raise Exception('GET request response is not 200: %s' % data)

  allArrivals = [Arrival(json) for json in data['data']['entry']['arrivalsAndDepartures']]
  futureArrivals = [arrival for arrival in allArrivals if arrival.num_stops_away > 0]

  futureArrivals.sort(key=lambda arrival : arrival.eta)
  return futureArrivals

