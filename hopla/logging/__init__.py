import logging
import sys


def default_handler():
    """
    Creates a default stdout handler
    :return:
    """
    handler = logging.StreamHandler(sys.stdout)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    return handler


def create_logger(*handlers, capture_warnings=None, level=None):
    """
    Creates a logging object and returns it
    """
    try:
        level = logging.INFO if level is None or level not in [logging.CRITICAL, logging.FATAL, logging.ERROR,
                                                               logging.WARNING, logging.WARN, logging.INFO,
                                                               logging.DEBUG,
                                                               logging.NOTSET] else level
        new_logger = logging.getLogger(__name__.split('.')[0])
        new_logger.setLevel(level)

        if len(handlers) == 0:
            handlers = [default_handler()]

        # add handlers to logger object
        for handler in handlers:
            new_logger.addHandler(handler)

        if capture_warnings is None or capture_warnings:
            logging.captureWarnings(True)
        else:
            logging.captureWarnings(False)
        return new_logger
    except Exception as ex:
        print(ex)
        new_logger = logging.getLogger()
        new_logger.addHandler([logging.NullHandler])
        return new_logger


logger = create_logger()


def logger_off():
    logger.info("Logs turned off.")
    logger.handlers.clear()


def logger_on():
    global logger
    logger = create_logger()
    logger.info("Logs turned on.")
