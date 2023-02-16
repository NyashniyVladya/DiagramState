
init python early in _0some_utils:
    """
    Небольшой набор констант и фукнционала, для облегчения работы.
    """

    import sys

    try:
        import __builtin__ as builtins
    except ImportError:
        import builtins

    VERSION = (1, 0, 0)

    PY3 = True
    if sys.version_info.major != 3:
        PY3 = False

    if PY3:
        unicode = builtins.str
        basestring = (builtins.str, builtins.bytes)
        xrange = builtins.range
        unichr = builtins.chr


    PHI = ((5. ** (1. / 2.)) - 1.) / 2.
    PHI, PHI2 = (1. - PHI), PHI

    def get_displayable(data):
        result = renpy.displayable(data)
        if not isinstance(result, renpy.display.core.Displayable):
            raise ValueError("{0!r} isn't a displayable.".format(data))
        return result

    def is_even(number):
        if (number % 2) == 0:
            return True
        return False
