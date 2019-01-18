from hopla.logging import logger
from hopla.logging.auto import LoggerLevel, When


def auto_log(when=None, log_method=None, exception_type=None, msg=None):
    """
    A decorator that logs before or after the method's execution
    :param msg: message to log
    :param aspect_logger: logger
    :param when: When enum
    :param log_method: method to call on the logger
    :param exception_type: when an exception_type exception is encountered it gets logged automatically before raising
    :return:
    """

    log_method = LoggerLevel.INFO if log_method is None or type(log_method) != LoggerLevel else log_method
    if log_method == LoggerLevel.NOTSET:
        when = When.NOTSET
    else:
        when = When.NOTSET if log_method is None or type(when) != When else when

    def decorator(*func):
        def wrapper(*args, **kwargs):
            def do_log(*l_args, **l_kwargs):
                try:
                    if log_method == LoggerLevel.CRITICAL:
                        method = logger.critical
                    elif log_method == LoggerLevel.FATAL:
                        method = logger.critical
                    elif log_method == LoggerLevel.ERROR:
                        method = logger.error
                    elif log_method == LoggerLevel.WARNING:
                        method = logger.warn
                    elif log_method == LoggerLevel.WARN:
                        method = logger.warning
                    elif log_method == LoggerLevel.INFO:
                        method = logger.info
                    elif log_method == LoggerLevel.DEBUG:
                        method = logger.debug
                    else:
                        return
                    full_message = "message: {msg}; *args: {args}; **kwargs: {kwargs}".format(
                        msg=msg,
                        args=l_args,
                        kwargs=l_kwargs) if msg is not None else "*args: {args}; **kwargs: {kwargs}".format(
                        args=l_args,
                        kwargs=l_kwargs)
                    method(full_message)
                except Exception as lex:
                    print(lex, l_args, l_kwargs)

            if when == When.BEFORE:
                if log_method != LoggerLevel.NOTSET:
                    do_log(*args, **kwargs)
                try:
                    return func[-1](*args, **kwargs)
                except Exception as ex:
                    if exception_type is not None:
                        if type(ex) == exception_type:
                            logger.exception(ex)
                    else:
                        logger.exception(ex)
                    raise
            elif when == When.AFTER:
                try:
                    val = func[-1](*args, **kwargs)
                except Exception as ex:
                    if exception_type is not None:
                        if type(ex) == exception_type:
                            logger.exception(ex)
                    else:
                        logger.exception(ex)
                    raise
                if log_method != LoggerLevel.NOTSET:
                    do_log(*args, **kwargs)
                return val
            else:
                try:
                    return func[-1](*args, **kwargs)
                except Exception as ex:
                    if exception_type is not None:
                        if type(ex) == exception_type:
                            logger.exception(ex)
                    else:
                        logger.exception(ex)
                    raise

        return wrapper

    return decorator
