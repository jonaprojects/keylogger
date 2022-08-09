# Exception classes for the client (which in this case, is the attacker)

class ServerInvalidResponseStatus(Exception):
    pass


class ServerInvalidContentType(Exception):
    pass


class ServerInvalidJSON(Exception):
    pass

