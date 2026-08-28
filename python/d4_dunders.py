class Money:
    def __init__(self,amount,currency):
        self.amount = amount
        self.currency = currency
    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"
    def __str__(self):
        return f"The amount is {self.amount} of currency {self.currency}"
    def __eq__(self , others):
        if not isinstance(others,Money):
            return NotImplemented            
        return self.amount == others.amount and self.currency == others.currency
    def __lt__(self,other):
        if not isinstance(other,Money):
            return NotImplemented
        if self.currency == other.currency:
            return self.amount < other.amount
        else:
            raise ValueError(f"You are trying to compare {self.currency} with {other.currency}")
    def __add__(self,other):
        if not isinstance(other,Money):
            return NotImplemented
        if self.currency == other.currency:
            return Money(self.amount + other.amount,self.currency)
        else:
            raise ValueError(f"You are trying to sum {self.currency} with {other.currency}")
    def __hash__(self):
        return hash((self.amount,self.currency))
        
    

m1 = Money(2000,"PKR")
m2 = Money(2000,"PKR")
m3 = Money(3000,"INR")

s = {m1}

m1.amount = 9999


print(m1 in s)
