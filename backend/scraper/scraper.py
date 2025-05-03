# mytrainticket

from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerProcess
from .spiders.nationalrail import NationalRailSpider
from .spiders.lner import LNERSpider
#from ..station import StationService

#https://www.lner.co.uk/buy-tickets/booking-engine/?cojid=&ocrs=NRW&dcrs=KGX&onlc=7309&dnlc=6121&vcrs=&vnlc=&nvcrs=&nvnlc=&outy=2025&outm=05&outd=16&outh=13&outmi=45&outda=y&JourneyType=returnJourney&ret=y&rety=2025&retm=05&retd=31&reth=15&retmi=45&retda=y&nad=2&nch=1&rc=YNG%2CTST&rcn=1%2C1&tto=n&editJourneyOpen=False&shouldHideJourneyPicker=False&od=Norwich&dd=London+Kings+Cross&cojcbeid=&cojcbeitemnumber=&OriginalJourneyCost=&OriginalTicketClass=&OriginalFareSignature=&OriginalOutboundJourneySignature=&OriginalInboundJourneySignature=&OriginalFareIsFlexiAdvance=&pc=&pat=

def crawler():
	results = []

	def crawler_results(signal, sender, item, response, spider):
		results.append(item)

	dispatcher.connect(crawler_results, signal=signals.item_scraped)
	
	process = CrawlerProcess()
	process.crawl(NationalRailSpider,
		ticket_type="return",
		origin="NRW",
		destination="KGX",
		leavingType="departing",
		leavingYear="2025",
		leavingMonth="05",
		leavingDay="16",
		leavingHour="13",
		leavingMin="45",
		returnType="departing",
		returnYear="2025",
		returnMonth="05",
		returnDay="31",
		returnHour="15",
		returnMin="45",
		adults="2",
		children="1",
		railcards=[["YNG", 1], ["TST", 1]],
		)

	process.start()  # the script will block here until the crawling is finished
	return results

#print(crawler())

#results = []
#for item in processor.run(job):
#	results.append(item)

mindict = {"price": float('inf')}
for item in crawler():
	if item["price"] < mindict["price"]:
		mindict = item
print(mindict)

#print(crawler())
