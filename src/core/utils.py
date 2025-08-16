import time
from enum import Enum


class ResultFileType(Enum):
    ANIMATION = 'animation'
    METRICS = 'metrics'

class OutputFormat(Enum):
    JSON = 'json'
    CSV = 'csv'


def handle_file_path(self, result_type: ResultFileType,
                      output_format: OutputFormat,
                      file_name: str = None ) -> str:

    if file_name is None:
        timestamp = int(time.time())
        file_name = f"{self.algorithm_type.value}_{timestamp}"

    return f"output/{result_type.value}_{file_name}.{output_format.value}"