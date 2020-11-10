import requests
import csv
import json
import yaml
import datetime
import random


def generate_csv():
    random_cafe_config = get_random_cafe_config()
    print(random_cafe_config["name"])

    date_as_string = get_date_today()
    order_times = get_order_times(random_cafe_config)
    order_count = len(order_times)
    fnames, lnames = get_random_names(order_count)
    purchases, total_prices = get_random_purchases(random_cafe_config, order_times, order_count)
    payment_types = get_random_payment_types(random_cafe_config, order_count)
    payment_dict = assign_card_numbers(payment_types)
    assign_card_numbers(payment_types)

    data_dict = build_dictionary(date_as_string, order_times, fnames, lnames, purchases, total_prices, payment_dict)
    create_csv(random_cafe_config, data_dict, order_count)


def get_close_time_as_string(config):
    close_time = config["close_time"]
    formatted_close_time = str(close_time)[:2] + "-" + str(random.randrange(10, 60)) + "-" + str(random.randrange(10, 60))

    return formatted_close_time


def get_random_cafe_config():
    configs = yaml.safe_load_all(open("storeConfig.yaml"))
    cafe_configs = []

    for config in configs:
        cafe_configs.append(config)

    random_index = random.randrange(0, len(cafe_configs))
    return cafe_configs[random_index]
    

def get_date_today():
    date_today = str(datetime.date.today())
    split_date_today = date_today.split("-")

    formatted_date_today = split_date_today[2] + "/" + split_date_today[1] + "/" + split_date_today[0]

    return formatted_date_today


def get_random_names(order_count):
    name_count_to_get = order_count
    request_count = order_count * 3
    
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

    #print(order_times)
    if emergency_break > 9000:
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

    if emergency_break > 9000:
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
        formatted_times.append(formatted_time)

    return formatted_times


def get_random_purchases(random_cafe_config, order_times, order_count):
    drink_dict = get_drink_info()
    drink_dict["probability"] = []
    
    config_drink_info = random_cafe_config["menu_probability_weights"]
    config_drink_names = list(config_drink_info.keys())
    running_probability = 0

    for drink in drink_dict["name"]:
        if drink in config_drink_names:
            print("matched drink: " + drink)
            running_probability += config_drink_info[drink]
        else:
            running_probability += 100
            
        drink_dict["probability"].append(running_probability)

    purchases = []
    total_prices = []

    for i in range(order_count):
        drink_count = random.randrange(1, 6)
        random_drinks = []
        drink_sizes = []
        drink_prices = []
        total_price = 0
        
        for i in range(drink_count):
            rndm = random.randrange(0, running_probability)
            selected_drink = None
            drink_to_check = 0
            
            while selected_drink == None:
                if rndm < drink_dict["probability"][drink_to_check]:
                    selected_drink = drink_dict["name"][drink_to_check]
                else:
                    drink_to_check += 1

            random_drinks.append(selected_drink)

            if drink_dict["is_sized"][drink_to_check] == "False":
                size = None
            else:
                size = random.choice(["Large", "Regular"])

            drink_sizes.append(size)

            if size == "Large":
                price = drink_dict["large_price"][drink_to_check]
            else:
                price = drink_dict["regular_price"][drink_to_check]

            drink_prices.append(price)
            total_price += int(price.replace(".", ""))

        total_prices.append(total_price)
        purchases.append(concat_purchase_strings(random_drinks, drink_sizes, drink_prices))
    
    total_prices_as_decimal_strings = format_total_prices(total_prices)

    # print(purchases)
    # print(total_prices_as_decimal_strings)

    return purchases, total_prices_as_decimal_strings


def concat_purchase_strings(drink_names, drink_sizes, drink_prices):
    return_string = ""

    for i in range(len(drink_names)):
        if drink_sizes[i] != None:
            return_string += drink_sizes[i]
        
        return_string += " " #because the csv files has a bug where leading spaces exist when the first drink has no size

        return_string += drink_names[i] + " - "
        return_string += drink_prices[i] + ", "

    return return_string[:-2]


def format_total_prices(total_prices):
    formatted_prices = []

    for price in total_prices:
        price_as_string = str(price)
        formatted_price = price_as_string[:-2] + "." + price_as_string[-2:]
        formatted_prices.append(formatted_price)

    return formatted_prices


def get_drink_info():
    drink_dict = {"name": [], "is_sized": [], "regular_price": [], "large_price": []}
    drink_raw_text_rows = []

    with open("drink_info.txt", "r") as file_:
        drinks_file_reader = csv.reader(file_, quoting = csv.QUOTE_ALL)
        
        for drink in drinks_file_reader:
            drink_raw_text_rows.append(drink)

    for row in drink_raw_text_rows:
        drink_dict["name"].append(row[0])
        drink_dict["is_sized"].append(row[1])
        drink_dict["regular_price"].append(row[2])
        drink_dict["large_price"].append(row[3])

    return drink_dict


def get_random_payment_types(config, order_count):
    if "CARD" in config["payment_method_probability_weights"]:
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
    else:
        raw_cash_probability = int(config["payment_method_probability_weights"]["CASH"])
        adjusted_cash_probability = int(raw_cash_probability / 1.63)

        payment_types = []
        card_count = 0 #for debugging
        cash_count = 0

        for i in range(order_count):
            rndm = random.randrange(0, 100 + adjusted_cash_probability)
            
            if rndm < 100:
                payment_types.append("CARD")
                card_count += 1
            else:
                payment_types.append("CASH")
                cash_count += 1

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

    while len(card_number) < chosen_card_length:
        random_digit = str(random.randrange(0, 10))
        card_number += random_digit

    return card_number


def build_dictionary(date, times, fnames, lnames, purchases, total_prices, payments):
    return_dict = {}
    return_dict["date"] = date
    return_dict["time"] = times
    return_dict["fname"] = fnames
    return_dict["lname"] = lnames
    return_dict["purchase"] = purchases
    return_dict["total_price"] = total_prices
    return_dict["payment type"] = payments["payment type"]
    return_dict["card number"] = payments["card number"]

    return return_dict


def create_csv(random_cafe_config, dict_, order_count):
    csv_lines = []

    file_name = "output/"
    file_name += random_cafe_config["name"].lower()
    file_name += "_"
    file_name += dict_['date'].replace("/", "-")
    file_name += "_"
    file_name += get_close_time_as_string(random_cafe_config)
    file_name += ".csv"

    for i in range(order_count):
        date_time = dict_['date'] + ' ' + dict_['time'][i] + ','
        full_name = dict_['fname'][i] + ' ' + dict_['lname'][i] + ','
        payment = dict_['payment type'][i] + ',' + dict_['card number'][i]
        purchase_in_quotes = '"' + dict_['purchase'][i] + '",'
        csv_line = date_time + full_name + purchase_in_quotes + dict_['total_price'][i] + ',' + payment

        csv_lines.append(csv_line)

    for line in csv_lines:
        print(line)

    with open(file_name, "w") as file_:
            string_to_write = ""
            
            for line in csv_lines:
                string_to_write += f"{line}\n"
        
            file_.write(string_to_write)


if __name__ == "__main__":
    generate_csv()