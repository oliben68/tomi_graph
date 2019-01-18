import inspect
import weakref

from pydispatch import dispatcher

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


def disconnect_handler(signal=None, handler=None):
    if signal is not None and handler is not None:
        dispatcher.disconnect(handler, signal=signal, sender=dispatcher.Any)
    elif signal is None and handler is not None:
        ref_ids = [k for k, v in dispatcher.connections.items() if
                   any([val == weakref.ref(handler) or val == handler for val in
                        [item for sublist in list(v.values()) for item in
                         sublist]])]
        for ref_id in ref_ids:
            new_refs = {s: refs for s, refs in
                        {s: [ref for ref in refs if ref != handler and ref != weakref.ref(handler)] for
                         s, refs in dispatcher.connections[ref_id].items()}.items() if len(refs) > 0}

            if len(new_refs) == 0:
                del dispatcher.connections[ref_id]
            else:
                dispatcher.connections[ref_id] = new_refs
    elif signal is not None and handler is None:
        ref_ids = [k for k, v in dispatcher.connections.items() if signal in list(v.keys())]
        for ref_id in ref_ids:
            new_refs = {s: handlers for s, handlers in dispatcher.connections[ref_id].items() if s != signal}

            if len(new_refs) == 0:
                del dispatcher.connections[ref_id]
            else:
                dispatcher.connections[ref_id] = new_refs

    else:
        return


def send_message(message, signal, sender=None):
    dispatcher.send(message=message, signal=signal, sender=sender if sender is not None else object())
