import time
from functools import wraps


def log_call(func):
    @wraps(func)  # without wraps the 
    def wrapper(*args,**kwargs):
        name = func.__name__
        print(name,args,kwargs)
        reuslt = func(*args,**kwargs)
        print(f"{name} returned {reuslt}")
        
        return reuslt
    return wrapper
@log_call
def add(a,b):
    return a + b
add(4,7)
add(a = 10, b=10)

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args,**kwargs)
        end = time.perf_counter()
        print(f"The funtion took {end - start} to print {result}")
        return result
    return wrapper
@log_call   #Stacking decorators changed the decorated func as wrapper in and identified as wrapper.The functools wraps decorator keeps the functions metadata and keep it consistent
@timer      #consequence the Fastapi makes its docs by reading the function name if the wraps is not used every function will be named as wrapper.
def test(name):
    time.sleep(2)
    return name
    
test("Sherry")
"""
def retry(times):
    def decorator(func):
        def wrapper(*arg, **kwargs):
            for i in range(times):
                try:
                    result = func(*arg, **kwargs)
                    if result:
                        return result
                except Exception as e:
                    raise e 
        return wrapper
    return decorator

clock = 0

@retry(times=3)
def test2():
    global clock
    clock += 1
    if clock < 3:
        raise ValueError("Boom")
    return "Ok"    
            
print(test2())
"""
def retry(times, on=(Exception,)):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)

                except on as e:
                    print(f"Attempt {attempt + 1} failed: {e}")

                    if attempt == times - 1:
                        raise

        return wrapper

    return decorator


calls = 0


@retry(times=3, on=(ValueError,))
def flaky():
    global calls

    calls += 1

    if calls < 3:
        raise ValueError("boom")

    return "ok"


print(flaky())