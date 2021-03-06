class RaceDataNotFoundException(Exception):
    """
    Raise this exception if no data available at specified url.
    """

    def __init__(self, message="No data found at url"):
        self.message = message
        super().__init__(self.message)


class MissingParametersException(Exception):
    """
    Raise this exception if a required parameter is absent.
    """

    def __init__(self, message="Woah, missing some parameters are we?"):
        self.message = message
        super().__init__(self.message)


class InsufficientParametersException(Exception):
    """
    Raise this exception if the required number of parameters is not passed.
    """

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)
