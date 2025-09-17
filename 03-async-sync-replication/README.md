# Database Replication Patterns

## What is Database Replication?

Database replication keeps multiple copies of data on different servers.

## Two Main Patterns

**Synchronous Replication**: Wait for all replicas before confirming success  
**Asynchronous Replication**: Confirm immediately, replicate in background

## Synchronous Replication

### When to Use:
Banking, medical records, legal documents - any data where loss causes problems

### Pseudocode:
```
FUNCTION sync_replication(data):
    primary_db.save(data)
    
    FOR EACH replica:
        success = replica.save(data)  // Wait for confirmation
        IF NOT success:
            ROLLBACK
            RETURN FAILURE
    
    RETURN SUCCESS
```

### Transaction Flow:
```
User: Transfer $100
Primary: Save transaction
Replica1: Confirm saved
Replica2: Confirm saved  
User: "SUCCESS" (after all confirmations)
```

### Characteristics:
- Strong consistency
- Slower writes
- Zero data loss

## Asynchronous Replication

### When to Use:
Social media, content, analytics - where speed matters more than perfect consistency

### Pseudocode:
```
FUNCTION async_replication(data):
    primary_db.save(data)
    user.send_response("SUCCESS")  // Return immediately
    
    background_queue.add(data)  // Replicate later
```

### Transaction Flow:
```
User: Create post
Primary: Save post
User: "SUCCESS" (immediate)
Background: Replicate to other servers later
```

### Characteristics:
- Fast writes
- Eventual consistency
- Can handle replica failures

## Transaction Differences

### Synchronous:
```
BEGIN TRANSACTION
  UPDATE balance = balance - 100
  Wait for all replicas to confirm
COMMIT TRANSACTION
```

### Asynchronous:
```
BEGIN TRANSACTION  
  UPDATE likes = likes + 1
COMMIT TRANSACTION  // Primary only

Replicas update later in background
```

## Decision Framework

**Use Sync**: When data loss causes legal/financial problems  
**Use Async**: When speed matters and brief inconsistency is acceptable