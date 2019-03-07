import logging
import sys

from tomi_config import CONFIG

from tomi_base.shared.meta_singleton import MetaSingleton


class Slf4p(metaclass=MetaSingleton):
    def __init__(self):
        self._loggers = {}

    def __call__(self, cls):
        if cls.__module__ not in self._loggers.keys():
            logger = logging.getLogger(cls.__module__)
            level = CONFIG.LOG_CONFIG["level"]
            if not isinstance(level, int):
                try:
                    level = eval(level)
                except:
                    level = logging.CRITICAL
            logger.setLevel(level)

            # create console handler and set level to debug
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter(CONFIG.LOG_CONFIG["format"])

            # add formatter to ch
            ch.setFormatter(formatter)

            # add ch to logger
            logger.addHandler(ch)
            self._loggers[cls.__module__] = logger

        cls_logger = self._loggers[cls.__module__]

        return type(cls.__name__, (cls,), {"log": property(lambda s: cls_logger)})
