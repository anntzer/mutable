from mutable import ref, overloading

def test_all():
    x = ref(int)(1)
    assert x == 1
    assert (x << 2) == 2
    assert x == 2
    assert x + 1 == 3
    assert x.__add__.__doc__ == int.__add__.__doc__
    with overloading(False):
        assert (x << 0) == 2
        assert x == 2

    y = ref(int)()
    incr = lambda: y << (1 + y)
    incr()
    assert y == 1

    assert isinstance(x, int)
    assert issubclass(type(x), int)
