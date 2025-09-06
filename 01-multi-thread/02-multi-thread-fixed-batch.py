## so we will be writing 3 approaches to showcase how do we write a multi thread safe queue

import time
import math
import threading
from threading import Lock
##Approach 2: using multi threading simple way


MAX_INT=100_00_000
CONCURRENCY = 10
total_prime_numbers = 0
lock = Lock()


def check_prime(x):
    if x%2 == 0:
        return 
    
    for i in range(3, int(math.sqrt(x))+1, 2): # to do it for odd numbers
        if x%i == 0:
            return
    
    with lock:
        global total_prime_numbers
        total_prime_numbers+=1;



def do_batch( name, start_num, end_num):
    start_time = time.time()
    
    for i in range(start_num, end_num+1, 2):
        check_prime(i)

    end_time = time.time()
    total_elapsed = end_time - start_time
    print(f"Thread {name}:  [{start_num}, {end_num}] competed in {total_elapsed:.2f} seconds")

def main():
    global total_prime_numbers
    start = time.time()

    # 2 is a prime
    total_prime_numbers = 1

    #lets create thread
    threads = [] # Empty list to keep the track of our workers
    concurreny = 10
    batch_size = MAX_INT//CONCURRENCY
    current_start = 3 #Start with 3 (first odd number)

    for i in range(CONCURRENCY - 1): # Create the first 0 to 8 WOrkers
        thread = threading.Thread(
            target=do_batch,  # The function each worker will run will be here
            args = (str(i), current_start, current_start+ batch_size)
        )
        threads.append(thread) # Add worker to our list
        thread.start()
        current_start+=batch_size

    thread = threading.Thread(
        target = do_batch,
        args = (str(CONCURRENCY - 1), current_start, MAX_INT)
    )
    threads.append(thread)
    thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    elapsed = time.time() - start
    print(f"Checking till {MAX_INT}, found {total_prime_numbers} prime numbers and took {elapsed} seconds")


if __name__ == "__main__":
    main()
