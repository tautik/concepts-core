# Database Concurrency and Race Conditions - Approach 1

## The Problem Setup

We have a simple airline booking system with three tables:
- **Users**: 120 people with just ID and name (no email, age, or other details)
- **Trips**: Just one trip "AIRINDIA-101" 
- **Seats**: 8 seats (1-A through 2-B) initially unassigned (user_id = NULL)

The goal is to simulate 120 people trying to book seats simultaneously and understand what happens with database concurrency.

## The Approach

**Approach 1** is the most basic implementation:
1. Start 120 threads (one for each user)
2. Each thread tries to book a seat by:
   - Starting a transaction
   - Finding the first available seat (`WHERE user_id IS NULL ORDER BY id LIMIT 1`)
   - Updating that seat with the user's ID
   - Committing the transaction

## What Actually Happens?

When we run this code, instead of all 120 people getting seats (which is impossible since we only have 8 seats), we see something interesting: **only 4-5 seats get allocated**, and the number varies each time we run it.

## Why This Happens - The Race Condition

### Multiple Levels of Contention

The race condition occurs at several levels:

1. **Thread Scheduling**: Not all 120 threads start simultaneously. The operating system decides which thread gets CPU time when.

2. **Database Connection**: Each thread needs to establish a database connection and start a transaction.

3. **Query Execution**: Multiple transactions fire the same SELECT query almost simultaneously.

### The Race Condition in Detail

Here's what happens step by step:

1. **First Wave**: Multiple transactions (let's say 20-30) start almost simultaneously and execute:
   ```sql
   SELECT id, name, trip_id, user_id FROM seats 
   WHERE trip_id = 1 AND user_id IS NULL 
   ORDER BY id LIMIT 1
   ```
   
2. **Same Result**: All these transactions get the **same row** (seat 1-A) because at the time they read, all seats were still available.

3. **Race to Update**: All these transactions then try to update seat 1-A:
   ```sql
   UPDATE seats SET user_id = ? WHERE id = ?
   ```

4. **Only One Wins**: Only one transaction successfully commits. The others either fail or get blocked.

5. **Next Wave**: The next batch of transactions that execute the SELECT query now see that seat 1-A is taken, so they all get seat 1-B, and the race repeats.

6. **Sequential Pattern**: This continues, with each "wave" of concurrent transactions all targeting the same next available seat.

### Why So Few Seats Get Allocated?

The key insight is that transactions are reading the **same data** and trying to update the **same rows**. Instead of 120 transactions each getting a unique seat, we have:

- 20-30 transactions all trying to book seat 1-A (only 1 succeeds)
- 15-25 transactions all trying to book seat 1-B (only 1 succeeds)  
- 10-20 transactions all trying to book seat 1-C (only 1 succeeds)
- And so on...

The exact number of seats allocated depends on:
- How threads get scheduled by the OS
- Database connection timing
- Transaction isolation levels
- System load

## The Fundamental Issue

This approach has a classic **race condition**: the time gap between reading data (SELECT) and modifying it (UPDATE) allows other transactions to read the same stale data. Multiple transactions make decisions based on the same outdated information.

## Key Takeaways

1. **Concurrency is Hard**: Even simple operations can have complex race conditions when multiple threads are involved.

2. **Non-Deterministic Results**: The same code produces different results each time because thread scheduling is unpredictable.

3. **Resource Waste**: Many threads do unnecessary work, trying to book seats that are already taken.

4. **Need for Better Locking**: This approach demonstrates why we need proper locking mechanisms to handle concurrent access to shared resources.

This is just the first approach to understand the problem. Better approaches would involve proper locking mechanisms like SELECT FOR UPDATE, optimistic locking, or application-level coordination to ensure fair seat allocation.