from pydispatch import dispatcher
import inspect

from hopla.core.events.exceptions import HandlerArgsCountException
from hopla.core.events.signals import Signals


def connect(handler, signal, sender=None):
    if not callable(handler):
        raise TypeError("Handler should be callable.")
    if len(inspect.getfullargspec(handler).args) == 0:
        raise HandlerArgsCountException("The the handler should at least have one argument.")

    if type(signal) != Signals:
        raise TypeError("The signal should be of type {signal}.".format(signal=Signals.__name__))

    dispatcher.connect(handler, signal=signal, sender=sender if sender is not None else dispatcher.Any)
