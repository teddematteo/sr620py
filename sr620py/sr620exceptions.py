class SR620ReadException(Exception):
    """Raised when a read exception from SR620 occurs"""

    def __init__(self):
        super().__init__("An error occured while reading from the device")


class SR620WriteException(Exception):
    """Raised when a write exception from SR620 occurs"""

    def __init__(self):
        super().__init__("An error occured while writing on the device")


class SR620SizeException(Exception):
    """Raised when the user chooses a not valid number of samples"""

    def __init__(self,lst):
        super().__init__(f"The number of samples must be one of the following values: {str(lst)}")


class SR620ValueException(Exception):
    """Raised when one(or more) of the values set as parameters does not exist!"""

    def __init__(self):
        super().__init__("One(or more) of the values set as parameters does not exist!")