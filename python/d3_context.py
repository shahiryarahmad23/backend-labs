import sys
from contextlib import contextmanager

def count_up_to(n):
    for i in range(n):
        yield i
    
count = count_up_to(5)
print(count)
for i in count:
    print(i)
print(sys.getsizeof([i for i in range(1_000_000)]))
print(sys.getsizeof((i for i in range(1_000_000))))

@contextmanager
def fake_conn():
    names = []
    print("Connection open")
    try:
        yield names
    finally:
        print("Connection closed")
        
@contextmanager
def fake_conn_raise():
    names = []
    print("Connection open")
    yield names
    print("Connection closed")

with fake_conn() as c:
    for i in range(3):
        n = input("Enter a name -> ")
        c.append(n)
    print(c)
    
with fake_conn_raise() as c:
    raise ValueError("Boom")
    
class FakeConn:
    def __init__(self,names : list):
        self.data = names
    
    def __enter__(self):
        print("Connected")
        return self
    
    def __exit__(self,exc_type,exc_value,traceback):
        print("Closing the session")
        print(exc_type,exc_value,traceback)
    
naming = []    
with FakeConn(naming) as c:
    for i in range(3):
        n = input("Enter a name -> ")
        c.data.append(n)
    print(c.data)
    
with FakeConn(naming) as c:
    raise ValueError("Boom")