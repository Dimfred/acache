def make_key(*args, **kwargs):
    safe_args = [make_safe(arg) for arg in args]
    safe_kwargs = list(make_safe(kwargs))
    key = tuple(safe_args + safe_kwargs)

    return key


def make_safe(args):
    if isinstance(args, dict):
        res = []
        for k, v in args.items():
            res.append((k, make_safe(v)))
        res = tuple(sorted(res))
    elif isinstance(args, (list, tuple, set)):
        res = (make_safe(arg) for arg in args)
        res = tuple(sorted(res))
    else:
        res = args

    return res
