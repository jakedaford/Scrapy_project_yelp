from scrapy import Spider, Request
from yelp.items import YelpItem
import re

class YelpSpider(Spider):
	name = 'yelp_spider'
	allowed_urls = ['https://www.yelp.com/']
	start_urls = ['https://www.yelp.com/search?find_desc=indian&find_loc=10001&start=0']

	def parse(self, response):
		# Find the total number of pages in the result so that we can decide how many urls to scrape next
		text = response.xpath('//span[@class = "pagination-results-window"]/text()').extract_first()
		_, _, total = map(lambda x: int(x), re.findall('\d+', text))
		
		# list comprehension to construct all the urls
		result_urls = ['https://www.yelp.com/search?find_desc=indian&find_loc=10001&start=' + str(x) for x in range(0, total, 10)]

		# Yield the requests to different search result urls, 
		# using parse_result_page function to parse the response.
		for url in result_urls:
			yield Request(url=url, callback=self.parse_result_page)

	def parse_result_page(self, response):
		# This function parses the search result page

		# We are looking for the url of the detail page
		''' NOT DONE WITH THIS YET NEED TO USE GET_ATTRIBUTE TO GRAB THE HREF'''
		restaurant_urls = response.xpath('//a[@class="biz-name js-analytics-click"]')