# SELECT FOR UPDATE - Database Locking Approach 2

## The Change - Adding FOR UPDATE

**Approach 2** makes a tiny but crucial change to Approach 1: we simply add `FOR UPDATE` to the end of our SELECT query:

```sql
SELECT id, name, trip_id, user_id FROM seats 
WHERE trip_id = 1 AND user_id IS NULL 
ORDER BY id LIMIT 1 FOR UPDATE
```

This small addition completely changes the behavior of our concurrent seat booking system.

## What FOR UPDATE Does

`FOR UPDATE` creates an **exclusive lock** on the rows returned by the SELECT query. This means:
- Only one transaction can hold the lock on a row at a time
- Other transactions trying to lock the same row must wait
- The lock is released when the transaction commits or rolls back

## What Happens Now - The Extreme Example

Let's trace through what happens when all 120 threads try to book seats simultaneously:

### Step 1: The Initial Lock Battle
1. All 120 transactions start and fire the SELECT FOR UPDATE query
2. All 120 transactions want to lock **the same row** (seat 1-A) because it's the first available seat
3. **Only one transaction gets the exclusive lock** on seat 1-A
4. **119 transactions are now waiting** for that lock to be released

### Step 2: The First Success
1. The transaction that got the lock updates seat 1-A and commits
2. Database signals all 119 waiting transactions: "Wake up! The lock is released!"

### Step 3: The Key Insight - Query Re-evaluation
Here's the crucial part that many people miss:

When the 119 transactions wake up, they **don't just proceed with their original result**. Instead, the database **re-evaluates the entire query** to see which rows match the WHERE clause now.

Why? Because the WHERE clause `user_id IS NULL` might no longer be true for seat 1-A (it now has a user_id).

### Step 4: The Next Lock Battle
1. All 119 transactions re-evaluate: `WHERE trip_id = 1 AND user_id IS NULL ORDER BY id LIMIT 1`
2. Now seat 1-B is the first available seat that matches
3. All 119 transactions try to lock seat 1-B
4. One gets it, 118 wait...

### Step 5: The Pattern Continues
This process repeats until all 8 seats are allocated:
- 118 transactions wake up, re-evaluate, all try to lock seat 1-C
- 117 transactions wake up, re-evaluate, all try to lock seat 1-D
- And so on...

## Why All 8 Seats Get Filled (In Order)

Unlike Approach 1 where only 4-5 seats got filled randomly, Approach 2 fills **all available seats in perfect order**:

1. **No Race Conditions**: Only one transaction can work on a seat at a time
2. **Query Re-evaluation**: Ensures transactions always work on truly available seats
3. **Sequential Processing**: The ORDER BY id ensures seats are allocated 1-A, 1-B, 1-C, etc.

## Performance Trade-off

**The Cost**: Execution time increases dramatically (from ~few ms to ~489ms in the example)

**Why it's slower**:
- Transactions spend most of their time **waiting** for locks
- Only one transaction can make progress at a time
- We've essentially serialized what was previously parallel

## Key Behavioral Changes

### Seats Allocated
- **Approach 1**: 4-5 seats (unpredictable)
- **Approach 2**: All 8 seats (predictable)

### Order of Allocation  
- **Approach 1**: Random seats (1-A, 1-C, 1-F, etc.)
- **Approach 2**: Sequential seats (1-A, 1-B, 1-C, 1-D, 1-E, 1-F, 2-A, 2-B)

### User Allocation
- **Approach 1**: Unpredictable which users get seats
- **Approach 2**: Still unpredictable which users get seats (depends on thread scheduling)

### Execution Time
- **Approach 1**: Very fast (~few milliseconds)
- **Approach 2**: Much slower (~489ms)

## The Fundamental Lesson

`SELECT FOR UPDATE` transforms our system from:
- **Fast but incorrect** (race conditions, inconsistent results)
- **Slow but correct** (no race conditions, predictable results)

This demonstrates a classic trade-off in concurrent systems: **consistency vs. performance**. 

The database's automatic query re-evaluation feature ensures that even when transactions are waiting and waking up, they always work with fresh, accurate data - eliminating the race conditions we saw in Approach 1.

## What's Still Unpredictable

Even though seats are allocated in order, **which user gets which seat is still unpredictable** because:
1. Thread scheduling by the OS is non-deterministic
2. Database connection timing varies
3. Transaction scheduling within the database varies

So while Liam Hudson got seat 1-A in one run, it could be any user in the next run - but it will always be seat 1-A that gets filled first.