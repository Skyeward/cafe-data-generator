import random

def linear_dropoff():
    attempts = 10000
    total = 0

    drink_count_totals = {}
    drink_count_totals[1] = 0
    drink_count_totals[2] = 0
    drink_count_totals[3] = 0
    drink_count_totals[4] = 0
    drink_count_totals[5] = 0
    
    for i in range(attempts):
        addition = 1

        if random.randrange(0, 10) < 9:
            addition += 1

            if random.randrange(0, 10) < 7:
                addition += 1

                if random.randrange(0, 10) < 5:
                    addition += 1

                    if random.randrange(0, 10) < 3:
                        addition += 1
                    
                        # if random.randrange(0, 10) < 1:
                        #     addition += 1

        total += addition
        drink_count_totals[addition] += 1
    
    print("LINEAR DROPOFF")
    print("average: " + str(float(total) / float(attempts)))
    print("number of 1 drink orders: " + str(drink_count_totals[1]))
    print("number of 2 drink orders: " + str(drink_count_totals[2]))
    print("number of 3 drink orders: " + str(drink_count_totals[3]))
    print("number of 4 drink orders: " + str(drink_count_totals[4]))
    print("number of 5 drink orders: " + str(drink_count_totals[5]))


def homogenous():
    attempts = 500
    total = 0

    drink_count_totals = {}
    drink_count_totals[1] = 0
    drink_count_totals[2] = 0
    drink_count_totals[3] = 0
    drink_count_totals[4] = 0
    drink_count_totals[5] = 0

    for i in range(attempts):
        rndm = random.randrange(1, 6)
        total += rndm
        drink_count_totals[rndm] += 1

    print("HOMOGENOUS")
    print("average: " + str(float(total) / float(attempts)))
    print("number of 1 drink orders: " + str(drink_count_totals[1]))
    print("number of 2 drink orders: " + str(drink_count_totals[2]))
    print("number of 3 drink orders: " + str(drink_count_totals[3]))
    print("number of 4 drink orders: " + str(drink_count_totals[4]))
    print("number of 5 drink orders: " + str(drink_count_totals[5]))

if __name__ == "__main__":
    linear_dropoff()
    print()
    homogenous()