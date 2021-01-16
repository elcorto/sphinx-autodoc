"""
Module level

doc string.
"""


def func(x=None):
    """
    Function `func` here, hi!

    Parameters
    ----------
    x : array, optional
        Important numbers

    Returns
    -------
    y : array

    See Also
    --------
    :func:`numpy.bincount`

    Notes
    -----
    Here be notes and math :math:`\int\sin(x) dx`

    Examples
    --------
    >>> import gryyzz, numpy as np
    >>> foo(1.0)
    1.234
    """
    return 3.1


class Foo:
    """Class Foo doc string.

    This class provides amazing foo!11!

    Examples
    --------
    >>> class Foo:
    ...     print("class doc string example")

    Notes
    -----
    Note the notes. Always.
    """

    # Class level doc strings get picked up only when attrs are defined after
    # it.
    attr = 1.23

    def __init__(self, x, y):
        """
        Parameters
        ----------
        x : array
        y : array

        Examples
        --------
        >>> class Foo:
        ...     print("__init__ doc string example")
        """
        self.x = x
        self.y = y

    def meth(self):
        """Class Foo method doc string.

        Returns
        -------
        float
        """
        return self.x

    def other_meth(self, k):
        """Class Foo other method doc string.

        Parameters
        ----------
        k : array
            Array with k values. This is going to be a longish explanation, so
            we better come up with some non-trivial facts here! Let's hope this
            is already enough. Oh, yes, also some rst math :math:`\int\sin(x)
            dx` here, too.

        Returns
        -------
        x : float
            accurately calculated stuff, scalar
        """
        return self.x


class Bar(Foo):
    def meth(self):
        """Class Bar method doc string.
        """
        return self.y

    def __call__(self, arg):
        return arg + self.x


class Baz:
    pass
