# файл для настройки логгирования, по умолчанию создает два файла для разных уровней огирования,
# так же часть информации печатается в консоль
import logging

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


def get_warning_file_handler():
    file_handler = logging.FileHandler("logs/only_warnings.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_all_file_handler():
    file_handler = logging.FileHandler("logs/all_info.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_warning_file_handler())
    logger.addHandler(get_all_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
