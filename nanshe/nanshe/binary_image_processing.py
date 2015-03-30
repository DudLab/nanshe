__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 16, 2014 23:21:43 EDT$"


# Generally useful and fast to import so done immediately.
import numpy

import scipy
import scipy.ndimage
import scipy.ndimage.filters

# Need in order to have logging information no matter what.
import debugging_tools


# Get the logger
logger = debugging_tools.logging.getLogger(__name__)


@debugging_tools.log_call(logger)
def binary_dilation(input_array, footprint, out=None):
    """
        Performs simple binary dilation on a bool array of arbitrary dimension.

        Args:
            input_array(numpy.ndarray):         the bool array to perform dilation on.
            footprint(numpy.ndarray):           the footprint to use for the kernel.
            out(numpy.ndarray):                 a place to store the result if provided. (optional)

        Returns:
            out(numpy.ndarray):                 Same as out if out was provided.

        >>> a = numpy.array([[ True,  True, False, False, False, False, False],
        ...                  [False, False, False, False, False, False, False],
        ...                  [False, False, False, False, False, False, False],
        ...                  [False, False, False, False, False, False, False],
        ...                  [False, False, False, False,  True, False, False],
        ...                  [False, False, False, False, False, False, False],
        ...                  [False, False, False, False, False, False, False]], dtype=bool)
        >>> b = numpy.zeros_like(a)

        >>> binary_dilation(a, numpy.ones(a.ndim*(3,), dtype=bool))
        array([[ True,  True,  True, False, False, False, False],
               [ True,  True,  True, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False, False, False, False, False]], dtype=bool)

        >>> binary_dilation(a, numpy.ones(a.ndim*(3,), dtype=bool), out=b)
        array([[ True,  True,  True, False, False, False, False],
               [ True,  True,  True, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False, False, False, False, False]], dtype=bool)
        >>> b
        array([[ True,  True,  True, False, False, False, False],
               [ True,  True,  True, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False, False, False, False, False]], dtype=bool)

        >>> binary_dilation(a, numpy.ones(a.ndim*(3,), dtype=bool), out=a)
        array([[ True,  True,  True, False, False, False, False],
               [ True,  True,  True, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False, False, False, False, False]], dtype=bool)
        >>> a
        array([[ True,  True,  True, False, False, False, False],
               [ True,  True,  True, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False,  True,  True,  True, False],
               [False, False, False, False, False, False, False]], dtype=bool)
    """

    assert issubclass(input_array.dtype.type, (bool, numpy.bool_))

    if out is None:
        out = input_array.copy()
    elif id(input_array) != id(out):
        assert issubclass(out.dtype.type, (bool, numpy.bool_))

    scipy.ndimage.filters.maximum_filter(input_array, footprint=footprint, output=out)

    return(out)


@debugging_tools.log_call(logger)
def binary_erosion(input_array, footprint, out = None):
    """
        Performs simple binary erosion on a bool array of arbitrary dimension.

        Args:
            input_array(numpy.ndarray):         the bool array to perform erosion on.
            footprint(numpy.ndarray):           the footprint to use for the kernel.
            out(numpy.ndarray):                 a place to store the result if provided. (optional)

        Returns:
            out(numpy.ndarray):                 Same as out if out was provided.

        >>> a = numpy.array([[ True,  True,  True, False, False, False,  True],
        ...                  [ True,  True,  True, False, False,  True,  True],
        ...                  [False, False, False, False, False, False, False],
        ...                  [False, False, False,  True,  True,  True, False],
        ...                  [False,  True, False,  True,  True,  True, False],
        ...                  [False,  True, False,  True,  True,  True, False],
        ...                  [False, False, False, False, False, False,  True]], dtype=bool)
        >>> b = numpy.zeros_like(a)

        >>> binary_erosion(a, numpy.ones(a.ndim*(3,), dtype=bool))
        array([[ True,  True, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False,  True, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False]], dtype=bool)

        >>> binary_erosion(a, numpy.ones(a.ndim*(3,), dtype=bool), out=b)
        array([[ True,  True, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False,  True, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False]], dtype=bool)
        >>> b
        array([[ True,  True, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False,  True, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False]], dtype=bool)

        >>> binary_erosion(a, numpy.ones(a.ndim*(3,), dtype=bool), out=a)
        array([[ True,  True, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False,  True, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False]], dtype=bool)
        >>> a
        array([[ True,  True, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False,  True, False, False],
               [False, False, False, False, False, False, False],
               [False, False, False, False, False, False, False]], dtype=bool)
    """

    assert issubclass(input_array.dtype.type, (bool, numpy.bool_))

    if out is None:
        out = input_array.copy()
    elif id(input_array) != id(out):
        assert issubclass(out.dtype.type, (bool, numpy.bool_))

    scipy.ndimage.filters.minimum_filter(input_array, footprint=footprint, output=out)

    return(out)