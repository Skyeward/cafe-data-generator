import requests
import json


def generate_csv():
    fnames, lnames = get_random_names()


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

    print(fnames)
    print(lnames)

    try:
        test = fnames[name_count_to_get - 1]
    except:
        print("NOT ENOUGH NAMES GATHERED FROM THE API!")
        print("RESPONSE PRINTED BELOW:")
        print(response_as_json)

    return fnames, lnames


if __name__ == "__main__":
    get_random_names()