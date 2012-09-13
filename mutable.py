"""Assignment as a Python expression through overloading of <<.

See test_mutable.py for some examples.
"""

import contextlib
import functools


__overload_lshift__ = True


@contextlib.contextmanager
def overloading(new_value=True):
    """Context manager to temporarily set the value of __overload_lshift__
    (by default to True).
    """

    global __overload_lshift__
    old = __overload_lshift__
    __overload_lshift__ = new_value
    try:
        yield
    finally:
        __overload_lshift__ = old


def ref(typ):
    """Creates a mutable version of a type.
    
    `ref(typ)(*args, **kwargs)` is an object that behaves exactly like (i.e.,
    has the same attributes and implements the same methods as) the object
    `typ(*args, **kwargs)`, except that the `<<` operator is overloaded so that
    `x << y` assigns `y` as the new value for `x` (and returns `x`), if the
    module-level flag __overload_lshift__ is True.  Note that no type-checking
    is done, i.e. `typ` is only present to indicate where to find attribute and
    method definitions.
    """

    cls = type("Ref_" + typ.__name__,
               (typ, object,),
               {"__doc__": "A mutable version of {}.".format(typ.__name__)})

    value_field = "_{}__value".format(cls.__name__)

    for name in dir(int):
        if name in ["__class__", "__doc__",
                    "__new__", "__init__",
                    "__getattribute__", "__setattr__"]:
            continue
        attr = getattr(typ, name)
        if callable(attr):
            def _(attr=attr):
                @functools.wraps(attr,
                                 assigned=set(functools.WRAPPER_ASSIGNMENTS) &
                                          set(dir(attr)))
                def wrapper(self, *args, **kwargs):
                    return attr(getattr(self, value_field), *args, **kwargs)
                return wrapper
            setattr(cls, name, _())
        else:
            setattr(cls, name, attr)

    obj = object()
    cls.__init__ = (lambda self, value=obj:
                    setattr(self, value_field, typ() if value is obj else value))

    def lshift(self, other):
        """Assign a new value to the object.
        """
        if __overload_lshift__:
            setattr(self, value_field, other)
            return self
        else:
            return getattr(self, value_field) << other
    cls.__lshift__ = lshift

    return cls
