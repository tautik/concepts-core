## so we will be writing 3 approaches to showcase how do we write a multi thread safe queue

import time
import math

##Approach 1: using seuquential processing (lets estimate the time)

MAX_INT=100_00_000

def check_prime(x):
    global total_prime_numbers
    if x % 2 == 0: # that means its even and even numbers are not prime
        return
    for i in range(3, int(math.sqrt(x))+1, 2): # so here how we are checking is that the number is prime or not by 
        if x % i == 0:
            return
    total_prime_numbers += 1


def main():
    global total_prime_numbers
    start = time.time()

    total_prime_numbers = 1

    for i in range(3, MAX_INT, 2): # Only check odd numbers
        check_prime(i)
    
    end = time.time()
    print(f"CHekcing till {MAX_INT}, found {total_prime_numbers} prime numbers and took {end - start} seconds")

if __name__ == "__main__":
    main()
