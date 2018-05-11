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
		result_urls = ['https://www.yelp.com/search?find_desc=indian&find_loc=10001&start=' + str(x) for x in range(0, 2, 10)]

		# Yield the requests to different search result urls, 
		# using parse_result_page function to parse the response.
		for url in result_urls:
			yield Request(url=url, callback=self.parse_result_page)

	def parse_result_page(self, response):
		# This function parses the search result page

		# We are looking for the url of the detail page
		restaurant_urls_ending = response.xpath('//a[@class="biz-name js-analytics-click"]/@href').extract()[1:]
		
		# Manually concatenate all the urls
		restaurant_urls = ['https://www.yelp.com' + url for url in restaurant_urls_ending]

		# Yield the requests to the restaurant pages,
		# using parse_restaurant_page function to parse the response
		for url in restaurant_urls:
			yield Request(url=url, callback=self.parse_restaurant_page, meta = {
				'current_url':url
				})

	def parse_restaurant_page(self, response):
		current_url = response.meta['current_url']
		# so we can append
		truncated_url = re.search('^[^?]+', current_url)[0]
		# Find the total number of reviews so that we can decide how many urls to scrape next
		text = response.xpath('//span[@class = "review-count rating-qualifier"]/text()').extract_first()
		#total = map(lambda x: int(x), re.findall('\d+', text))
		total = int(re.findall('\d+', text)[0])
		restaurant_review_urls = [truncated_url + '?start=' + str(x) for x in range(0, 2, 20)]

		# Yield the requests to the restaurant reviews pages,
		# using parse_restaurant_reviews_page function to parse the response
		for url in restaurant_review_urls:
			yield Request(url=url, callback=self.parse_restaurant_reviews_page)

	def parse_restaurant_reviews_page(self, response):
		reviews = response.xpath('//div[@class = "review review--with-sidebar"]')
		restaurant = response.xpath('//div[@class = "biz-page-header-left claim-status"]/div/h1/text()').extract_first().strip()
		# this address is too much and will need to be munged later
		address = response.xpath('//div[@class="mapbox"]//address/text()').extract_first().strip()
		i = 0
		for review in reviews:
			rating = review.xpath('.//div[@class="biz-rating biz-rating-large clearfix"]/div/div/@title').extract_first()[0]
			text = review.xpath('.//p[@lang="en"]/text()').extract()
			date = review.xpath('.//span[@class="rating-qualifier"]/text()').extract_first().strip()

			item = YelpItem()
			item['restaurant'] = restaurant
			item['rating'] = rating
			item['text'] = text
			item['date'] = date
			item['address'] = address
			print(item)
			print(i)
			i += 1
			print('='*50)
			#yield item

















