from enum import Enum
import os
from datetime import datetime


class ResultFileType(Enum):
    ANIMATION = 'animation'
    METRICS = 'metrics'

class OutputFormat(Enum):
    JSON = 'json'
    CSV = 'csv'


def handle_file_path(result_type: ResultFileType,
                     output_format: OutputFormat,
                     file_name: str = None) -> str:
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if file_name is None:
        file_name = f"{result_type.value}_{date_str}"

    os.makedirs('output', exist_ok=True)
    return f"output/{result_type.value}_{file_name}_{date_str}.{output_format.value}"