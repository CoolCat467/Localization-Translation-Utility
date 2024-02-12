#!/usr/bin/env python3
# TimeUtils

"""Utilities for Time"""

# Programmed by CoolCat467

__title__ = "Time Utils"
__author__ = "CoolCat467"
__version__ = "1.0.0"
__ver_major__ = 1
__ver_minor__ = 0
__ver_patch__ = 0

import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def timed(func: F) -> F:
    """Wrapper to time how long func takes"""

    @wraps(func)
    def time_func(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        stop = time.perf_counter()
        call_elapsed = stop - start
        print(f"\n{func.__name__} took {call_elapsed:.4f} seconds.\n")
        return result

    return cast(F, time_func)


C = TypeVar("C", bound=Callable[..., Awaitable[Any]])


def async_timed(func: C) -> C:
    """Wrapper to time how long func takes"""

    @wraps(func)
    async def time_func(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        stop = time.perf_counter()
        call_elapsed = stop - start
        print(f"\n{func.__name__} took {call_elapsed:.4f} seconds.\n")
        return result

    return cast(C, time_func)


def split_time(seconds: int) -> list[int]:
    """Split time into decades, years, months, weeks, days, hours, minutes, and seconds."""
    seconds = int(seconds)

    def mod_time(sec: int, num: int) -> tuple:
        """Return number of times sec divides equally by number, then remainder."""
        smod = sec % num
        return int((sec - smod) // num), smod

    ##values = (1, 60, 60, 24, 7, 365/12/7, 12, 10, 10, 10, 1000, 10, 10, 5)
    ##mults = {0:values[0]}
    ##for i in range(len(values)):
    ##    mults[i+1] = round(mults[i] * values[i])
    ##divs = list(reversed(mults.values()))[:-1]
    divs = (
        15768000000000000,
        3153600000000000,
        315360000000000,
        31536000000000,
        31536000000,
        3153600000,
        315360000,
        31536000,
        2628000,
        604800,
        86400,
        3600,
        60,
        1,
    )
    ret = []
    for num in divs:
        edivs, seconds = mod_time(seconds, num)
        ret.append(edivs)
    return ret


def combine_and(data: list[str]) -> str:
    """Join values of text, and have 'and' with the last one properly."""
    data = list(data)
    if len(data) >= 2:
        data[-1] = "and " + data[-1]
    if len(data) > 2:
        return ", ".join(data)
    return " ".join(data)


def format_time(seconds: int, single_title_allowed: bool = False) -> str:
    """Returns time using the output of split_time."""
    times = (
        "eons",
        "eras",
        "epochs",
        "ages",
        "millenniums",
        "centuries",
        "decades",
        "years",
        "months",
        "weeks",
        "days",
        "hours",
        "minutes",
        "seconds",
    )
    single = [i[:-1] for i in times]
    single[5] = "century"
    split = split_time(seconds)
    zip_idx_values = [(i, v) for i, v in enumerate(split) if v]
    if single_title_allowed:
        if len(zip_idx_values) == 1:
            index, value = zip_idx_values[0]
            if value == 1:
                return "a " + single[index]
    data = []
    for index, value in zip_idx_values:
        title = single[index] if abs(value) < 2 else times[index]
        data.append(str(value) + " " + title)
    return combine_and(data)


def run() -> None:
    """Run as main"""


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.")
    run()