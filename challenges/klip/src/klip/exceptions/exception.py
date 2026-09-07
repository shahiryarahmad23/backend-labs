class InvalideRefreshToken(Exception):
    pass


class RevokedRefreshToken(Exception):
    pass


class ExpiredRefreshToken(Exception):
    pass


class ExpiredSnippet(Exception):
    pass


class PrivateSnippet(Exception):
    pass


class SnippetNotFound(Exception):
    pass


class SnippetForbidden(Exception):
    pass
