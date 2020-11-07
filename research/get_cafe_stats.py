import csv


def define_file_list():
    files = []
    files.append("aberdeen_11-10-2020_19-49-26.csv")
    files.append("chesterfield_05-11-2020_14-04-23.csv")
    
    return files


def get_raw_text(filepath):
    line_list = []
    
    with open(filepath, "r") as file_:
        file_reader = csv.reader(file_, quoting = csv.QUOTE_ALL)
        
        for line in file_reader:
            line_list.append(line)

    return line_list


def print_stats(file_, text):
    print(file_)

    #find some stats


if __name__ == "__main__":
    files = define_file_list()

    for file_ in files:
        text = get_raw_text(file)
        print_stats(file_, text)