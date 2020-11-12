import requests
import csv
import json
import yaml
import datetime
import random


def main():
    #READ FROM SETTINGS AND CONFIG YAML FILES
    settings = get_formatted_settings()
    cafe_config = get_cafe_config(settings)
    print(cafe_config["name"])

    #GENERATING RANDOM CSV DATA
    date_as_string = get_date_today()
    order_times, order_count = get_order_times(cafe_config)
    fnames, lnames = get_random_names(order_count, True) #to bypass the API, set second argument to True
    purchases, total_prices = get_random_purchases(cafe_config, order_times, order_count)
    payment_types = get_random_payment_types(cafe_config, order_count)
    payment_dict = assign_card_numbers(payment_types)
    assign_card_numbers(payment_types)

    #BUILDING CSV WITH GENERATED DATA
    data_dict = build_dictionary(date_as_string, order_times, fnames, lnames, purchases, total_prices, payment_dict)
    create_csv_file(cafe_config, data_dict, order_count)


def get_formatted_settings():
    settings = yaml.safe_load(open("settings.yaml"))

    if settings["use_custom_location"] == "true":
        settings["use_custom_location"] = True
    elif settings["use_custom_location"] == "false":
        settings["use_custom_location"] = False
    elif settings["use_custom_location"] != True and settings["use_custom_location"] != False:
        print("SETTINGS.YAML ERROR: use_custom_location should be set to True or False")
        exit()

    if type(settings["custom_location"]) == str:
        settings["custom_location"] = settings["custom_location"].lower()
    else:
        print("SETTINGS.YAML ERROR: use_custom_location should be set to True or False")
        exit()

    return settings


def get_cafe_config(settings):
    configs = yaml.safe_load_all(open("storeConfig.yaml")) 
    configs_as_list = list(configs) #safe_load_all() returns a <generator>
    
    if settings["use_custom_location"] == True:
        location = settings["custom_location"]

        for config in configs_as_list:
            if config["name"].lower() == location:
                return config
    else:
        config_count = len(configs_as_list)
        random_index = random.randrange(0, config_count)
        random_config = configs_as_list[random_index]
        return random_config
    

def get_date_today(): #TODO: add a mode that allows for a manual date to be entered
    date_today = str(datetime.date.today())
    split_date_today = date_today.split("-")

    formatted_date_today = f"{split_date_today[2]}/{split_date_today[1]}/{split_date_today[0]}"
    return formatted_date_today


def get_order_times(config):
    order_frequencies = config["frequency"]
    frequencies_with_start_times_seconds_after_midnight = get_frequencies_with_times_in_seconds(order_frequencies)

    open_time = config["open_time"]
    close_time = config["close_time"]
    open_time_seconds_after_midnight, close_time_seconds_after_midnight = convert_open_close_times_to_seconds(open_time, close_time)

    order_times = []
    current_time_period_start = open_time_seconds_after_midnight

    while current_time_period_start < close_time_seconds_after_midnight:
        new_order_times, current_time_period_start = get_order_times_one_hour(current_time_period_start, frequencies_with_start_times_seconds_after_midnight)
        order_times += new_order_times

    formatted_order_times = format_order_times(order_times)
    order_count = len(formatted_order_times)

    return formatted_order_times, order_count


def get_frequencies_with_times_in_seconds(order_frequencies):
    frequencies_with_start_times_seconds_after_midnight = {}
    
    for start_time, order_frequency in order_frequencies.items():
        hours = str(start_time)[:2] #times formatted in config like 1210; this slices off the minutes
        seconds = int(hours) * 3600
        frequencies_with_start_times_seconds_after_midnight[seconds] = order_frequency

    return frequencies_with_start_times_seconds_after_midnight


def convert_open_close_times_to_seconds(open_time, close_time):
    open_time_hours = int(open_time / 100)
    open_time_minutes = open_time % 100

    close_time_hours = int(close_time / 100)
    close_time_minutes = close_time % 100

    open_time_seconds_after_midnight = (open_time_hours * 3600) + (open_time_minutes * 60)
    close_time_seconds_after_midnight = (close_time_hours * 3600) + (close_time_minutes * 60)

    return open_time_seconds_after_midnight, close_time_seconds_after_midnight


