from twisted.internet.defer import ensureDeferred
from scraper import MyTrainScraper, NationalRailScraper
#from station import StationService

#source_station = StationService.get_by_code("NRW")
#destination_station = StationService.get_by_code("KGX")
#if source_station:
#    print(f"Found: {source_station.name} ({source_station.code})")

scraped_tickets = []

__nrscrapper = NationalRailScraper()
scraperfunction = __nrscrapper.run_scrapper(
        ticket_type="oneWay",
        source="NRW",
        destination="KGX",
        leaving_type="DepartingAt",
        leaving_date_time="2025-06-01T07:00:00Z",
        returning_type=None,
        return_date_time=None,
        adults=1,
        children=0,
        railcards=[['YNG', 1]],
    )
async def get_nrscraper():
    scraped_tickets.extend(await scraperfunction)

ensureDeferred(get_nrscraper())

#__mtscrapper = MyTrainScrapper()
#scraped_tickets.extend(__mtscrapper.run_scrapper(
#    ticket_type="oneWay",
#    source="2d7a7a24-6514-4bc5-bf83-ddcba5be0448",
#    destination="85b48392-83cf-4bea-9a80-17c8189b1c06",
#    leaving_type="DepartingAt",
#    leaving_date_time="2025-06-01T07:00:00Z",
#    returning_type=None,
#    return_date_time=None,
#    adults=1,
#    children=0,
#    railcards=[['YNG', 1]],
#))

#print(scraped_tickets)

mindict = {"price": float('inf')}
try:
    for item in scraped_tickets:
        if "price" not in item:
            pass
        elif item["price"] < mindict["price"]:
            mindict = item
except:
    raise ConnectionError("Could not connect to website")

if mindict == {"price": float('inf')}:
    raise ConnectionError("Could not connect to website")
else:
    print(f"This is the cheapest item: {mindict}")
