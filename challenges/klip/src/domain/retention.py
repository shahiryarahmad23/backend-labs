class Retention():
    def __init__(self,bytes,plan):
       self.bytes = bytes
       self.plan = plan
    
    def __add__(self, other):
        if self.plan != other.plan:
            raise ValueError("Cannot combine different plans")

        return Retention(self.bytes + other.bytes, self.plan)


    def __eq__(self, other):
        if not isinstance(other, Retention):
            return NotImplemented

        return self.bytes == other.bytes and self.plan == other.plan


    def __lt__(self, other):
        if not isinstance(other, Retention):
            return NotImplemented

        return self.bytes < other.bytes


    def __hash__(self):
        return hash((self.bytes, self.plan))
        