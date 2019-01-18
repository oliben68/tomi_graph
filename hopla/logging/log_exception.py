def log_exception(logger, exception_type=None):
    """
    A decorator that wraps a function and logs exceptions should one occur
    :param logger: logger to which log the exception
    :param exception_type: only logs exceptions when this type of exception is raised; None all are logged
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                if exception_type is not None:
                    if type(ex) == exception_type:
                        logger.exception(ex)
                else:
                    logger.exception(ex)
                raise

        return wrapper

    return decorator
