class Tools(object):
    @staticmethod
    def is_numeric(value):
        if str(value).isnumeric():
            return True
        else:
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
