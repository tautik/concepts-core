# Airline Check-in System - Database Concurrency and Locking

## Problem Statement

When you book your tickets with an airline, you are required to complete the payment and confirm your reservation. Once the reservation is complete, you can either optionally do a web check-in and confirm your seats or just before your departure do a physical check-in at the airport.

In this problem statement, let's design this web check-in system, where the passenger logs in to the system with the PNR, performs the seat selection and gets the boarding pass. If the passenger tries to book a seat already booked and assigned to another passenger, show an error message requesting the passenger to re-select the seats.

### Relog Airline Check-in System

## Requirements

The problem statement is something to start with, be creative and dive into the product details and add constraints and features you think would be important.

### Core Requirements

- One seat can be assigned to only one passenger and once assigned the seat cannot be transferred
- Assume all 100 people boarding the plane are trying to make a selection of their seat at the same time
- The check-in should be as fast as possible
- When one passenger is booking a seat it should not lead to other passengers waiting

### High Level Requirements

- Make your high-level components operate with high availability
- Ensure that the data in your system is durable, no matter what happens
- Define how your system would behave while scaling-up and scaling-down
- Make your system cost-effective and provide a justification for the same
- Describe how capacity planning helped you make a good design decision
- Think about how other services will interact with your service

### Micro Requirements

- Ensure the data in your system is never going in an inconsistent state
- Ensure your system is free of deadlocks (if applicable)
- Ensure that the throughput of your system is not affected by locking, if it does, state how it would affect

## Output

### Design Document
Create a design document of this system/feature stating all critical design decisions, tradeoffs, components, services, and communications. Also specify how your system handles at scale, and what will eventually become a chokepoint.

Do not create unnecessary components, just to make design look complicated. A good design is always simple and elegant. A good way to think about it is if you were to create a separate process/machine/infra for each component and you will have to code it yourself, would you still do it?

### Prototype
To understand the nuances and internals of this system, build a prototype that:

- Design a database schema for the airline check-in system
- Build a simple interface allowing passenger to:
  - View available seats
  - View unavailable seats
  - Select a seat of their liking
  - Upon successful booking, print their boarding pass
- Simulate multiple passengers trying to book the same seats and handle the concurrency

## Implemented Approaches

This repository contains three different approaches to handling database concurrency in the airline check-in system, each demonstrating different locking mechanisms and their trade-offs.

### Database Schema

The prototype uses a simple database schema with three tables:
- **Users**: 120 people with ID and name
- **Trips**: One trip "AIRINDIA-101"
- **Seats**: 8 seats (1-A through 2-B) initially unassigned (user_id = NULL)

### Approach 1: Basic Implementation (Race Conditions)

**Location**: `approach1/`

**Implementation**: Basic threading with simple SELECT and UPDATE queries
- Start 120 threads (one for each user)
- Each thread finds the first available seat and tries to book it
- No explicit locking mechanism

**Results**:
- ❌ Only 4-5 seats get allocated (unpredictable)
- ❌ Race conditions occur
- ✅ Very fast execution (~few milliseconds)
- ❌ Non-deterministic results

**Key Learning**: Demonstrates classic race conditions where multiple transactions read the same data and try to update the same rows, leading to inconsistent results.

### Approach 2: SELECT FOR UPDATE (Exclusive Locking)

**Location**: `approach2/`

**Implementation**: Adds `FOR UPDATE` to the SELECT query
```sql
SELECT id, name, trip_id, user_id FROM seats 
WHERE trip_id = 1 AND user_id IS NULL 
ORDER BY id LIMIT 1 FOR UPDATE
```

**Results**:
- ✅ All 8 seats get allocated
- ✅ No race conditions
- ✅ Sequential seat allocation (1-A, 1-B, 1-C, etc.)
- ❌ Much slower execution (~489ms)

**Key Learning**: Exclusive locking eliminates race conditions but creates a bottleneck where transactions wait for each other, essentially serializing the process.

### Approach 3: SKIP LOCKED (Non-blocking Locking)

**Location**: `approach3/`

**Implementation**: Adds `SKIP LOCKED` to the SELECT FOR UPDATE query
```sql
SELECT id, name, trip_id, user_id FROM seats 
WHERE trip_id = 1 AND user_id IS NULL 
ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED
```

**Results**:
- ✅ All 8 seats get allocated
- ✅ No race conditions
- ✅ Fast execution (~23ms)
- ✅ No waiting/blocking
- ⚠️ Seats picked in order but allocated randomly due to commit timing

**Key Learning**: `SKIP LOCKED` provides the best of both worlds - correctness and performance - by allowing transactions to skip locked rows and find available ones immediately.

## Performance Comparison

| Aspect | Approach 1 | Approach 2 | Approach 3 |
|--------|------------|------------|------------|
| **Seats Filled** | 4-5 (unpredictable) | 8 (all) | 8 (all) |
| **Speed** | Very fast (~few ms) | Very slow (~489ms) | Fast (~23ms) |
| **Correctness** | Race conditions | Correct | Correct |
| **Seat Order** | Random | Sequential | Picked in order, allocated randomly |
| **Waiting** | No explicit waiting | Lots of waiting | No waiting |
| **Consistency** | ❌ Inconsistent | ✅ Consistent | ✅ Consistent |

## Key Takeaways

1. **Concurrency is Hard**: Even simple operations can have complex race conditions when multiple threads are involved
2. **Trade-offs are Inevitable**: You often have to choose between performance and consistency
3. **Database Features Matter**: Modern databases provide sophisticated locking mechanisms that can help achieve both performance and correctness
4. **SKIP LOCKED is Often Optimal**: For many use cases, it provides the best balance of speed and correctness
5. **Simple Solutions**: Sometimes the best solution is not to use concurrency at all - a simple sequential loop might be sufficient

## Recommended Tech Stack

| Component | Options |
|-----------|---------|
| **Language** | Golang, Java, C++, Python |
| **Database** | Relational Database - MySQL, PostgreSQL, SQLite |

## Common Pitfalls

Keep these pitfalls in mind while building the prototype:
- Have a primary key in your tables otherwise the entire table might get locked
- Understand the difference between different isolation levels
- Be aware of deadlock possibilities when using multiple locks
- Consider the trade-offs between consistency and performance

## What You'll Learn

- Database locking mechanisms
- Database schema design
- Concurrency control strategies
- Performance vs consistency trade-offs
- Real-world application of database isolation levels 