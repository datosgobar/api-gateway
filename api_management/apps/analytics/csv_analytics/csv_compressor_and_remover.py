from api_management.apps.analytics.csv_analytics.csv_compressor import CsvCompressor
from api_management.apps.analytics.exceptions.invalid_csv_file import InvalidCsvFile
from api_management.apps.analytics.models import next_day_of
from api_management.apps.common.utils import date_at_midnight, last_n_days


def check_csv_before_delete(csv_file):
    if csv_file is None:
        raise InvalidCsvFile()


class CsvCompressorAndRemover(CsvCompressor):

    def time_from_first_csv_file(self):
        csv_file = self.csv_file_repository.get_first()
        check_csv_before_delete(csv_file)

        return csv_file.date_from_name()

    def delete_zipped_files(self, days):
        from_time = self.time_from_first_csv_file()
        to_time = date_at_midnight(last_n_days(days))
        if from_time >= to_time:
            return

        while from_time < to_time:
            str_date = from_time.strftime('%Y-%m-%d')
            file_to_delete = self.csv_file_repository.get_by_file_name(str_date)
            if file_to_delete is not None:
                self.csv_file_repository.delete(file_to_delete)
            from_time = next_day_of(from_time)
