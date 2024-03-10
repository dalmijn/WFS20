"""Custom error handling."""


class WFSError(Exception):
    """General WFS error."""

    def __init__(self, base, code, message):
        self.base = base
        self.code = code
        self.message = message
        super(WFSError, self).__init__(self.base)

    def __str__(self):
        return f"{self.base} => {self.message} (status_code: {self.code})"


class WFSInternalError(Exception):
    """Internal error from the WFS20 package."""

    def __init__(self, base, message):
        self.base = base
        self.message = message
        super(WFSInternalError, self).__init__(self.base)

    def __str__(self):
        return f"{self.base} => {self.message}"


class AUTHError(Exception):
    """Authentication error."""

    def __init__(self, msg):
        self.base = "Wrong authentication credentials."
        self.msg = msg
        super(AUTHError, self).__init__(self.base)

    def __str__(self):
        return f"{self.base} => {self.msg}"
