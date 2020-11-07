import random

def my_func():
    attempts = 1000

    total = 0
    
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
                    
                        if random.randrange(0, 10) < 1:
                            addition += 1

        total += addition
    
    print(float(total) / float(attempts))


if __name__ == "__main__":
    my_func()