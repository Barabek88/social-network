"""Failover test script for PostgreSQL master-slave setup."""

import asyncio
import asyncpg
import time
from datetime import datetime


class FailoverTest:
    def __init__(self):
        self.master_url = "postgresql://postgres:p!fHj12345@localhost:5432/social_network"
        self.slave1_url = "postgresql://postgres:p!fHj12345@localhost:5433/social_network"
        self.slave2_url = "postgresql://postgres:p!fHj12345@localhost:5434/social_network"
        
        self.successful_writes = 0
        self.failed_writes = 0
        self.running = True
    
    async def create_test_table(self):
        """Create test table for load testing."""
        try:
            conn = await asyncpg.connect(self.master_url)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS failover_test (
                    id SERIAL PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("TRUNCATE TABLE failover_test")
            await conn.close()
            print("✅ Test table created and cleared")
        except Exception as e:
            print(f"❌ Failed to create test table: {e}")
    
    async def write_load_worker(self, worker_id: int):
        """Worker that continuously writes data to master."""
        while self.running:
            try:
                conn = await asyncpg.connect(self.master_url)
                await conn.execute(
                    "INSERT INTO failover_test (data) VALUES ($1)",
                    f"worker_{worker_id}_data_{int(time.time())}"
                )
                await conn.close()
                self.successful_writes += 1
                
                if self.successful_writes % 100 == 0:
                    print(f"📝 Successful writes: {self.successful_writes}")
                
                await asyncio.sleep(0.1)  # 10 writes per second per worker
                
            except Exception as e:
                self.failed_writes += 1
                print(f"❌ Write failed (worker {worker_id}): {e}")
                await asyncio.sleep(1)  # Wait longer on error
    
    async def start_load_test(self, num_workers: int = 5):
        """Start load testing with multiple workers."""
        print(f"🚀 Starting load test with {num_workers} workers...")
        
        # Create test table
        await self.create_test_table()
        
        # Start workers
        tasks = []
        for i in range(num_workers):
            task = asyncio.create_task(self.write_load_worker(i))
            tasks.append(task)
        
        return tasks
    
    async def stop_load_test(self, tasks):
        """Stop load testing."""
        print("🛑 Stopping load test...")
        self.running = False
        
        # Cancel all tasks
        for task in tasks:
            task.cancel()
        
        # Wait for tasks to finish
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"📊 Final results:")
        print(f"   Successful writes: {self.successful_writes}")
        print(f"   Failed writes: {self.failed_writes}")
    
    async def check_data_consistency(self):
        """Check data consistency across all nodes."""
        print("🔍 Checking data consistency...")
        
        results = {}
        
        # Check master (if available)
        try:
            conn = await asyncpg.connect(self.master_url)
            count = await conn.fetchval("SELECT COUNT(*) FROM failover_test")
            results["master"] = count
            await conn.close()
            print(f"   Master: {count} rows")
        except Exception as e:
            print(f"   Master: UNAVAILABLE ({e})")
            results["master"] = "UNAVAILABLE"
        
        # Check slave1
        try:
            conn = await asyncpg.connect(self.slave1_url)
            count = await conn.fetchval("SELECT COUNT(*) FROM failover_test")
            results["slave1"] = count
            await conn.close()
            print(f"   Slave1: {count} rows")
        except Exception as e:
            print(f"   Slave1: UNAVAILABLE ({e})")
            results["slave1"] = "UNAVAILABLE"
        
        # Check slave2
        try:
            conn = await asyncpg.connect(self.slave2_url)
            count = await conn.fetchval("SELECT COUNT(*) FROM failover_test")
            results["slave2"] = count
            await conn.close()
            print(f"   Slave2: {count} rows")
        except Exception as e:
            print(f"   Slave2: UNAVAILABLE ({e})")
            results["slave2"] = "UNAVAILABLE"
        
        return results
    
    async def get_latest_lsn(self, url: str):
        """Get latest LSN from a node."""
        try:
            conn = await asyncpg.connect(url)
            lsn = await conn.fetchval("SELECT pg_last_wal_replay_lsn()")
            await conn.close()
            return lsn
        except Exception as e:
            print(f"❌ Failed to get LSN: {e}")
            return None
    
    async def find_most_recent_slave(self):
        """Find slave with most recent data."""
        print("🔍 Finding most recent slave...")
        
        slave1_lsn = await self.get_latest_lsn(self.slave1_url)
        slave2_lsn = await self.get_latest_lsn(self.slave2_url)
        
        print(f"   Slave1 LSN: {slave1_lsn}")
        print(f"   Slave2 LSN: {slave2_lsn}")
        
        if slave1_lsn and slave2_lsn:
            if slave1_lsn >= slave2_lsn:
                print("   🏆 Slave1 has most recent data")
                return "slave1", self.slave1_url
            else:
                print("   🏆 Slave2 has most recent data")
                return "slave2", self.slave2_url
        elif slave1_lsn:
            print("   🏆 Slave1 is available (slave2 down)")
            return "slave1", self.slave1_url
        elif slave2_lsn:
            print("   🏆 Slave2 is available (slave1 down)")
            return "slave2", self.slave2_url
        else:
            print("   ❌ No slaves available")
            return None, None


async def main():
    """Main failover test scenario."""
    test = FailoverTest()
    
    print("=" * 60)
    print("🧪 PostgreSQL Failover Test")
    print("=" * 60)
    
    # Step 1: Start load testing
    print("\n1️⃣ Starting load test...")
    tasks = await test.start_load_test(num_workers=3)
    
    # Let it run for a while
    print("⏳ Running load test for 30 seconds...")
    await asyncio.sleep(30)
    
    # Step 2: Check initial state
    print("\n2️⃣ Checking initial state...")
    initial_results = await test.check_data_consistency()
    
    # Step 3: Simulate master failure
    print("\n3️⃣ Simulating master failure...")
    print("   💀 Kill master node manually: docker-compose stop db")
    print("   Press Enter when master is killed...")
    input()
    
    # Continue load test for a bit to see failures
    print("⏳ Continuing load test for 10 seconds to observe failures...")
    await asyncio.sleep(10)
    
    # Step 4: Stop load test
    print("\n4️⃣ Stopping load test...")
    await test.stop_load_test(tasks)
    
    # Step 5: Find most recent slave
    print("\n5️⃣ Finding most recent slave...")
    best_slave, best_url = await test.find_most_recent_slave()
    
    # Step 6: Check final consistency
    print("\n6️⃣ Checking final data consistency...")
    final_results = await test.check_data_consistency()
    
    # Step 7: Calculate data loss
    print("\n7️⃣ Analyzing results...")
    print(f"   Expected writes: {test.successful_writes}")
    
    if best_slave and isinstance(final_results.get(best_slave), int):
        actual_rows = final_results[best_slave]
        lost_transactions = test.successful_writes - actual_rows
        print(f"   Actual rows in {best_slave}: {actual_rows}")
        print(f"   Lost transactions: {lost_transactions}")
        
        if lost_transactions == 0:
            print("   ✅ NO DATA LOSS!")
        else:
            print(f"   ⚠️  Data loss detected: {lost_transactions} transactions")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())