from inspect import signature

from pydantic import validator as pydantic_validator


def validator(*args, **kwargs):
    def decorator(func):
        def wrapped_validator(cls, v, values, field, config):
            if field.allow_none and v is None:
                return v

            func_args = list(signature(func).parameters.keys())
            v_kwargs = {'values': values, 'field': field, 'config': config}
            call_kwargs = {k: v_kwargs[k] for k in func_args[2:]}

            return func(cls, v, **call_kwargs)

        kwargs['allow_reuse'] = True
        f_cls = pydantic_validator(*args, **kwargs)(wrapped_validator)

        return f_cls

    return decorator
