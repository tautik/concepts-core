# Multi-Threading Concepts: Prime Number Counting

## Overview

This project demonstrates the evolution from sequential to optimized multi-threaded programming through a practical example: counting prime numbers up to 100 million. We explore three approaches that showcase the key principles of good multi-threaded code: **correctness** and **fairness**.

## Key Concepts

### What is Multi-Threading?
Multi-threading allows a program to execute multiple tasks concurrently. Think of it like having multiple workers instead of one person doing all the work.

### The Two Pillars of Good Multi-Threading

1. **Correctness**: Ensuring no race conditions or data corruption
   - Use locks to protect shared variables
   - Atomic operations for thread-safe updates

2. **Fairness**: Equal work distribution among threads
   - Prevents some threads from being idle while others are overloaded
   - Maximizes system resource utilization

### Important Concepts

- **Race Condition**: When multiple threads access shared data simultaneously, leading to incorrect results
- **Lock**: A synchronization mechanism that ensures only one thread can access a resource at a time
- **Atomic Operation**: An operation that completes entirely or not at all, preventing interruption

## The Three Approaches

### Approach 1: Sequential Processing
**File**: `01-sequential.py`
**Time**: ~3 minutes 49 seconds

```pseudocode
for each number from 3 to MAX_INT:
    if is_prime(number):
        increment counter
```

**Problem**: Uses only one core/thread, leaving other CPU resources unused.

### Approach 2: Multi-Threading with Fixed Batches
**File**: `02-multi-thread-fixed-batch.py`
**Time**: ~22 seconds

```pseudocode
divide range into equal batches
for each batch:
    create thread to process batch
    
thread_work(start, end):
    for number in range(start, end):
        if is_prime(number):
            with lock:
                increment shared_counter
```

**Problem**: Unequal work distribution. Later threads take longer because larger numbers require more computation to check primality.

### Approach 3: Fair Multi-Threading
**File**: `03-fair-multi-thread.py`
**Time**: ~22 seconds (all threads finish nearly simultaneously)

```pseudocode
shared_current_number = 3

thread_work():
    while True:
        with number_lock:
            if shared_current_number >= MAX_INT:
                break
            my_number = shared_current_number
            shared_current_number += 2
        
        if is_prime(my_number):
            with counter_lock:
                increment shared_counter
```

**Advantage**: All threads work continuously until completion. No thread sits idle.

## Code Structure

### Prime Checking Algorithm
```python
def check_prime(x):
    if x % 2 == 0:  # Even numbers (except 2) aren't prime
        return False
    
    # Only check odd divisors up to square root
    for i in range(3, int(math.sqrt(x)) + 1, 2):
        if x % i == 0:  # Found a divisor
            return False
    
    return True  # No divisors found, it's prime
```

### Thread-Safe Counter Update
```python
from threading import Lock

lock = Lock()
total_prime_numbers = 0

def increment_counter():
    with lock:  # Only one thread can execute this at a time
        global total_prime_numbers
        total_prime_numbers += 1
```

## Performance Comparison

| Approach | Time | Speedup | Efficiency |
|----------|------|---------|------------|
| Sequential | ~229 seconds | 1x | Single core |
| Fixed Batches | ~23 seconds | 10x | Uneven load |
| Fair Threading | ~22 seconds | 10.4x | Optimal load |

## Key Takeaways

1. **Just adding threads isn't enough** - work distribution matters
2. **Locks prevent race conditions** but should be used minimally to avoid bottlenecks
3. **Fair work distribution** ensures all threads contribute equally
4. **Atomic operations** are crucial for shared resource management

## Running the Examples

```bash
# Sequential approach
python3 01-multi-thread/main.py

# Multi-threading with batches
python3 01-multi-thread/02-multi-thread-fixed-batch.py

# Fair multi-threading
python3 01-multi-thread/03-fair-multi-thread.py
```

## Learning Resources

To learn more about these concepts, explore:
- **Variable Scope**: `global` vs `local` variables
- **Threading Module**: `threading.Thread`, `threading.Lock`
- **Synchronization**: Locks, semaphores, atomic operations
- **LEGB Rule**: Local, Enclosing, Global, Built-in scope resolution

---