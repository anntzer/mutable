from mutable import ref, ref_type, overloading

def test_simple():
    x = ref(1)
    assert x == 1
    assert (x << 2) == 2
    assert x == 2
    assert x + 1 == 3
    assert x.__add__.__doc__ == int.__add__.__doc__
    with overloading(False):
        assert (x << 0) == 2
        assert x == 2

    y = ref_type(int)()
    incr = lambda: y.__lshift__(1 + y)
    incr()
    assert y == 1

    assert isinstance(x, int)
    assert issubclass(type(x), int)

def test_change_type():
    class A(object): pass
    class B(object): pass
    x = ref(A())
    assert isinstance(x, A)
    assert not isinstance(x, B)
    assert issubclass(type(x), A)
    assert not issubclass(type(x), B)
    x << B()
    assert isinstance(x, B)
    assert not isinstance(x, A)
    assert issubclass(type(x), B)
    assert not issubclass(type(x), A)
