#!/usr/bin/env python3
"""
Simple Replication Demo
======================
Shows the basic difference between sync and async replication
"""

import time
import random


class Database:
    """A simple database that holds data"""
    
    def __init__(self, name):
        self.name = name
        self.data = {}  # Our "database" is just a dictionary
    
    def write(self, key, value):
        """Write data to this database"""
        # Simulate some network/disk delay
        time.sleep(random.uniform(0.01, 0.05))  # 10-50ms delay
        self.data[key] = value
        print(f"  ✓ {self.name}: saved {key} = {value}")
    
    def read(self, key):
        """Read data from this database"""
        return self.data.get(key, "NOT FOUND")


def synchronous_replication(primary, replicas, key, value):
    """
    SYNCHRONOUS: Write to primary, then wait for ALL replicas to confirm
    """
    print(f"\n🔄 SYNC REPLICATION: Writing {key} = {value}")
    start_time = time.time()
    
    # Step 1: Write to primary first
    print(f"Step 1: Writing to primary...")
    primary.write(key, value)
    
    # Step 2: Write to ALL replicas and WAIT for each one
    print(f"Step 2: Writing to {len(replicas)} replicas...")
    for replica in replicas:
        replica.write(key, value)  # This blocks until replica confirms
    
    elapsed = time.time() - start_time
    print(f"✅ SYNC COMPLETE: {elapsed:.3f} seconds")
    return True


def asynchronous_replication(primary, replicas, key, value):
    """
    ASYNCHRONOUS: Write to primary, return immediately, replicate in background
    """
    print(f"\n🚀 ASYNC REPLICATION: Writing {key} = {value}")
    start_time = time.time()
    
    # Step 1: Write to primary
    print(f"Step 1: Writing to primary...")
    primary.write(key, value)
    
    # Step 2: Return success immediately (don't wait for replicas)
    elapsed = time.time() - start_time
    print(f"✅ ASYNC PRIMARY COMPLETE: {elapsed:.3f} seconds")
    print(f"📤 Replicas will be updated in background...")
    
    # Step 3: Simulate background replication (happens "later")
    def background_replication():
        print(f"  🔄 Background: Updating replicas...")
        for replica in replicas:
            replica.write(key, value)
    
    # In real systems, this would run in a separate thread
    # For simplicity, we'll just call it after a delay
    time.sleep(0.1)  # Simulate some time passing
    background_replication()
    
    return True


def show_database_state(databases):
    """Show what's in each database"""
    print(f"\n📊 DATABASE STATE:")
    for db in databases:
        print(f"  {db.name}: {db.data}")


def main():
    print("🎯 SIMPLE REPLICATION DEMO")
    print("=" * 40)
    
    # Create databases
    primary = Database("PRIMARY")
    replica1 = Database("REPLICA-1") 
    replica2 = Database("REPLICA-2")
    
    print(f"\n💾 Created 1 primary + 2 replica databases")
    
    # Demo 1: Synchronous Replication (like banking)
    print(f"\n" + "="*50)
    print(f"🏦 BANKING SCENARIO - Must be consistent!")
    synchronous_replication(primary, [replica1, replica2], "account_123", 5000)
    show_database_state([primary, replica1, replica2])
    
    # Demo 2: Asynchronous Replication (like social media)
    print(f"\n" + "="*50)
    print(f"📱 SOCIAL MEDIA SCENARIO - Speed matters!")
    asynchronous_replication(primary, [replica1, replica2], "post_456", "Hello World!")
    show_database_state([primary, replica1, replica2])
    
    # Performance comparison
    print(f"\n" + "="*50)
    print(f"⚡ SPEED COMPARISON")
    
    # Time sync replication
    start = time.time()
    synchronous_replication(primary, [replica1, replica2], "sync_test", "data")
    sync_time = time.time() - start
    
    # Time async replication (just the primary write)
    start = time.time()
    primary.write("async_test", "data")
    async_time = time.time() - start
    
    print(f"\n📈 RESULTS:")
    print(f"  Synchronous:  {sync_time:.3f} seconds")
    print(f"  Asynchronous: {async_time:.3f} seconds") 
    print(f"  Speedup:      {sync_time/async_time:.1f}x faster with async")


if __name__ == "__main__":
    main()