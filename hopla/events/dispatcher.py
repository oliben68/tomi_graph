from pydispatch import dispatcher
import inspect

from hopla.events.exceptions import HandlerArgsCountException
from hopla.events.signals import Signals


def connect_handler(handler, signal, sender=None):
    if not callable(handler):
        raise TypeError("Handler should be callable.")
    if len(inspect.getfullargspec(handler).args) == 0:
        raise HandlerArgsCountException("The the handler should at least have one argument.")

    if type(signal) != Signals:
        raise TypeError("The signal should be of type {signal}.".format(signal=Signals.__name__))

    dispatcher.connect(handler, signal=signal, sender=sender if sender is not None else dispatcher.Any)


def send_message(message, signal, sender=None):
    dispatcher.send(message=message, signal=signal, sender=sender if sender is not None else object())