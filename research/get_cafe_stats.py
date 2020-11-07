import csv


def define_file_list():
    files = []
    files.append("aberdeen_11-10-2020_19-49-26.csv")
    files.append("chesterfield_05-11-2020_14-04-23.csv")

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


def print_stats(file_name, file_text_line_list):
    #HEADER WITH FILE NAME
    print("-----")
    print(file_name.replace("data_files/", ""))
    print("-----")

    number_of_orders = 0
    number_of_drink_purchases = 0
    number_of_large = 0
    number_of_regular = 0
    
    #NUMBER OF ORDERS AND DRINK PURCHASES
    number_of_orders = len(file_text_line_list)

    drink_count = 0

    for line in file_text_line_list:
        drink_count += line[3].count(".") #[3] is purchases, and all drink prices contain a dot, thus finding drink count

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

    for line in file_text_line_list:
        order_time = line[0].split(" ")[1]
        hours_and_minutes = order_time.split(":")
        minutes_total = (int(hours_and_minutes[0]) * 60) + int(hours_and_minutes[1])
        minutes_total_after_opening = minutes_total - opening_time_minutes_total
        half_hour_time_period = int(minutes_total_after_opening / 30)

        drink_count = line[3].count(".")

        if half_hour_time_period in counts_per_half_hour:
            counts_per_half_hour[half_hour_time_period] += drink_count
        else:
            counts_per_half_hour[half_hour_time_period] = drink_count
    
    counts_per_half_hour_formatted_times = {}

    for key, value in counts_per_half_hour.items():
        time_period_start_minutes_total = opening_time_minutes_total + (key * 30)
        time_period_hour = str(int(time_period_start_minutes_total / 60))
        time_period_minutes = str(time_period_start_minutes_total % 60)

        if len(time_period_minutes) == 1:
            time_period_minutes = "0" + time_period_minutes

        formatted_time = str(time_period_hour) + ":" + str(time_period_minutes)

        counts_per_half_hour_formatted_times[formatted_time] = value



    #PRINTING STATS
    print("number of orders: " + str(number_of_orders))
    print("number of individual drinks purchased: " + str(number_of_drink_purchases))
    print()
    print("number of Large drinks: " + str(number_of_large))
    print("number of Regular drinks: " + str(number_of_regular))
    print()
    print("cafe opens at " + first_order_time)
    print()

    for period, count in counts_per_half_hour_formatted_times.items():
        print("drinks sold during the 30 minutes beginning at " + period + " - " + str(count))

    print()
    print("-----")
    print()
    print()


if __name__ == "__main__":
    print()
    
    files = define_file_list()

    for file_ in files:
        text = get_raw_text(file_)
        print_stats(file_, text)