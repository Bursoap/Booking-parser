import scrapy


class HotelItem(scrapy.Item):
    unique_hotel_id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    country = scrapy.Field()
    stars = scrapy.Field()
    rating = scrapy.Field()
    description = scrapy.Field()
    highlights = scrapy.Field()
    room_kinds = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()



