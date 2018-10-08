import scrapy
from pprint import pformat
from scrapy.pipelines.images import ImagesPipeline
from services.mail_sender import ScrapyMailSender
from sqlalchemy.exc import IntegrityError
from models import Session, Hotel, Room, RoomConditions


class BookingPipeline(object):
    def __init__(self, stats):
        self.stats = stats
        self.errors = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def open_spider(self, spider):
        self.session = Session()

    def process_item(self, item, spider):
        new_hotel = Hotel(**item)
        self.session.add(new_hotel)
        new_hotel.rooms = self.add_rooms(item)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            old_hotel = self.session.query(Hotel).filter_by(name=new_hotel.name).first()
            old_hotel.update(new_hotel)
            self.session.commit()
        return item

    def add_rooms(self, item):
        rooms = []
        if item['room_kinds']:
            for room_item in item['room_kinds']:
                room = Room(**room_item)
                room.conditions = self.add_conditions(room_item)
                rooms.append(room)
        return rooms

    def add_conditions(self, room_item):
        conditions = []
        if room_item["conditions"]:
            for condition in room_item["conditions"]:
               conditions.append(RoomConditions(**condition))
        return conditions

    def close_spider(self, spider):
        stats = f"Dumping Scrapy stats:\n{pformat(self.stats.get_stats())}\nspider: {spider}\n"
        mailer = ScrapyMailSender()
        mailer.send_email(data=stats)


class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['room_kinds']:
            for room in item['room_kinds']:
                if room['image_url']:
                    yield scrapy.Request(room['image_url'])

    def item_completed(self, results, item, info):
        if item['room_kinds']:
            for room in item['room_kinds']:
                for res in results:
                    if res[0]:
                        if room["image_url"] == res[1]["url"]:
                            room["image"] = res[1]["path"]
                            break
                else:
                    room["image"] = None
        return item
