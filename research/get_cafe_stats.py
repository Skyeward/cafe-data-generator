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

    price_count = 0

    for line in file_text_line_list:
        price_count += line[3].count(".") #[3] is purchases, and all drink prices contain a dot, thus finding drink count

    number_of_drink_purchases = price_count

    #FINDING LARGES AND REGULARS
    for line in file_text_line_list:
        number_of_large += line[3].count("Large")
        number_of_regular += line[3].count("Regular")

    #PRINTING STATS
    print("number of orders: " + str(number_of_orders))
    print("number of individual drinks purchased: " + str(number_of_drink_purchases))
    print()
    print("number of Large drinks: " + str(number_of_large))
    print("number of Regular drinks: " + str(number_of_regular))
    print("-----")
    print()
    print()


if __name__ == "__main__":
    files = define_file_list()

    for file_ in files:
        text = get_raw_text(file_)
        print_stats(file_, text)