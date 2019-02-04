from api_management.apps.analytics.csv_compressor import CsvCompressor
from api_management.apps.analytics.models import next_day_of
from api_management.apps.analytics.repositories.csv_file_repository import CsvFileRepository
from api_management.apps.common.utils import date_at_midnight, last_n_days


def check_csv_before_delete(csv_file):
    if csv_file is None:
        raise Exception('CsvFile to be deleted does not exists.')


def check_period_before_delete(from_time, to_time):
    if from_time >= to_time:
        raise Exception('Invalid date to delete files.')


class CsvCompressorAndRemover(CsvCompressor):

    def __init__(self, api_name):
        super().__init__(api_name)
        self.csv_file_repository = CsvFileRepository('analytics', self.api_name)

    def time_from_first_csv_file(self):
        csv_file = self.csv_file_repository.get_first()
        check_csv_before_delete(csv_file)

        return csv_file.date_from_name()

    def delete_zipped_files(self, days):
        from_time = self.time_from_first_csv_file()
        to_time = date_at_midnight(last_n_days(days))
        check_period_before_delete(from_time, to_time)

        while from_time < to_time:
            str_date = from_time.strftime('%Y-%m-%d')
            file_to_delete = self.csv_file_repository.get_by_file_name(str_date)
            self.csv_file_repository.delete(file_to_delete)
            from_time = next_day_of(from_time)
