class InvalidCsvFile(Exception):
    def __init__(self):

        super().__init__('Csv file does not exists.')
