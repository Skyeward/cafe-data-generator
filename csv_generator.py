import requests
import json
import yaml
import datetime
import random


def generate_csv():
    random_cafe_config = get_random_cafe_config()
    print(random_cafe_config["name"])

    date_as_string = get_date_today()
    order_times = get_order_times(random_cafe_config)
    fnames, lnames = get_random_names()
    purchases = get_random_purchases(random_cafe_config, order_times)
    payment_types = get_random_payment_types(random_cafe_config, len(order_times))
    payment_dict = assign_card_numbers(payment_types)
    assign_card_numbers(payment_types)

    data_dict = build_dictionary(date_as_string, order_times, fnames, lnames, None, None, payment_dict)
    create_csv(data_dict)


#MOVE DOWN FILE
def create_csv(dict_):
    pass


#MOVE DOWN FILE
def build_dictionary(date, times, fnames, lnames, ___, __, payments):
    return_dict = {}
    return_dict["date"] = date
    return_dict["time"] = times
    return_dict["fname"] = fnames
    return_dict["lname"] = lnames
    #purchases
    #total_prices
    return_dict["payment type"] = payments["payment type"]
    return_dict["card number"] = payments["card number"]

    return return_dict


def get_random_cafe_config():
    configs = yaml.safe_load_all(open("storeConfig.yaml"))
    cafe_configs = []

    for config in configs:
        cafe_configs.append(config)

    random_index = random.randrange(0, len(cafe_configs))
    return cafe_configs[0]
    

def get_date_today():
    date_today = str(datetime.date.today())
    split_date_today = date_today.split("-")

    formatted_date_today = split_date_today[2] + "/" + split_date_today[1] + "/" + split_date_today[0]

    return formatted_date_today


def get_random_names():
    name_count_to_get = 20
    request_count = 100
    
    response = requests.get("https://randomuser.me/api/?results=" + str(request_count))
    response_as_json = response.json()
    people_list = response_as_json["results"]

    fnames = []
    lnames = []
    index_to_read = 0

    while len(fnames) < name_count_to_get and index_to_read < request_count:
        name_dict = people_list[index_to_read]["name"]
        fname = name_dict["first"]
        lname = name_dict["last"]
        is_name_valid = True

        if fname.isalpha() == False or lname.isalpha() == False:
            is_name_valid = False
        elif len(fname) < 3 or len(lname) < 3:
            is_name_valid = False
        elif all(ord(c) < 128 for c in fname) == False or all(ord(c) < 128 for c in lname) == False:
            is_name_valid = False
        
        if is_name_valid == True:
            fnames.append(fname)
            lnames.append(lname)

        index_to_read += 1

    try:
        test = fnames[name_count_to_get - 1]
    except:
        print("NOT ENOUGH NAMES GATHERED FROM THE API!")
        print("RESPONSE PRINTED BELOW:")
        print(response_as_json)

    return fnames, lnames


def get_order_times(config):
    frequency_dict = config["frequency"]
    frequency_times_in_seconds = {}

    for time, freq in frequency_dict.items():
        hours = int(time / 100)
        seconds = hours * 3600
        frequency_times_in_seconds[seconds] = freq

    open_time = config["open_time"]
    open_time_hours = int(open_time / 100)
    open_time_minutes = open_time % 100

    close_time = config["close_time"]
    close_time_hours = int(close_time / 100)
    close_time_minutes = close_time % 100

    open_time_seconds_after_midnight = (open_time_hours * 3600) + (open_time_minutes * 60)
    close_time_seconds_after_midnight = (close_time_hours * 3600) + (close_time_minutes * 60)

    current_time_peiod_start = open_time_seconds_after_midnight
    order_times = []

    emergency_break = 0

    while current_time_peiod_start < close_time_seconds_after_midnight and emergency_break < 10000:
        new_order_times, current_time_peiod_start = get_order_times_one_hour(current_time_peiod_start, frequency_times_in_seconds)
        order_times += new_order_times

        emergency_break += 1

    print(order_times)
    print("loops: " + str(emergency_break))

    return format_order_times(order_times)

    #DEBUG PRINTS
    # print(open_time_hours)
    # print(open_time_minutes)
    # print(close_time_hours)
    # print(close_time_minutes)
    # print(open_time_seconds_after_midnight)
    # print(close_time_seconds_after_midnight)


def get_order_times_one_hour(start_time, frequencies):
    starting_seconds_after_oclock = 3600 - (start_time % 3600)
    time_period_end = start_time + starting_seconds_after_oclock

    if time_period_end - 3600 in frequencies:
        order_count = frequencies[time_period_end - 3600]
    else:
        order_count = frequencies[max(tuple(frequencies.keys()))]

    gap_between_orders = float(3600) / float(order_count)
    current_time = start_time
    order_times = []

    emergency_break = 0

    while current_time < time_period_end and emergency_break < 10000:
        order_times.append(current_time)
        current_time += gap_between_orders

        emergency_break += 1

    print("loops: " + str(emergency_break))

    return order_times, int(current_time)


def format_order_times(order_times):
    formatted_times = []
    
    for order_time in order_times:
        total_time_in_minutes = int(order_time / 60)
        hours = int(total_time_in_minutes / 60)
        minutes = total_time_in_minutes % 60

        hours_as_string = "{:02d}".format(hours)
        minutes_as_string = "{:02d}".format(minutes)
        formatted_time = hours_as_string + ":" + minutes_as_string
        print(formatted_time)
        formatted_times.append(formatted_time)

    return formatted_times


def get_random_purchases(random_cafe_config, order_times):
    pass


def get_drink_info():
    drink_dict = {}

    return drink_dict


def get_random_payment_types(config, order_count):
    raw_card_probability = int(config["payment_method_probability_weights"]["CARD"])
    adjusted_card_probability = int(raw_card_probability / 1.63)

    payment_types = []
    card_count = 0 #for debugging
    cash_count = 0

    for i in range(order_count):
        rndm = random.randrange(0, 100 + adjusted_card_probability)
        
        if rndm < 100:
            payment_types.append("CASH")
            cash_count += 1
        else:
            payment_types.append("CARD")
            card_count += 1

    # print(card_count)
    # print(cash_count)

    return payment_types


def assign_card_numbers(payment_types):
    payment_types_and_card_numbers = {}

    types = []
    numbers = []

    for payment_type in payment_types:
        if payment_type == "CASH":
            card_number = ""
        else:
            card_number = generate_random_card_number()

        types.append(payment_type)
        numbers.append(card_number)

    payment_types_and_card_numbers["payment type"] = types
    payment_types_and_card_numbers["card number"] = numbers

    return payment_types_and_card_numbers


def generate_random_card_number():
    #KEYS/VALUES ARE - CARD LENGTH: PERCENT CHANCE
    card_length_percent_weights = {13: 16, 14: 2, 15: 18, 16: 58, 17: 6}
    running_percent_total = 0
    rndm = random.randrange(0, 100)

    for card_length, percent_weight in card_length_percent_weights.items():
        running_percent_total += percent_weight

        if running_percent_total >= rndm:
            chosen_card_length = card_length
            break

    if chosen_card_length == 16 and random.randrange(0, 3) == 0:
        card_number = "6011"
    else:
        card_number = ""

    while card_number < chosen_card_length:
        random_digit = str(random.randrange(0, 10))
        card_number += random_digit

    return card_number


if __name__ == "__main__":
    generate_csv()