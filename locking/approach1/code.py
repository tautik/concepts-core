import mysql.connector
import threading
import logging
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'airline_booking'
}

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Seat:
    def __init__(self, id: int, name: str, trip_id: int, user_id: Optional[int]):
        self.id = id
        self.name = name
        self.trip_id = trip_id
        self.user_id = user_id

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_all_users() -> List[User]:
    """Get all users from database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM users")
        users = [User(row[0], row[1]) for row in cursor.fetchall()]
        return users
    finally:
        cursor.close()
        conn.close()

def book(user: User) -> Tuple[Optional[Seat], Optional[str]]:
    """Book a seat for the user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Start transaction
        conn.start_transaction()
        
        # Select the first available seat
        cursor.execute("""
            SELECT id, name, trip_id, user_id FROM seats 
            WHERE trip_id = 1 AND user_id IS NULL 
            ORDER BY id LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "No available seats"
        
        # Create seat object
        seat = Seat(row[0], row[1], row[2], row[3])
        
        # Update the seat with user_id
        cursor.execute("""
            UPDATE seats SET user_id = %s WHERE id = %s
        """, (user.id, seat.id))
        
        # Commit transaction
        conn.commit()
        
        return seat, None
        
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cursor.close()
        conn.close()

def book_seat_worker(user: User):
    """Worker function for each thread"""
    seat, error = book(user)
    
    if error:
        logging.error(f"We could not assign the seat to {user.name}: {error}")
    else:
        logging.info(f"{user.name} was assigned the seat {seat.name}")

def main():
    logging.info("Starting seat booking simulation")
    
    # Get all users
    users = get_all_users()
    logging.info(f"Simulating {len(users)} users")
    
    # Create and start threads
    threads = []
    for user in users:
        thread = threading.Thread(target=book_seat_worker, args=(user,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check final seat allocation
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM seats WHERE user_id IS NOT NULL")
        allocated_seats = cursor.fetchone()[0]
        logging.info(f"Total seats allocated: {allocated_seats}")
        
        cursor.execute("SELECT id, name, user_id FROM seats WHERE user_id IS NOT NULL ORDER BY id")
        for row in cursor.fetchall():
            logging.info(f"Seat {row[1]} (ID: {row[0]}) allocated to user {row[2]}")
            
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()