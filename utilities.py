"""Utility module with various helper functions.
Includes functions for safe min/max, linear interpolation, clamping, bounds checking, and matrix multiplication.
Contain:safemax,safemin,lerp,strictlerp,clerp,clamp,boundscheck,matrixmul

See function docstrings for details.

NOTE: please do not try to pass generators to truecopy, safemax or safemin."""

from collections.abc import Iterable
import copy as dcopy
import itertools
import types

def truecopy(x):
    "copies x."
    if isinstance(x, (int, float, str, bool, type(None))): return x # immutable types
    if isinstance(x, (types.GeneratorType, types.AsyncGeneratorType)):
        x = "<GeneratorType>"
        raise TypeError(x + " is not supported")
    try:
        return dcopy.deepcopy(x)
    except Exception:
        try:
            return dcopy.copy(x)
        except Exception:
            try:
                return x.copy()
            except Exception:
                try:
                    return itertools.tee(x,1)[0] # this copies the gen so we dont exhaust it
                except Exception:
                    raise ValueError("could not copy " + repr(x))


def safemax(iterable: Iterable) -> float:
    """Return the maximum of an iterable, or 0 if the iterable is empty."""
    if not isinstance(iterable, Iterable): raise ValueError("iterable must be an iterable, got " + repr(iterable))
    if not all(isinstance(x, (int, float)) for x in truecopy(iterable)): raise ValueError("iterable must contain numbers, got " + repr(iterable)) # in-case its a generator so we dont exhause it accidentally
    try:
        return max(truecopy(iterable))
    except ValueError:
        return 0

def safemin(iterable: Iterable) -> float:
    """Return the minimum of an iterable, or 0 if the iterable is empty."""
    if not isinstance(iterable, Iterable): raise ValueError("iterable must be an iterable, got " + repr(iterable))
    if not all(isinstance(x, (int, float)) for x in truecopy(iterable)): raise ValueError("iterable must contain numbers, got " + repr(iterable))
    try:
        return min(iterable)
    except ValueError:
        return 0
    
def lerp(a: float|int, b: float|int, t: float|int) -> float:
    """Linear interpolation between a and b with factor t in [0, 1]."""
    if not isinstance(a, (int, float)): raise ValueError("a must be a number, got " + repr(a))
    if not isinstance(b, (int, float)): raise ValueError("b must be a number, got " + repr(b))
    if not isinstance(t, (int, float)): raise ValueError("t must be a number, got " + repr(t))
    return a + (b - a) * t

def strictlerp(a: float|int, b: float|int, t: float|int) -> float:
    """Linear interpolation between a and b with factor t in [0, 1]. Raises ValueError if t is out of bounds."""
    if not isinstance(t, (int, float)): raise ValueError("t must be a number, got " + repr(t))
    if t < 0 or t > 1:
        raise ValueError("t must be in [0, 1], got " + repr(t))
    return lerp(a, b, t)

def clerp(a: list|tuple, b: list|tuple, t: float) -> list:
    """Color interpolation between colors a and b with factor t in [0, 1]."""
    if not isinstance(a, (tuple, list)): raise ValueError("a must be a tuple or list, got " + repr(a))
    if not isinstance(b, (tuple, list)): raise ValueError("b must be a tuple or list, got " + repr(b))
    if len(a) != 3 or len(b) != 3: raise ValueError("a and b must be of length 3, got " + repr(a) + " and " + repr(b))
    if not all(isinstance(x, (int, float)) for x in a): raise ValueError("a must contain numbers, got " + repr(a))
    if not all(isinstance(x, (int, float)) for x in b): raise ValueError("b must contain numbers, got " + repr(b))
    if not isinstance(t, (int, float)): raise ValueError("t must be a number, got " + repr(t))
    return [strictlerp(a[i], b[i], t) for i in range(3)]


def clamp(value: float|int, min_value: float|int, max_value: float|int) -> float|int:
    """Clamp value to the range [min_value, max_value]."""
    if not isinstance(value, (int, float)): raise ValueError("value must be a number, got " + repr(value))
    if not isinstance(min_value, (int, float)): raise ValueError("min_value must be a number, got " + repr(min_value))
    if not isinstance(max_value, (int, float)): raise ValueError("max_value must be a number, got " + repr(max_value))
    if min_value > max_value: raise ValueError("min_value must be <= max_value, got " + repr(min_value) + " and " + repr(max_value))
    return max(min_value, min(value, max_value))

def boundscheck(value: float|int, min_value: float|int, max_value: float|int) -> bool:
    """Check if value is within [min_value, max_value]."""
    if not isinstance(value, (int, float)): raise ValueError("value must be a number, got " + repr(value))
    if not isinstance(min_value, (int, float)): raise ValueError("min_value must be a number, got " + repr(min_value))
    if not isinstance(max_value, (int, float)): raise ValueError("max_value must be a number, got " + repr(max_value))
    if min_value > max_value: raise ValueError("min_value must be <= max_value, got " + repr(min_value) + " and " + repr(max_value))

    return min_value <= value <= max_value

def matrixmul(A: list[list[float|int]], B: list[list[float|int]]) -> list[list[float|int]]:
    """Multiply two matrices A and B."""
    if not isinstance(A, list) or not all(isinstance(row, list) for row in A):
        raise ValueError("A must be a 2D list, got " + repr(A))
    if not isinstance(B, list) or not all(isinstance(row, list) for row in B):
        raise ValueError("B must be a 2D list, got " + repr(B))
    if len(A) == 0 or len(B) == 0:
        raise ValueError("A and B must be non-empty")
    if len(A[0]) != len(B):
        raise ValueError("Number of columns in A must equal number of rows in B, got " + repr(len(A[0])) + " and " + repr(len(B)))
    if not all(len(row) == len(A[0]) for row in A):
        raise ValueError("A must be homogeneous (i.e. all rows same length), got " + repr([len(row) for row in A]))
    if not all(len(row) == len(B[0]) for row in B):
        raise ValueError("B must be homogeneous (i.e. all rows same length), got " + repr([len(row) for row in B]))

    result = [[0] * len(B[0]) for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                result[i][j] += A[i][k] * B[k][j]
    return result