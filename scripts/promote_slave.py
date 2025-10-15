"""Script to promote slave to master."""

import asyncio
import asyncpg


async def promote_slave_to_master(slave_port: int):
    """Promote slave to master."""
    slave_url = f"postgresql://postgres:p!fHj12345@localhost:{slave_port}/social_network"
    
    print(f"🔄 Promoting slave on port {slave_port} to master...")
    
    try:
        # Connect to slave
        conn = await asyncpg.connect(slave_url)
        
        # Check if it's in recovery mode
        is_recovery = await conn.fetchval("SELECT pg_is_in_recovery()")
        
        if is_recovery:
            print(f"   Slave is in recovery mode, promoting...")
            
            # This would require shell access to the container
            print(f"   Execute manually:")
            print(f"   docker exec postgres_slave{1 if slave_port == 5433 else 2} pg_ctl promote -D /var/lib/postgresql/data")
            
        else:
            print(f"   ✅ Node is already a master!")
        
        await conn.close()
        
    except Exception as e:
        print(f"   ❌ Failed to promote slave: {e}")


async def reconfigure_remaining_slave(new_master_port: int, slave_port: int):
    """Reconfigure remaining slave to follow new master."""
    print(f"🔄 Reconfiguring slave {slave_port} to follow new master {new_master_port}...")
    
    print(f"   Execute manually:")
    print(f"   1. Stop slave: docker-compose stop db-slave{1 if slave_port == 5433 else 2}")
    print(f"   2. Update primary_conninfo in postgresql.auto.conf")
    print(f"   3. Restart slave: docker-compose start db-slave{1 if slave_port == 5433 else 2}")


async def main():
    """Main promotion script."""
    print("🔄 PostgreSQL Slave Promotion Script")
    print("=" * 50)
    
    # Find which slave to promote (usually the one with most recent data)
    print("1️⃣ Choose slave to promote:")
    print("   1. Slave1 (port 5433)")
    print("   2. Slave2 (port 5434)")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        new_master_port = 5433
        remaining_slave_port = 5434
    elif choice == "2":
        new_master_port = 5434
        remaining_slave_port = 5433
    else:
        print("❌ Invalid choice")
        return
    
    # Promote chosen slave
    await promote_slave_to_master(new_master_port)
    
    # Reconfigure remaining slave
    await reconfigure_remaining_slave(new_master_port, remaining_slave_port)
    
    print("\n✅ Promotion process initiated!")
    print("   Follow the manual steps printed above.")


if __name__ == "__main__":
    asyncio.run(main())