import csv


def define_file_list():
    files = []
    files.append("livingston_10-11-2020_17-46-34.csv")
    #files.append("aberdeen_11-10-2020_19-49-26.csv")
    #files.append("chesterfield_05-11-2020_14-04-23.csv")

    files_with_directory = []

    for file_ in files:
        files_with_directory.append("data_files/" + file_)
    
    return files_with_directory


def get_raw_text(filepath):
    line_list = []
    
    with open(filepath, "r") as file_:
        file_reader = csv.reader(file_, quoting = csv.QUOTE_ALL)
        
        for line in file_reader:
            line_list.append(line)

    return line_list


def print_stats(file_name, file_text_line_list, time_period):
    #HEADER WITH FILE NAME
    print("-----")
    print(file_name.replace("data_files/", ""))
    print("-----")

    number_of_orders = 0
    number_of_drink_purchases = 0
    number_of_large = 0
    number_of_regular = 0
    max_drinks_in_single_order = 0

    drink_count_totals = {}
    drink_count_totals[1] = 0
    drink_count_totals[2] = 0
    drink_count_totals[3] = 0
    drink_count_totals[4] = 0
    drink_count_totals[5] = 0

    number_of_card = 0
    number_of_cash = 0

    card_lengths = {}
    card_leading_digits = {}
    card_frequent_digits = {}
    
    #NUMBER OF ORDERS AND DRINK PURCHASES
    number_of_orders = len(file_text_line_list)

    drink_count = 0

    for line in file_text_line_list:
        drinks_in_line = line[3].count(".")
        drink_count += drinks_in_line #[3] is purchases, and all drink prices contain a dot, thus finding drink count
        max_drinks_in_single_order = max(max_drinks_in_single_order, drinks_in_line)
        drink_count_totals[drinks_in_line] += 1

    number_of_drink_purchases = drink_count

    #FINDING LARGES AND REGULARS
    for line in file_text_line_list:
        number_of_large += line[3].count("Large")
        number_of_regular += line[3].count("Regular")

    #FINDING DRINK PURCHASES OVER TIME
    first_order_time = file_text_line_list[0][0].split(" ")[1]
    first_order_time_hours_and_minutes = first_order_time.split(":")
    opening_time_minutes_total = (int(first_order_time_hours_and_minutes[0]) * 60) + int(first_order_time_hours_and_minutes[1])
    counts_per_half_hour = {}
    orders_per_half_hour = {}
    orders_hour_to_hour = {}

    for line in file_text_line_list:
        order_time = line[0].split(" ")[1]
        hours_and_minutes = order_time.split(":")
        minutes_total = (int(hours_and_minutes[0]) * 60) + int(hours_and_minutes[1])
        minutes_total_after_opening = minutes_total - opening_time_minutes_total
        half_hour_time_period = int(minutes_total_after_opening / time_period)

        drink_count = line[3].count(".")

        if half_hour_time_period in counts_per_half_hour:
            counts_per_half_hour[half_hour_time_period] += drink_count
            orders_per_half_hour[half_hour_time_period] += 1
        else:
            counts_per_half_hour[half_hour_time_period] = drink_count
            orders_per_half_hour[half_hour_time_period] = 1

        if hours_and_minutes[0] in orders_hour_to_hour:
            orders_hour_to_hour[hours_and_minutes[0]] += 1
        else:
            orders_hour_to_hour[hours_and_minutes[0]] = 1
    
    counts_per_period_formatted_times = {}
    average_drinks_per_order_per_period = []

    for key, value in counts_per_half_hour.items():
        time_period_start_minutes_total = opening_time_minutes_total + (key * time_period)
        time_period_hour = str(int(time_period_start_minutes_total / 60))
        time_period_minutes = str(time_period_start_minutes_total % 60)

        if len(time_period_minutes) == 1:
            time_period_minutes = "0" + time_period_minutes

        formatted_time = str(time_period_hour) + ":" + str(time_period_minutes)

        counts_per_period_formatted_times[formatted_time] = value
        average_drinks_per_order_per_period.append(float(value) / float(orders_per_half_hour[key]))

    #CARD AND CASH
    for line in file_text_line_list:
        if line[-2] == "CARD":
            number_of_card += 1
        else:
            number_of_cash += 1

    #CARD NUMBERS
    for line in file_text_line_list:
        number = line[-1]
        number_leading_digits = number[:4]
        number_length = len(number)

        if number_leading_digits in card_leading_digits:
            card_leading_digits[number_leading_digits] += 1
        else:
            card_leading_digits[number_leading_digits] = 1

        if number_length in card_lengths:
            card_lengths[number_length] += 1
        else:
            card_lengths[number_length] = 1

        for key, value in card_leading_digits.items():
            if value > 1:
                card_frequent_digits[key] = value


    #PRINTING STATS
    print("number of orders: " + str(number_of_orders))
    print("number of individual drinks purchased: " + str(number_of_drink_purchases))
    print("most drinks in a single order: " + str(max_drinks_in_single_order))
    print()
    print("number of 1 drink orders: " + str(drink_count_totals[1]))
    print("number of 2 drink orders: " + str(drink_count_totals[2]))
    print("number of 3 drink orders: " + str(drink_count_totals[3]))
    print("number of 4 drink orders: " + str(drink_count_totals[4]))
    print("number of 5 drink orders: " + str(drink_count_totals[5]))
    print()
    print("number of Large drinks: " + str(number_of_large))
    print("number of Regular drinks: " + str(number_of_regular))
    print()
    print("cafe opens at " + first_order_time)
    print()
    print(card_lengths)
    print(card_frequent_digits)
    print()

    for period, count in counts_per_period_formatted_times.items():
        print("drinks sold during the " + str(time_period) + " minutes beginning at " + period + " - " + str(count))

    meta_average = 0

    for i in average_drinks_per_order_per_period:
        print("average drinks per order over same time period as above: " + str(i))
        meta_average += i

    meta_average = float(meta_average) / float(len(average_drinks_per_order_per_period)) 

    print()

    for hour, count in orders_hour_to_hour.items():
        print("orders during period starting at " + hour + ":00 - " + str(count))

    print()
    print("overall average drinks per order: " + str(meta_average))

    print()
    print("Number of CARD payments: " + str(number_of_card))
    print("Number of CASH payments: " + str(number_of_cash))
    print()
    print("-----")
    print()
    print()


if __name__ == "__main__":
    print()
    
    files = define_file_list()

    for file_ in files:
        text = get_raw_text(file_)
        sales_time_period = 60
        print_stats(file_, text, sales_time_period)