# SKIP LOCKED - Non-blocking Database Locking Approach 3

## The Change - Adding SKIP LOCKED

**Approach 3** adds one more keyword to our SELECT query from Approach 2:

```sql
SELECT id, name, trip_id, user_id FROM seats 
WHERE trip_id = 1 AND user_id IS NULL 
ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED
```

This small addition fundamentally changes how transactions handle locked rows.

## What SKIP LOCKED Does

`SKIP LOCKED` tells the database: **"If a row is locked by another transaction, don't wait - just skip it and move to the next available row."**

This eliminates the waiting/blocking behavior we saw in Approach 2.

## What Happens Now - No More Waiting

Let's trace through what happens when all 120 threads try to book seats simultaneously:

### Step 1: The Rush Begins
1. All 120 transactions start and fire the SELECT FOR UPDATE SKIP LOCKED query
2. **Transaction 1** locks seat 1-A and starts processing
3. **Transaction 2** tries to lock seat 1-A, finds it locked, **skips it automatically** and locks seat 1-B
4. **Transaction 3** tries seat 1-A (locked), tries 1-B (locked), locks seat 1-C
5. **Transaction 4** skips 1-A, 1-B, 1-C and locks seat 1-D
6. And so on...

### Step 2: Parallel Processing
- **No waiting!** Each transaction immediately finds an available seat
- **8 transactions** successfully lock seats 1-A through 2-B
- **112 transactions** find no available seats (all are locked) and get no results
- All transactions process in parallel instead of sequentially

### Step 3: Results
- **8 seats get allocated** (all available seats)
- **112 transactions fail** with "No available seats"
- **Much faster execution** (~23ms vs ~489ms in Approach 2)

## Key Behavioral Changes

### Speed - The Big Win
- **Approach 2**: ~489ms (slow due to waiting)
- **Approach 3**: ~23ms (fast due to no waiting)

**Why it's faster**: Transactions don't waste time waiting for locks. They either get a seat immediately or fail immediately.

### Seat Allocation Order
This is where it gets interesting. The transcript mentions seats are **picked in order** but **not allocated in order**.

**What this means**:
- **Database level**: Seats are examined in order (1-A, 1-B, 1-C, etc.)
- **Application level**: Seat assignments appear in random order in logs

**Why the mismatch**?
Even though Transaction 1 locks 1-A first, Transaction 2 locks 1-B first, etc., the **commit order** depends on:
- CPU scheduling of threads
- Transaction processing time variations
- Database internal scheduling

So you might see in logs:
```
User X was assigned seat 1-C
User Y was assigned seat 1-A  
User Z was assigned seat 1-E
User W was assigned seat 1-B
```

### All Available Seats Get Filled
Unlike Approach 1 (4-5 seats) but same as Approach 2, **all 8 seats get allocated**.

## The Three-Way Comparison

| Aspect | Approach 1 | Approach 2 | Approach 3 |
|--------|------------|------------|------------|
| **Seats Filled** | 4-5 (unpredictable) | 8 (all) | 8 (all) |
| **Speed** | Very fast (~few ms) | Very slow (~489ms) | Fast (~23ms) |
| **Correctness** | Race conditions | Correct | Correct |
| **Seat Order** | Random | Sequential | Picked in order, allocated randomly |
| **Waiting** | No explicit waiting | Lots of waiting | No waiting |

## The Fundamental Trade-offs

**Approach 3 gives us the best of both worlds**:
- ✅ **Correctness**: No race conditions, all seats allocated  
- ✅ **Performance**: Fast execution, no blocking
- ✅ **Efficiency**: No wasted CPU cycles waiting

**The only "downside"**: 
- 112 users get rejected immediately instead of waiting for a chance
- Commit order is unpredictable (though seat picking is ordered)

## The Fairness Question

The transcript raises an important point: **What if we want user 1 to get seat 1, user 2 to get seat 2, etc.?**

**Answer**: Don't use threading! Use a simple loop:
```python
for i, user in enumerate(users):
    if i < 8:  # Only 8 seats available
        assign_seat(user, seats[i])
```

**Key insight**: Most problems don't actually need the complexity of multi-threading. Sometimes the simplest solution is the best solution.

## Key Takeaways

1. **SKIP LOCKED eliminates waiting**: Transactions either succeed immediately or fail immediately
2. **Performance without sacrificing correctness**: We get speed AND reliability  
3. **Order vs Timing**: Database operations can be ordered while their completion is not
4. **Don't over-complicate**: Many "concurrent" problems have simple sequential solutions
5. **It's easy to write multi-threaded programs, difficult to write correct ones, even harder to write fair, efficient, and correct ones**

This approach demonstrates that with the right database features, we can achieve high performance concurrent processing without sacrificing data consistency.