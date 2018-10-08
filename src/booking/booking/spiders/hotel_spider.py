import logging

import scrapy
from scrapy import Spider
from items import HotelItem
from services.helpers import get_num, get_currency, get_price
from scrapy.utils.response import open_in_browser


class HotelsSpider(Spider):

    name = "hotels"
    site_url = "https://www.booking.com/"

    def start_requests(self):
        yield scrapy.Request(self.site_url, self.parse)

    def parse(self, response):

        data = {
            "ss": getattr(self, 'location', 'Las Vegas Strip'),
            "checkin_month": getattr(self, 'month_in', '12'),
            "checkin_monthday": getattr(self, 'day_in', '12'),
            "checkin_year": getattr(self, 'year_in', '2018'),
            "checkout_month": getattr(self, 'month_out', '12'),
            "checkout_monthday": getattr(self, 'day_out', '13'),
            "checkout_year": getattr(self, 'year_out', '2018'),
            "no_rooms": getattr(self, 'rooms', '1'),
            "group_adults": getattr(self, 'adults', '2'),
            "group_children": getattr(self, 'children', '0')
        }

        yield scrapy.FormRequest.from_response(
            response=response,
            formid="frm",
            formdata=data,
            callback=self.get_hotels,
        )

    def get_hotels(self, response):

        hotel_paths = response.xpath(
            '//a[contains(@class, "sr_item_photo_link sr_hotel_preview_track")]/@href'
        ).extract()

        for path in hotel_paths:
            yield response.follow(path, callback=self.parse_hotel)

        next_page = response.xpath(
            '//ul[@class="bui-pagination__list"]/li[contains(@class, "pagination__next-arrow")]/a/@href'
        ).extract_first()

        if next_page:
            yield response.follow(next_page, callback=self.get_hotels)

    def parse_hotel(self, response):
        item = HotelItem()

        unique_hotel_id = int(response.xpath(
            '//div[@id="wrap-hotelpage-top"]/form[@id="top-book"]/input[@name="hotel_id"]/@value'
        ).extract_first())

        name = response.xpath(
            '//h2[@id="hp_hotel_name"]/text()'
        ).extract_first().strip()

        stars = get_num(response.xpath(
            '//span[contains(@class, "hp__hotel_ratings__stars")]/i/svg[contains(@class, "bk-icon")]/@class'
        ).extract_first())

        rating = response.xpath(
            '//div[@id="js--hp-gallery-scorecard"]/@data-review-score'
        ).extract_first()

        location_list = response.xpath(
            '//p[@id="showMap2"]/span[contains(@class, "hp_address_subtitle")]/text()'
        ).extract_first().strip().split(',')

        country = location_list.pop().strip()

        address = ', '.join(location_list)

        image_url = response.xpath(
            '//div[@id="photo_wrapper"]//img/@data-highres'
        ).extract_first() or response.xpath(
            '//div[contains(@class, "clearfix")]/div[contains(@class, "grid")]//a/@href'
        ).extract_first() or response.xpath(
            '//div[contains(@class, "clearfix")]/div/a/@href'
        ).extract_first()

        description = ' '.join([x.strip() for x in response.xpath(
            '//div[@id="summary"]/p//text()'
        ).extract()])

        highlights = '; '.join(response.xpath(
            '//div[@id="hotel_main_content"]/div[contains(@class, "hp_hotel_description_hightlights_wrapper")]/div'
            '/div[contains(@class, "hp_desc_important_facilities")]/div/@data-name-en'
        ).extract())

        room_list = response.xpath(
            '//table[contains(@class, "hprt-table")]/tbody/tr/td[contains(@class, "hprt-table-cell-roomtype")]'
        )

        if room_list:
            room_kinds = self.parse_kind_of_rooms(response, room_list)
        else:
            room_kinds = False

        item['unique_hotel_id'] = unique_hotel_id
        item['name'] = name
        item['address'] = address
        item['country'] = country
        item['stars'] = stars
        item['rating'] = rating
        item['description'] = description
        item['highlights'] = highlights
        item['room_kinds'] = room_kinds
        item['image_urls'] = [image_url]

        yield item

    def parse_kind_of_rooms(self, response, room_list):
        rooms = []
        for room in room_list:
            room_id = get_num(room.xpath(
                './div//a[contains(@class, "hprt-roomtype-scroll-target")]/@name'
            ).extract_first())

            room_name = room.xpath(
                './/a/span[contains(@class, "hprt-roomtype-icon-link")]/text()'
            ).extract_first().strip()

            room_image = room.xpath(
                f'//form[@id="hprt-form"]/div[@id="blocktoggleRD{room_id}"]//div[@data-photoid]/img/@data-lazy'
            ).extract_first()

            rooms_desc = '; '.join([x.strip().replace("• ", "") for x in filter(lambda x: x != "\n", room.xpath(
                './/div[contains(@class, "hprt-roomtype-block")]/'
                'div[contains(@class, "hprt-facilities-block")]//'
                'span/text()').extract())]) or None

            room_conditions = self.parse_room_conditions(response, room, room_id)

            if room_conditions:
                rooms.append({
                    'name': room_name,
                    'room_id': room_id,
                    'description': rooms_desc,
                    'conditions': room_conditions,
                    'image_url': room_image
                })

        return rooms

    def parse_room_conditions(self, response, room, room_id):
        room_conditions = []

        room_block_id_list = room.xpath(
            './../../tr/td[contains(@class, "hprt-table-room-select")]/div/label/'
            f'select[@data-room-id="{room_id}"]/@data-block-id'
        ).extract()

        if room_block_id_list:
            for block_id in room_block_id_list:
                if block_id:
                    condition_block = room.xpath(
                        f'./../../tr[@data-block-id="{block_id}" and @data-et-view]'
                    )

                    occupancy = get_num(condition_block.xpath(
                        './td[contains(@class, "hprt-table-cell-occupancy")]/div/'
                        'div[contains(@class, "hprt-occupancy-occupancy-info")]/@data-title'
                    ).extract_first().strip())

                    price_str = condition_block.xpath(
                        './td[contains(@class, "hprt-table-cell-price")]/div/'
                        'div[contains(@class, "hprt-price-price")]/span/text()'
                    ).extract_first().strip()

                    price = get_price(price_str)

                    currency = get_currency(price_str)

                    conditions = '; '.join([x.strip() for x in filter(lambda x: x != "\n", condition_block.xpath(
                        './td[contains(@class, "hprt-table-cell-conditions")]/div/'
                        'ul[contains(@class, "hprt-conditions")]/li/span//text()'
                    ).extract())])

                    room_conditions.append({
                        'block_id': block_id,
                        'occupancy': occupancy,
                        'price': price,
                        'currency': currency,
                        'conditions': conditions
                    })
                else:
                    continue
        return room_conditions

