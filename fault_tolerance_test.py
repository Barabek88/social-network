#!/usr/bin/env python3
"""
Load testing script for fault tolerance testing
"""
import asyncio
import aiohttp
import time
from datetime import datetime

BASE_URL = "http://localhost"
TOKEN = "your_jwt_token_here"
NUM_REQUESTS = 10000
CONCURRENT = 50


async def send_request(session, url, headers):
    start = time.time()
    try:
        async with session.get(url, headers=headers) as resp:
            status = resp.status
            duration = time.time() - start
            return {"success": status == 200, "duration": duration, "status": status}
    except Exception as e:
        return {"success": False, "duration": time.time() - start, "error": str(e)}


async def run_load_test():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"{BASE_URL}/api/v1/user/search?first_name=Te&second_name=Us"
    
    print(f"[{datetime.now()}] Starting load test...")
    print(f"URL: {url}")
    print(f"Requests: {NUM_REQUESTS}, Concurrent: {CONCURRENT}")
    print("-" * 60)
    
    success_count = 0
    error_count = 0
    total_duration = 0
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        for i in range(0, NUM_REQUESTS, CONCURRENT):
            batch = min(CONCURRENT, NUM_REQUESTS - i)
            tasks = [send_request(session, url, headers) for _ in range(batch)]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                if result["success"]:
                    success_count += 1
                    total_duration += result["duration"]
                else:
                    error_count += 1
                    print(f"[{datetime.now()}] Error: {result.get('error', 'Unknown')}")
            
            # Progress
            if (i + batch) % 500 == 0:
                elapsed = time.time() - start_time
                current_rps = (i + batch) / elapsed
                print(f"[{datetime.now()}] Progress: {i + batch}/{NUM_REQUESTS} | RPS: {current_rps:.2f} | Errors: {error_count}")
        
        total_time = time.time() - start_time
    
    print("-" * 60)
    print(f"[{datetime.now()}] Test completed!")
    print(f"Total time: {total_time:.2f}s")
    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    print(f"RPS: {NUM_REQUESTS/total_time:.2f}")
    if success_count > 0:
        print(f"Avg latency: {(total_duration/success_count)*1000:.2f}ms")


if __name__ == "__main__":
    asyncio.run(run_load_test())
