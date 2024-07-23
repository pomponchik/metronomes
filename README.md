![logo](https://raw.githubusercontent.com/pomponchik/metronomes/main/docs/assets/logo_2.svg)

[![Downloads](https://static.pepy.tech/badge/metronomes/month)](https://pepy.tech/project/metronomes)
[![Downloads](https://static.pepy.tech/badge/metronomes)](https://pepy.tech/project/metronomes)
[![codecov](https://codecov.io/gh/pomponchik/metronomes/graph/badge.svg?token=Ee3UuDakQ1)](https://codecov.io/gh/pomponchik/metronomes)
[![Lines of code](https://sloc.xyz/github/pomponchik/metronomes/?category=code)](https://github.com/boyter/scc/)
[![Hits-of-Code](https://hitsofcode.com/github/pomponchik/metronomes?branch=main)](https://hitsofcode.com/github/pomponchik/metronomes/view?branch=main)
[![Test-Package](https://github.com/pomponchik/metronomes/actions/workflows/tests_and_coverage.yml/badge.svg)](https://github.com/pomponchik/metronomes/actions/workflows/tests_and_coverage.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/metronomes.svg)](https://pypi.python.org/pypi/metronomes)
[![PyPI version](https://badge.fury.io/py/metronomes.svg)](https://badge.fury.io/py/metronomes)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This library offers the easiest way to run regular tasks. Just give it a function and tell it how many seconds you need to run it, then step back and don't interfere. For all its simplicity, there are:

- 📜 Logging the start and end of each operation.
- 🛡️ Error escaping. But not when you don't even know about the errors, but again - with detailed logging.
- ⇆ Thread safety.
- ❌ Support for [cancellation tokens](https://github.com/pomponchik/cantok).


## Table of contents

- [**Quick start**](#quick-start)
- [**Why?**](#why)
- [**Basic usage**](#basic-usage)
- [**Use it as a context manager**](#use-it-as-a-context-manager)
- [**Logging**](#logging)
- [**Error escaping**](#error-escaping)
- [**Working with Cancellation Tokens**](#working-with-cancellation-tokens)
- [**How to set a time limit**](#how-to-set-a-time-limit)


## Quick start

Install it:

```bash
pip install metronomes
```

And use:

```python
from time import sleep
from metronomes import Metronome

metronome = Metronome(0.2, lambda: print('go!'))

metronome.start()
sleep(1)
metronome.stop()
#> go!
#> go!
#> go!
#> go!
#> go!
```

You can also quickly try out this and other packages without having to install using [instld](https://github.com/pomponchik/instld).


## Why?

A [metronome](https://en.wikipedia.org/wiki/Metronome) is a special device that musicians often use. It looks something like this (if you are interested in how it works, I recommend watching the [video on YouTube](https://youtu.be/LvBEyyuVu60?si=NtaNSw0Xsv5ZPEKr)):

![metronome](https://raw.githubusercontent.com/pomponchik/metronomes/develop/docs/assets/image_2.gif)

Its task is to produce sounds regularly and monotonously, which is very convenient if you want to develop a sense of rhythm. Unlike a person for whom strict rhythmicity is unusual, the metronome counts down time very accurately and therefore is used as a "guide" to which other rhythmic actions that we want to do are attached, whether it's tapping on a drum or pressing keys.

When we write programs, we also sometimes want some action to be performed regularly. And sometimes it happens that it may take a different amount of time, but we need the next action to start on time. This is exactly the task this library solves. When you call the `start()` method on a metronome object, it starts calling the function you passed once in a certain period of time. This happens in a separate specially created thread, so you can use these function calls to orchestrate some other actions in the main thread or even in several different threads.

At the same time, it may be important to you that even if in some cases the function does not work well and raises exceptions, in general the metronome continues to work, and after a certain time it will try to call this function again, and will not break at the first exception. After all, it would be strange if your real metronome went silent when you made a mistake in the rhythm that you are tapping on the drum, right? You may also want the errors that have occurred not to be lost, but to be recorded in your log. This library also provides all these amenities.


## Basic usage

The metronome object has 2 main methods: `start()` and `stop()`. Calling the `start()` method starts an additional thread, inside which the passed function starts running regularly in the loop. At the same time, the main thread can continue and, when it's necessary, stop the metronome calling the `stop()` method. Often, a metronome can be used for background notifications that are called during the execution of other code:

```python
from metronomes import Metronome

metronome = Metronome(0.001, lambda: print('An another function in progress...'))

metronome.start()
another_function()
metronome.stop()
#> An another function in progress...
#> An another function in progress...
#> An another function in progress...
```

Instead of manually starting and stopping the metronome, you can also use the [context manager mode](#use-it-as-a-context-manager).

The metronome object from this library cannot be used twice. If you started it once and then stopped it, you can't do it again:

```python
metronome = Metronome(0.2, lambda: print('go!'))

metronome.start()
sleep(0.2)
metronome.stop()
#> go!
metronome.start()
#> ...
#> metronomes.errors.RunStoppedMetronomeError: Metronomes are disposable, you cannot restart a stopped metronome.
```


## Use it as a context manager

We recommend using a metronome exclusively in the context manager mode, without "manual" start and stop:

```python
from time import sleep
from metronomes import Metronome

with Metronome(0.2, lambda: print('go!')):
    sleep(1)
#> go!
#> go!
#> go!
#> go!
#> go!
```

In this case, it is guaranteed that the metronome will be completed correctly after the end of the code block and will not remain "hanging" in a separate thread. Even if an error occurs in the block.


## Logging

In order for events inside the metronome to start logging, you need to pass the logger object there:

```python
import logging
from time import sleep
from metronomes import Metronome

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('logger_name')
metronome = Metronome(0.2, lambda: print('go!'), logger=logger)

metronome.start()
sleep(1)
metronome.stop()
#> 2024-04-18 19:38:42,910 [INFO] The metronome starts...
#> 2024-04-18 19:38:42,910 [DEBUG] The beginning of the execution of callback "<lambda>".
#> go!
#> 2024-04-18 19:38:42,910 [DEBUG] Callback "<lambda>" has been successfully completed.
#> 2024-04-18 19:38:43,115 [DEBUG] The beginning of the execution of callback "<lambda>".
#> go!
#> 2024-04-18 19:38:43,116 [DEBUG] Callback "<lambda>" has been successfully completed.
#> 2024-04-18 19:38:43,321 [DEBUG] The beginning of the execution of callback "<lambda>".
#> go!
#> 2024-04-18 19:38:43,322 [DEBUG] Callback "<lambda>" has been successfully completed.
#> 2024-04-18 19:38:43,523 [DEBUG] The beginning of the execution of callback "<lambda>".
#> go!
#> 2024-04-18 19:38:43,524 [DEBUG] Callback "<lambda>" has been successfully completed.
#> 2024-04-18 19:38:43,727 [DEBUG] The beginning of the execution of callback "<lambda>".
#> go!
#> 2024-04-18 19:38:43,729 [DEBUG] Callback "<lambda>" has been successfully completed.
#> 2024-04-18 19:38:43,933 [INFO] The metronome has stopped.
```

The events of the start and stop of the metronome will be logged with the `INFO` level, start and stop of the passed function - `DEBUG`. If the operation time of the passed function was longer than the allotted time for one iteration, you will see a `WARNING` message.

And finally, if an exception is raised inside the function, it will be suppressed, and an `ERROR` level message will be recorded along with it (with the traceback saved, that is, the `exception()` method will be called for this from the logger):

```python
# Here should be some imports, logging settings, and the creation of a logger object

def function():
    return 1/0

metronome = Metronome(0.2, function, logger=logger)

metronome.start()
sleep(0.4)
metronome.stop()
#> 2024-04-18 19:58:10,847 [INFO] The metronome starts...
#> 2024-04-18 19:58:10,847 [DEBUG] The beginning of the execution of callback "function".
#> 2024-04-18 19:58:10,847 [ERROR] The "ZeroDivisionError" ("division by zero") exception was suppressed inside the context.
#> Traceback (most recent call last):
#>   File "/project_path/metronomes/metronomes/metronome.py", line 68, in run_loop
#>     self.callback()
#>   File "test.py", line ?, in function
#>     return 1/0
#> ZeroDivisionError: division by zero
#> 2024-04-18 19:58:11,053 [DEBUG] The beginning of the execution of callback "function".
#> 2024-04-18 19:58:11,054 [ERROR] The "ZeroDivisionError" ("division by zero") exception was suppressed inside the context.
#> Traceback (most recent call last):
#>   File "/project_path/metronomes/metronomes/metronome.py", line 68, in run_loop
#>     self.callback()
#>   File "test.py", line ?, in function
#>     return 1/0
#> ZeroDivisionError: division by zero
#> 2024-04-18 19:58:11,258 [INFO] The metronome has stopped.
```


## Error escaping

Exceptions inside the function that you pass to the metronome will be:

- Suppressed.
- [Logged](#logging) (if you pass the logger object).

This applies to all the usual exceptions that are expected in normal code. For more information about the types of exceptions that are suppressed by default, read the documentation for the [`escaping`](https://github.com/pomponchik/escaping) library that is used for this.


## Working with Cancellation Tokens

This library is fully compatible with the [cancellation token pattern](https://cantok.readthedocs.io/en/latest/the_pattern/) and supports any token objects from the [`cantok`](https://github.com/pomponchik/cantok) library.

The essence of the pattern is that you can pass an object to metronome object, from which it can find out whether the work of the metronome still needs to be continued or not. If not, the metronome stops.

The token object is passed to the metronome as the `token` argument:

```python
from time import sleep
from metronomes import Metronome
from cantok import TimeoutToken

metronome = Metronome(0.2, lambda: None, token=TimeoutToken(1))

metronome.start()
print(metronome.stopped)
#> False
sleep(1.5)  # Here I specify a little more time than in the constructor of the token itself, since a small margin is needed for operations related to the creation of the metronome object itself.
print(metronome.stopped)
#> True
```

You can also pass a token when calling the `start()` method:

```python
metronome.start(token=TimeoutToken(1))
```

If you pass cancellation tokens both during metronome initialization and in the `start()` method, their limitations will be summed up.


## How to set a time limit

You can specify a time limit (in seconds) for which the metronome will tick. When the specified time is over, it will simply stop. There are 2 ways to do this: when creating a metronome object or when calling the `start()` method.

In the first way, the time will start counting from the moment the metronome object is created:

```python
metronome = Metronome(0.2, lambda: print('go!'), duration=0.6)  

metronome.start()
sleep(1)
#> go!
#> go!
#> go!
```

In the second way, the countdown will start by calling the `start()` method:

```python
metronome = Metronome(0.2, lambda: print('go!'))  

metronome.start(duration=0.6)
sleep(1)
#> go!
#> go!
#> go!
```

Choose the right way to limit time. When using the metronome in the [context manager mode](#use-it-as-a-context-manager), only the first way is available to you, in almost all other situations - the second one is preferable.
