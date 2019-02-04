class InvalidDateRange(Exception):
    def __init__(self):

        super().__init__('Range date is invalid.')
