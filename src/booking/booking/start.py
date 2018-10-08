import argparse
import datetime
import sys
import env
from googletrans import Translator
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


translator = Translator()


def date_format_test(date_str):

    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d', )
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    else:
        return date


def validate_dates(check_in=None, check_out=None):

    today = datetime.datetime.now().date()
    tomorrow = datetime.datetime.now().date() + datetime.timedelta(days=1)

    if check_in.year not in [today.year, today.year + 1]:
        raise ValueError(f"check-in and check-out dates should be in : {today.year} and {today.year + 1}")
    elif check_out.date() <= check_in.date():
        raise ValueError("check-out date must be more than check-in date")
    elif check_in.date() < today:
        raise ValueError("check-in date can`t be less than today")
    elif check_out.date() < tomorrow:
        raise ValueError("check-out date cant be less tan tomorrow ")
    return check_in, check_out


def validate_location(loc=None):

    allowed = ["`", " ", "-"]
    loc_list = []

    for x in loc:
        if x.isalpha() or x in allowed:
            loc_list.append(x)
        else:
            raise ValueError("location string should contains only letters, dashes and apostrophe")

    dest = ''.join(loc_list)

    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    def get_choice():

        choice = input(f"Your destination is {dest}? [y/n]").lower()

        if choice in yes:
            return dest
        elif choice in no:
            return sys.exit()
        else:
            get_choice()

    return get_choice()


parser = argparse.ArgumentParser()

parser.add_argument("-c", "--country", required=True,
                    help="destination country name")

parser.add_argument("-t", "--town", required=True,
                    help="destination/property name")

parser.add_argument("-i", "--check_in", required=True,
                    help="check-in date format YYYY-MM-DD")

parser.add_argument("-o", "--check_out",  required=True,
                    help="check-out date format YYYY-MM-DD")

parser.add_argument("-r", "--rooms", type=int, default=1, choices=range(1, 30),
                    help="number of rooms")

parser.add_argument("-a", "--adults", type=int, default=2, choices=range(1, 30),
                    help="number of adults")

parser.add_argument("-ch", "--children", type=int, default=0, choices=range(0, 10),
                    help="number of children with you")

parser.add_argument("-p", "--proxy", action="store_true",
                    help="command enable proxy")

args = parser.parse_args()

destination = translator.translate(args.town, dest='en').text + ' ' + translator.translate(args.country, dest='en').text
ss = validate_location(loc=destination)
date_in, date_out = validate_dates(
    check_in=date_format_test(args.check_in),
    check_out=date_format_test(args.check_out)
)

if args.proxy:
    env.PROXY["enable"] = True
else:
    print("Proxy is disable")

arg_dict = {
    "location": ss,
    "year_in": str(date_in.year),
    "month_in": str(date_in.month),
    "day_in": str(date_in.day),
    "year_out": str(date_out.year),
    "month_out": str(date_out.month),
    "day_out": str(date_out.day),
    "rooms": str(args.rooms),
    "adults": str(args.adults),
    "children": str(args.children)
}

process = CrawlerProcess(get_project_settings())
process.crawl('hotels', **arg_dict)
process.start()








