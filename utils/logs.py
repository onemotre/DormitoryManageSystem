import os
import logging

from config import LOG_DIR_NAME


def set_up_logger(name: str, level: object = logging.ERROR) -> object:
    log_dirname = LOG_DIR_NAME
    if not os.path.exists(log_dirname):
        os.makedirs(log_dirname)
    log_file = os.path.join(log_dirname, f"{name}.log")
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    logger.addHandler(handler)

    return logger


System_Logger = set_up_logger(name="System", level=logging.ERROR)
Data_Logger_history = set_up_logger(name="Data_Logger", level=logging.INFO)


if __name__ == "__main__":
    set_up_logger("Test_logger")
