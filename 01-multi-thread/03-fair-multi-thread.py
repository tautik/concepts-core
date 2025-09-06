# now we need to ensure each thread will be fair and takes equal time to process

import math
from threading import Lock
import time
import threading


MAX_INT = 100_00_000
CONCURRENCY = 10
total_prime_numbers = 0
lock = Lock()
current_num = 3
num_lock = Lock()

def check_prime(x):
    global total_prime_numbers
    if x % 2 == 0:
        return
    for i in range (3, int(math.sqrt(x))+1, 2):
        if x % i == 0:
            return

    with lock:
        total_prime_numbers += 1



def do_work(name):
    start = time.time()

    global current_num

    # we want this loop to keep on running and keep checking when the current num 
    while True:
        with num_lock:
            if current_num > MAX_INT:
                break;
            
            num_to_check = current_num
            current_num += 2
        
        check_prime(num_to_check)

    elapsed = time.time() - start
    print(f"Thread {name}: Completed in {elapsed} seconds")


def main():
    global total_prime_numbers
    total_prime_numbers = 1 # 2 is a prime
    start = time.time()
    threads = []
    # our job is to let these threads run in a fair way in terms of equal time per thread

    for i in range(CONCURRENCY):
        thread = threading.Thread(target=do_work, args=(str(i)))
        thread.start()
        threads.append(thread)
    

    for thread in threads:
        thread.join()

    
    elapsed = time.time() - start
    print(f"Checking till {MAX_INT}, found {total_prime_numbers} prime numbers and took {elapsed} seconds")




if __name__ == "__main__":
    main()