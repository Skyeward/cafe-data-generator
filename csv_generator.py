import requests
import json
import yaml
from datetime import date


def generate_csv():
    get_random_cafe_config_data()
    #date_as_string = get_date_today()
    #fnames, lnames = get_random_names()


def get_random_cafe_config_data():
    config_data = yaml.load_all(open("storeConfig.yaml"))
    print(config_data)


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


if __name__ == "__main__":
    generate_csv()