import requests
import json
import yaml
from datetime import date
import random


def generate_csv():
    random_cafe_config = get_random_cafe_config()
    order_count = get_order_count(random_cafe_config)
    print(random_cafe_config["name"])
    #date_as_string = get_date_today()
    #fnames, lnames = get_random_names()
    get_order_times(random_cafe_config)
    get_random_payment_types(random_cafe_config, order_count)


def get_random_cafe_config():
    configs = yaml.safe_load_all(open("storeConfig.yaml"))
    cafe_configs = []

    for config in configs:
        cafe_configs.append(config)

    random_index = random.randrange(0, len(cafe_configs))
    return cafe_configs[0]


def get_order_count(config):
    frequency_dict = config["frequency"]
    order_count = 0

    for value in frequency_dict.values():
        order_count += value

    return order_count
    

def get_date_today():
    date_today = str(date.today())
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

    open_time = config["open_time"]
    open_time_hours = int(open_time / 100)
    open_time_minutes = open_time % 100
    # open_time_hours = int(open_time[:-2])
    # open_time_minutes = int(open_time[-2:])

    close_time = config["close_time"]
    close_time_hours = int(close_time / 100)
    close_time_minutes = close_time % 100
    # close_time_hours = int(close_time[:-2])
    # close_time_minutes = int(close_time[-2:])

    open_time_seconds_after_midnight = (open_time_hours * 3600) + (open_time_minutes * 60)
    close_time_seconds_after_midnight = (close_time_hours * 3600) + (close_time_minutes * 60)

    current_time_peiod_start = open_time_seconds_after_midnight


    #DEBUG PRINTS
    print(open_time_hours)
    print(open_time_minutes)
    print(close_time_hours)
    print(close_time_minutes)
    print(open_time_seconds_after_midnight)
    print(close_time_seconds_after_midnight)




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

    print(card_count)
    print(cash_count)


if __name__ == "__main__":
    generate_csv()