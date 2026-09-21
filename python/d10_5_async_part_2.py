import time
from collections import deque
from typing import Iterator
def task(name: str, steps: int) -> Iterator[None]:
    for i in range(steps):
        if name == "C":
            time.sleep(2)
        print(f"{name} is at {i + 1}")
        yield

queue = deque([("A",task("A",3)),("B",task("B",1)),("C",task("C",2))])



if __name__ == "__main__":
    
    start = time.perf_counter()
    while queue:
        name,first = queue.popleft()
        try:
            next(first)
            queue.append((name,first))
            
        except StopIteration:
            print(f"{name} is finished")    
    print(time.perf_counter() - start)

