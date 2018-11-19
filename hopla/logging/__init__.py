import sys
import logging


def default_handler():
    """
    Creates a default stdout handler
    :return:
    """
    handler =  logging.StreamHandler(sys.stdout)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    return handler


def create_logger(*handlers, capture_warnings=None):
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("hopla")
    logger.setLevel(logging.INFO)

    if len(handlers) == 0:
        handlers = [default_handler()]

    # add handlers to logger object
    for handler in handlers:
        logger.addHandler(handler)

    if capture_warnings is None or capture_warnings:
        logging.captureWarnings(True)
    else:
        logging.captureWarnings(False)
    return logger


logger = create_logger()