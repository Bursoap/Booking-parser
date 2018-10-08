import re


def get_num(some_str):
    if some_str:
        number_list = re.findall(r"\d+", some_str)
        if number_list:
            number = number_list.pop(0)
        else:
            number = 0
    else:
        number = 0
    return int(number)


def get_price(price_str):

    num_list = [x for x in filter(lambda x: x.isdigit() or x == "." or x == ",", price_str)]
    result = ''.join(num_list)
    if num_list[-1] == ".":
        num_list = num_list[:-1]

    if len(num_list) >= 3:
        if num_list[-3] == "." or num_list == ",":
            num_list[-3] = "."

        if "," or "." in num_list[:-3]:
            price_first = [x for x in filter(lambda x: x.isdigit(), num_list[:-3])]
            result = ''.join(price_first + num_list[-3:])
    return result


def get_currency(price_str):
    if price_str:
        currency_list = re.findall(r"[a-zA-Z$€£złKč¥руб]", price_str)
        currency = ''.join(currency_list).strip()
    else:
        currency = None
    return currency
