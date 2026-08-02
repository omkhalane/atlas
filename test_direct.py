import asyncio
import json
from api import run_atlas_engine, event_queues, approval_events

async def test_engine():
    exec_id = "test_123"
    goal = "What is today's date? Just run the date command."
    
    event_queues[exec_id] = asyncio.Queue()
    approval_events[exec_id] = asyncio.Event()
    
    # Run engine in background
    task = asyncio.create_task(run_atlas_engine(exec_id, goal))
    
    q = event_queues[exec_id]
    while True:
        msg = await q.get()
        print(f"Event: {msg}")
        if '"status": "completed"' in msg or '"status": "failed"' in msg or '"type": "error"' in msg or '"type": "finish"' in msg:
            break
            
    await task

if __name__ == "__main__":
    asyncio.run(test_engine())
