class SR620ReadException(Exception):
    """Raised when a read exception from SR620 occurs"""

    def __init__(self,message,errors=None):
        super().__init__(message)
        self.errors = errors

    def __str__(self):
        if self.errors:
            return f"{self.message} (Errors: {self.errors})"
        return self.message
    
class SR620WriteException(Exception):
    """Raised when a write exception from SR620 occurs"""

    def __init__(self,message,errors=None):
        super().__init__(message)
        self.errors = errors

    def __str__(self):
        if self.errors:
            return f"{self.message} (Errors: {self.errors})"
        return self.message
    
class SR620SizeException(Exception):
    """Raised when the user chooses a not valid number of samples"""

    def __init__(self,lst):
        super().__init__(f"The number of samples must be one of the following values: {str(lst)}")