class GarminConnectObjectError(Exception):
    """
    Exception raised when there is an error in the Garmin Connect API object
    on input or there as unexpected input.

    Attributes:
        property -- property which caused the error
        obj      -- full object
    """
    def __init__(self, property, obj):
        # type: (str, dict) -> None
        self.property = property
        self.obj = obj

    def __str__(self):
        return f'Missing "{self.property}" in the object. Full object:\n' \
               f'{self.obj}'


class GarminConnectNotImplementedError(Exception):
    """
    Exception raised when there is not implemented part for a object.
    """
    def __init__(self, property, value, obj):
        # type: (str, str, dict) -> None
        self.property = property
        self.value = value
        self.obj = obj

    def __str__(self):
        return f"'{self.property}' = '{self.value}' -> Not implemented. " \
               f"Object:\n{self.obj}"


class OwnFormatDataObjectError(Exception):
    """
    Exception raised when there is an error in the input file with our
    own format.

    Attributes:
        property -- property which caused the error
        obj      -- full object
    """
    def __init__(self, property, obj):
        # type: (str, dict) -> None
        self.property = property
        self.obj = obj

    def __str__(self):
        return f'Missing "{self.property}" in the object. Full object:\n' \
               f'{self.obj}'


class OwnFormatDataObjectNotImplementedError(Exception):
    """
    Exception raised when there is not implemented part for a object.
    """
    def __init__(self, property, value, obj):
        # type: (str, str, dict) -> None
        self.property = property
        self.value = value
        self.obj = obj

    def __str__(self):
        return f"'{self.property}' = '{self.value}' -> Not implemented. " \
               f"Object:\n{self.obj}"
