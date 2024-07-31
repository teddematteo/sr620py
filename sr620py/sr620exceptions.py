class SR620ReadException(Exception):
    """Raised when a read exception from SR620 occurs"""

    def __init__(self,message,errors=None):
        super().__init__(message)
        self.errors = errors

    def __str__(self):
        if self.errors:
            return f"{self.message} (Errors: {self.errors})"
        return self.message