def get_order_times_one_hour(start_time_in_seconds, frequencies):
    # Time periods all end on the oclock. However, some time periods start after the hour.
    # In these cases, the time period will be less than an hour.
    # The code below adds an hour and then truncates the minutes by rounding down to the nearest hour.
    # Both 8:00am and 8:15am would result in an end time of 9:00am
    ONE_HOUR_IN_SECONDS = 3600

    start_time_seconds_after_oclock = start_time_in_seconds % ONE_HOUR_IN_SECONDS
    start_time_rounded_down_to_oclock = start_time_in_seconds - start_time_seconds_after_oclock
    end_time_in_seconds = start_time_rounded_down_to_oclock + ONE_HOUR_IN_SECONDS

    # Time periods should try to use the frequency value from the rounded down hour.
    # If unavailable, it should use the last frequency in the config.
    if start_time_rounded_down_to_oclock in frequencies:
        order_count = frequencies[start_time_rounded_down_to_oclock]
    else:
        time_period_starts_in_seconds = tuple(frequencies.keys())
        last_time_period_start = max(time_period_starts_in_seconds)
        order_count = frequencies[last_time_period_start]

    gap_between_orders_in_seconds = float(ONE_HOUR_IN_SECONDS) / float(order_count)
    current_time_in_seconds = start_time_in_seconds
    order_times = []

    while current_time_in_seconds < end_time_in_seconds:
        order_times.append(current_time_in_seconds)
        current_time_in_seconds += gap_between_orders_in_seconds

    return order_times, int(current_time_in_seconds)


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


def get_random_names(order_count, debug_mode = False):
    if debug_mode == True:
        return get_debug_names(order_count)
    else:
        return get_names_from_api(order_count)
    

def get_names_from_api(name_count_to_get):
    request_count = name_count_to_get * 3 #some names are unsuitable, grabs 3x the name count needed from the API to compensate
    people_list = send_api_request(request_count)

    fnames = []
    lnames = []

    for person_info in people_list:
        name_dict = person_info["name"]
        fname = name_dict["first"]
        lname = name_dict["last"]

        if fname.isalpha() == False or lname.isalpha() == False:
            continue
        elif len(fname) < 3 or len(lname) < 3:
            continue
        elif all(ord(c) < 128 for c in fname) == False or all(ord(c) < 128 for c in lname) == False:
            continue
        else:
            fnames.append(fname)
            lnames.append(lname)

        if len(fnames) == name_count_to_get:
            break

    if len(fnames) < name_count_to_get:
        print("NOT ENOUGH NAMES GATHERED FROM THE API!")
        exit()

    return fnames, lnames


def send_api_request(request_count):
    try:
        api_url = f"https://randomuser.me/api/?results={str(request_count)}"
        response = requests.get(api_url)
        response_as_json = response.json()
        people_list = response_as_json["results"]
        return people_list
    except:
        print("THERE HAS BEEN A PROBLEM WITH THE API REQUEST. THE RESPONSE BODY IS AS FOLLOWS:")
        response.encoding = 'utf-8'
        print(response.text)
        exit()


def get_debug_names(order_count):
    fnames = []
    lnames = []

    for i in range(order_count):
        fnames.append("Alan")
        lnames.append("Smithee")

    return fnames, lnames


def get_random_purchases(random_cafe_config, order_times, order_count):
    config_drink_info = random_cafe_config["menu_probability_weights"]
    drink_menu = get_drink_info()
    drink_weightings = get_drink_weightings(drink_menu, config_drink_info)
    
    purchases = []
    total_prices = []

    for i in range(order_count):
        random_drink_count = random.randrange(1, 6)

        random_drinks = random.choices(drink_menu["name"], weights = drink_weightings, k = random_drink_count)
        drink_sizes, drink_prices = get_sizes_and_prices_of_drinks(random_drinks, drink_menu)

        total_price = 0

        for price in drink_prices:
            total_price += int(price.replace(".", ""))

        full_purchase_string = concat_purchase_strings(random_drinks, drink_sizes, drink_prices)
        purchases.append(full_purchase_string)
        total_prices.append(total_price)

    total_prices_as_decimal_strings = format_total_prices(total_prices)

    return purchases, total_prices_as_decimal_strings


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


def get_drink_weightings(drink_menu, config_drink_info):
    DEFAULT_DRINK_WEIGHTING = 100
    drink_weightings = []

    for drink in drink_menu["name"]:
        if drink in config_drink_info:
            drink_weighting = config_drink_info[drink]
            drink_weightings.append(drink_weighting)
        else:
            drink_weightings.append(DEFAULT_DRINK_WEIGHTING)
    
    return drink_weightings


