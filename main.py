from utils import utils 
import asyncio
import time

runtime = time.perf_counter()
print(f"""
Initializing data...
""")
asyncio.run(utils.create_csv())
print(f"""
Execution Ended...
""")
