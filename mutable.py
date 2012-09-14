"""Assignment as a Python expression through overloading of <<.
"""

from collections import namedtuple as _namedtuple
_Cfg = _namedtuple("_Cfg", ["overloaded", "value_field"])
import contextlib as _contextlib
import functools as _functools


overloading = True
overloaded = "__lshift__"
value_field = "__value"


def _setattr(**kwargs):
    """Sets attributes of the decorated object according to the given kwargs.
    """
    def decorator(obj):
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
    return decorator


@_contextlib.contextmanager
def overloading(new_value=True):
    """Context manager to temporarily set the value of `overloading` (by
    default to True).
    """

    global overloading
    old = overloading
    overloading = new_value
    try:
        yield
    finally:
        overloading = old


def _cls_name(typ):
    return "Ref_" + typ.__name__


def ref_type(typ):
    """Creates a mutable reference type with a single copy-constructor.

    `ref_type(typ)(obj)` is an object that behaves exactly like (i.e., has
    the same attributes, implements the same methods as, etc.) the object
    `obj`, except that the `<<` operator is redefined so that `x << y` assigns
    `y` as the new value for `x` (and returns `x`), if the module-level flag
    `overloading` is True.
    
    Actually, the module-level `overloaded` (defaulting to "__lshift__") and
    `value_field` (defaulting to "__value") strings respectively indicate the
    method that is overloaded for assignment, and the field where the wrapped
    object is stored.

    Modifying the type of (the contents of) `x` will fail if the old and the
    new types have different deallocators at the C-level.
    """

    obj = object()
    # We keep track of the value of `overloaded` and `value_field` for each
    # created class in case they change later.
    cfgs = {}

    def _define_specials(cls, typ):
        """Redefine all the special methods of `cls` using wrappers of the
        corresponding methods of `typ`.
        """

        cfg = cfgs[cls]
        exclude = ["__class__", "__doc__", "__module__",
                   "__new__", "__init__",
                   "__getattribute__", "__dict__", "__setattr__",
                   cfg.overloaded]
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
                        @_functools.wraps(attr,
                            assigned=set(_functools.WRAPPER_ASSIGNMENTS) &
                                     set(dir(attr)))
                        def wrapper(self, *args, **kwargs):
                            return attr(getattr(self, cfg.value_field),
                                        *args, **kwargs)
                        return wrapper
                    setattr(cls, name, _())
                else:
                    setattr(cls, name, attr)

    @_setattr(__name__=_cls_name(typ))
    class cls(typ, object):
        __doc__ = "A mutable reference to a {}.".format(typ.__name__)

        def __init__(self, value=obj):
            cfg = cfgs[type(self)]
            setattr(self, cfg.value_field, typ() if value is obj else value)

        def __getattribute__(self, name):
            cfg = cfgs[type(self)]
            if name in (cfg.value_field, cfg.overloaded):
                return object.__getattribute__(self, name)
            else:
                return getattr(object.__getattribute__(self, cfg.value_field), name)

        def __setattr__(self, name, value):
            cfg = cfgs[type(self)]
            if name == cfg.value_field:
                object.__setattr__(self, cfg.value_field, value)
                _define_specials(type(self), type(value))
            else:
                setattr(getattr(self, cfg.value_field), name, value)

    @_setattr(__name__=overloaded)
    def assign_value(self, other):
        """Assign a new value to the object.
        """
        cfg = cfgs[type(self)]
        if overloading:
            setattr(self, cfg.value_field, other)
            return self
        else:
            return getattr(getattr(self, cfg.value_field), cfg.overloaded)(other)

    setattr(cls, overloaded, assign_value)

    cfgs[cls] = _Cfg(overloaded, value_field)

    return cls


def ref(obj):
    """Creates a mutable reference initialized to obj, with type `type(obj)`.
    """
    return ref_type(type(obj))(obj)
