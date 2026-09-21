import asyncio,time,os


def helper(n: int):
    time.sleep(n)
    
async def print_name(name: str = "sherry") -> None:
    print(f"I am {name} funtion and is started")
    await asyncio.to_thread(helper,2)
    print(f"I was {name} function and i am done")
    
async def run_all_separate(n: int) -> None:
    names = ["A","B","C"]
    for i in range(n):
        await print_name(names[i])
        
async def run_all():
    await asyncio.gather(print_name("A"),print_name("B"),print_name("C"))
        
        
if __name__ == "__main__":
    start_1 = time.perf_counter()
    asyncio.run(print_name())
    end_1 = time.perf_counter()
    print(f"First event loop took {end_1 - start_1}")
    start_2 = time.perf_counter()
    asyncio.run(run_all_separate(3))
    end_2 = time.perf_counter()
    print(f"Second event loop took {end_2 - start_2}")
    start_3 = time.perf_counter()
    asyncio.run(run_all())
    end_3 = time.perf_counter()
    print(f"Third event loop took {end_3 - start_3}")
    