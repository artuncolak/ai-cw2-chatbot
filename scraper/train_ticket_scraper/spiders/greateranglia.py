# ISSUES DOWNLOADING WEBPAGE: ERROR 403

import scrapy
from scrapy_playwright.page import PageMethod
from train_ticket_scraper.items import TicketItem

class GreaterAngliaSpider(scrapy.Spider):
	name = 'greateranglia'

	def start_requests(self):
		url = "https://www.buytickets.greateranglia.co.uk/book/results?origin=urn%3Atrainline%3Ageneric%3Aloc%3ANRW7309gb&destination=urn%3Atrainline%3Ageneric%3Aloc%3AKGX6121gb&outwardDate=2025-04-23T06%3A00%3A00&outwardDateType=departAfter&journeySearchType=single&passengerDiscountCards%5B%5D=eab6a7078be95d5bf04bb0b2a5ddc49efbaca253&passengers%5B%5D=1995-04-08&directSearch=false&transportModes%5B%5D=mixed&selectedOutward=UMLYYxBsfpc%3D%3AhMqksGWYc68%3D"
        # yourneySearchType = ["single","return"]
        # note not open return
        # origin, destination = [...]
        # outwardDateType, inwardDateType = [
            # "departAfter" = Departing after
            # "arriveBefore" = Arriving by
            # ]
        # outwardDate
        # inwardDate
        # selectedTab
        # splitSave
        # directSearch
        # transportModes%5B%5D
        # selectedOutward
        # passengerDiscountCards%5B%5D
        # passengers[]=1995-04-08&passengers[]=2015-04-08&passengers[]=2015-04-08
        # dpiCookieId
        # partnershipType
        # partnershipSelection

        # railcards = [
            # "TSU" = 16-17 Saver
            # "YNG" = 16-25 Railcard
            # "W18" = 18 Saver Transport for Wales
            # "TST" = 26-30 Railcard
            # "NGC" = Annual Gold Card | Gold Record Card
            # "CRC" = Cambrian Railcard
            # "OC5" = Club 50 Web: ScotRail
            # "DRD" = Dales Railcard
            # "DCG" = Devon & Cornwall Gold Card
            # "DCR" = Devon & Cornwall Railcard
            # "DIS" = Disabled Persons Railcard
            # "EVC" = Esk Valley Railcard
            # "FAM" = Family & Friends Railcard
            # "GS3" = GroupSave
            # "HOW" = Heart of Wales Railcard
            # "HRC" = Highland Railcard
            # "HMF" = HM Forces Railcard
            # "JCP" = Jobcentre Plus Travel Discount Card
            # "CUR" = MyCumbria Card
            # "NEW" = Network Railcard
            # "HCC" = North Lincolnshire Concessionary 34%
            # "HCS" = North Lincolnshire Concessionary 50%
            # "PBR" = Pembrokeshire Railcrd
            # "RRC" = Rhondda Railcard
            # "SRN" = Senior Railcard
            # "SSP" = South Yorkshire 16-18 Zoom Travel Pass
            # "WSC" = Student Railcard: Transport for Wales
            # "2TR" = Two Together Railcard
            # "VLS" = Valleys Senior Railcard
            # "VLC" = Valleys Student Railcard
            # "VET" = Veterans Railcard
            # "WYD" = West Yorkshire Disables Concessionary Discount
            # "WMR" = West Yorkshire MetroRover Permit
            # "WYS" = West Yorkshire Senior Concessionary Discount
            # ]|number
		yield scrapy.Request(url=url,
            meta={
            'playwright': True,
            'playwright_page_methods': [
                PageMethod("wait_for_load_state", "domcontentloaded"),
                PageMethod("wait_for_load_state", "networkidle"),
                ]
            })

	def parse(self, response):
		for ticket in response.css('div > div > div > div > div > div > div > div > div > div > div > div > div > ul > li > div'):
			ticket_field = TicketItem()
#			ticket_field['duration'] = ticket.css('div > div > div > button > div > div > div > span > span:first-of-type::text').get()
#			ticket_field['changeovers'] = ticket.css('div > div > div > button > div > div > div > div > button > span::text').get()
#			ticket_field['price'] = ticket.css('div > div > div > fieldset > div > div > div > div > div > label > div > span > span > span::text').get()[1::]
#			ticket_field['leaveTime'] = ticket.css('div > div > div > div > div > div > div > div > div > div > p > time > span::text').get()
			ticket_field['duration'] = "success"

			yield ticket_field