def get_sizes_and_prices_of_drinks(drink_list, drink_menu):
    drink_sizes = []
    drink_prices = []

    for drink in drink_list:
        drink_index = drink_menu["name"].index(drink)
        drink_has_size = drink_menu["is_sized"][drink_index]

        if drink_has_size == "True":
            random_drink_size = random.choice(["Large", "Regular"])
        else:
            random_drink_size = None

        if random_drink_size == "Large":
            drink_price = drink_menu["large_price"][drink_index]
        else:
            drink_price = drink_menu["regular_price"][drink_index]

        drink_sizes.append(random_drink_size)
        drink_prices.append(drink_price)

    return drink_sizes, drink_prices


def concat_purchase_strings(drink_names, drink_sizes, drink_prices):
    return_string = ""

    for i in range(len(drink_names)):
        if drink_sizes[i] != None:
            return_string += drink_sizes[i]
        
        return_string += " " #because the csv files has a bug where leading spaces exist when the first drink has no size

        return_string += drink_names[i] + " - "
        return_string += drink_prices[i] + ", "

    return return_string[:-2] #slices off final trailing comma and space


def format_total_prices(total_prices):
    formatted_prices = []

    for price in total_prices:
        price_as_string = str(price)
        formatted_price = price_as_string[:-2] + "." + price_as_string[-2:]
        formatted_prices.append(formatted_price)

    return formatted_prices


def get_random_payment_types(config, order_count):
    payment_types = ["CARD", "CASH"]
    payment_weightings = [100]
    
    if "CARD" in config["payment_method_probability_weights"]:
        card_weighting = int(config["payment_method_probability_weights"]["CARD"])
        payment_weightings.insert(0, card_weighting)
    else:
        cash_weighting = int(config["payment_method_probability_weights"]["CASH"])
        payment_weightings.append(cash_weighting)

    payment_types = random.choices(payment_types, weights = payment_weightings, k = order_count)
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
    card_lengths = [13, 14, 15, 16, 17]
    card_length_weightings = [16, 2, 18, 58, 6] # arbitrary numbers based on csv observations
    chosen_card_length_as_list = random.choices(card_lengths, weights = card_length_weightings)
    chosen_card_length = chosen_card_length_as_list[0]

    if chosen_card_length == 16 and random.randrange(0, 3) == 0:
        card_number = "6011" #based on csv observations, appears that 33% of 16 digit numbers start with 6011
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


def create_csv_file(random_cafe_config, dict_, order_count):
    file_name = "output/"
    file_name += random_cafe_config["name"].lower().replace(" ", "_")
    file_name += "_"
    file_name += dict_['date'].replace("/", "-")
    file_name += "_"
    file_name += get_close_time_as_string(random_cafe_config)
    file_name += ".csv"

    csv_lines = []

    for i in range(order_count):
        #number of decimals in a purchase represents the number of drinks, since each drink has one price associated with it (eg 1.50)
        drink_count_in_order = dict_['purchase'][i].count('.')
        
        date_time = dict_['date'] + ' ' + dict_['time'][i] + ','
        full_name = dict_['fname'][i] + ' ' + dict_['lname'][i] + ','
        payment = dict_['payment type'][i] + ',' + dict_['card number'][i]

        #purchases in csv files only have quotes around them when more than one drink is present
        if drink_count_in_order == 1:
            purchase_string = dict_['purchase'][i] + ','
        else:
            purchase_string = '"' + dict_['purchase'][i] + '",'

        csv_line = date_time + random_cafe_config["name"] + ',' + full_name + purchase_string + dict_['total_price'][i] + ',' + payment
        csv_lines.append(csv_line)

    for line in csv_lines:
        print(line)

    with open(file_name, "w") as file_:
            string_to_write = ""
            
            for line in csv_lines:
                string_to_write += f"{line}\n"
        
            file_.write(string_to_write)


def get_close_time_as_string(config):
    close_time = config["close_time"]
    formatted_close_time = str(close_time)[:2] + "-" + str(random.randrange(10, 60)) + "-" + str(random.randrange(10, 60))

    return formatted_close_time


if __name__ == "__main__":
    main()