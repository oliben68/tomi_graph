def self_reset_finalizer(*args, **kwargs):
    kwargs["relationship"].__reset__()


def preserve_entity_finalizer(*args, **kwargs):
    kwargs["safe"][kwargs["property"]] = kwargs["value"]
