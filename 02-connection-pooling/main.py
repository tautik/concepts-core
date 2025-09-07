# okay so we will discuss about connection pooling - and what is the time difference between creating a new connection and using a connection from the pool
# so vs reusuing the already thing we have created

import threading
import time
import queue
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from time import sleep


class ConnectionPool:
    def __init__(self, database_path, pool_size=10):
        self.database_path = database_path
        self.pool = queue.Queue(maxsize=pool_size) # we are creating a queue with max size as pool size

        # Create initial connections
        for _ in range(pool_size):
            self.pool.put(sqlite3.connect(database_path, check_same_thread=False)) # by default sqlite3 only allows the thread that created it to use this connection, so check_same_thread=False is used to allow other threads to use this connection


    
    def get_connection(self):
        return self.pool.get() # gets the connection from the top of the queue
    
    def release_connection(self, conn):
        self.pool.put(conn) # puts the connection back to the top of the queue

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

        


#lets create the test db
def create_test_db():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("INSERT OR REPLACE INTO users (id, name) VALUES (1, 'John')")
    conn.commit()
    conn.close()

def benchmark_without_pool(num_requests):
    "Each request creates a new connection - SLOW"

    def make_request():
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        return result

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=20) as executor:
        threads = []
        for _ in range(num_requests):
            thread = executor.submit(make_request) # its similar to thread.start()
            threads.append(thread)
        results = []
        for thread in threads:
            results.append(thread.result())

    duration = time.time() - start_time
    print(f"Without pool ({num_requests} requests): {duration:.3f} seconds")
    return duration


def benchmark_with_pool(num_requests, pool_size=10):
    "Each request uses a connection from the pool - FAST"

    pool = ConnectionPool("test.db", pool_size)

    def make_request(thread_name):
        start_time = time.time()
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = 1")
        result = cursor.fetchone()
        pool.release_connection(conn)
        end_time = time.time()

        return result, end_time - start_time

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for i in range(num_requests):
            future = executor.submit(make_request, f"Thread {i}") # its similar to thread.start()
            futures.append(future)
        results = []
        for future in futures:
            results.append(future.result()[0])
            print(f"{future.result()[1]:.3f} seconds")

    duration = time.time() - start_time
    print(f"With pool ({num_requests} requests, pool size {pool_size}): {duration:.3f} seconds")
    
    # Clean up - close all connections
    pool.close_all()
    return duration

        



def main():
    create_test_db()

    print("Test db created successfully")
    print("--------------------------------")

    #Now lets create different benchmarks

    time1 = benchmark_without_pool(20)
    time2 = benchmark_with_pool(100, pool_size=5)
    time3 = benchmark_with_pool(100, pool_size=20)
    
    # Calculate and show improvements
    print(f"\nResults:")
    print(f"Improvement with small pool: {((time1 - time2) / time1 * 100):.1f}%")
    print(f"Improvement with large pool: {((time1 - time3) / time1 * 100):.1f}%")



if __name__ == "__main__":
    main()