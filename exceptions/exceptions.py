class RaceDataNotFound(Exception):
    """
    """

    def __init__(self, message="No data found at url"):
        self.message = message
        super().__init__(self.message)
