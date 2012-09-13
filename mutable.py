"""Assignment as a Python expression through overloading of <<.

See test_mutable.py for some examples.
"""

import contextlib
import functools


__overloading__ = True
_overloaded = "__lshift__"


@contextlib.contextmanager
def overloading(new_value=True):
    """Context manager to temporarily set the value of __overloading__
    (by default to True).
    """

    global __overloading__
    old = __overloading__
    __overloading__ = new_value
    try:
        yield
    finally:
        __overloading__ = old


def _cls_name(typ):
    return "Ref_" + typ.__name__


_value_field = "__value"


def _define_specials(cls, typ):
    """Redefine all the special methods of `cls` using wrappers of the
    corresponding methods of `typ`.
    """
    exclude = ["__class__", "__doc__", "__module__",
               "__new__", "__init__",
               "__getattribute__", "__dict__", "__setattr__",
               _overloaded]
    try:
        cls.__bases__ = (typ, object)
    except TypeError:
        raise TypeError(
            "Invalid change in the type of the contents of a reference.")
    for name in list(vars(cls).keys()):
        if (name.startswith("__") and name.endswith("__") and
            not name in exclude):
            delattr(cls, name)
    for name in dir(typ):
        if (name.startswith("__") and name.endswith("__") and
            not name in exclude):
            attr = getattr(typ, name)
            if callable(attr):
                def _(attr=attr):
                    @functools.wraps(attr,
                        assigned=set(functools.WRAPPER_ASSIGNMENTS) &
                                 set(dir(attr)))
                    def wrapper(self, *args, **kwargs):
                        return attr(getattr(self, _value_field),
                                    *args, **kwargs)
                    return wrapper
                setattr(cls, name, _())
            else:
                setattr(cls, name, attr)


def ref_type(typ):
    """Creates a mutable reference type with a single copy-constructor.

    `ref_type(typ)(obj)` is an object that behaves exactly like (i.e., has
    the same attributes, implements the same methods as, etc.) the object
    `obj`, except that the `<<` operator is redefined so that `x << y` assigns
    `y` as the new value for `x` (and returns `x`), if the module-level flag
    `__overloading__` is True.  (Actually, the module-level `_overloaded`
    variable, defaulting to `__lshift__`, indicates the method that is
    overloaded).

    Modifying the type of (the contents of) `x` will fail if the old and the
    new types have different deallocators at the C-level.
    """

    cls_name = _cls_name(typ)
    value_field = _value_field
    obj = object()

    class cls(typ, object):
        __doc__ = "A mutable version of {}.".format(typ.__name__)

        def __init__(self, value=obj):
            setattr(self, value_field, typ() if value is obj else value)

        def __getattribute__(self, name):
            if name in (value_field, _overloaded):
                return object.__getattribute__(self, name)
            else:
                return getattr(object.__getattribute__(self, value_field), name)

        def __setattr__(self, name, value):
            if name == value_field:
                object.__setattr__(self, value_field, value)
                _define_specials(type(self), type(value))
            else:
                setattr(getattr(self, value_field), name, value)

    cls.__name__ = cls_name

    def assign_value(self, other):
        """Assign a new value to the object.
        """
        if __overloading__:
            setattr(self, value_field, other)
            return self
        else:
            return getattr(getattr(self, value_field), _overloaded)(other)
    assign_value.__name__ = _overloaded
    setattr(cls, _overloaded, assign_value)

    return cls


def ref(obj):
    """Creates a mutable reference initialized to obj, with type `type(obj)`.
    """
    return ref_type(type(obj))(obj)
