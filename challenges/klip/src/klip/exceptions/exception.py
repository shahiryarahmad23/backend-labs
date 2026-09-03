
class InvalideRefreshToken(Exception):
    pass

class RevokedRefreshToken(Exception):
    pass

class ExpiredRefreshToken(Exception):
    pass