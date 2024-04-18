# metronomes

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

This library offers the easiest way to run regular tasks. Just give her a function and tell her how many seconds you need to run it, then step back and don't interfere. For all its simplicity, there are:

- 📜 Logging the start and end of each operation.
- 🛡️ Error escaping. But not when you don't even know about the errors, but again - with detailed logging.
- ⇆ Thread safety.
- ❌ Support for [cancellation tokens](https://github.com/pomponchik/cantok).


## Table of contents

- [**Quick start**](#quick-start)
- [**Why?**](#why)


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


## Why?

A metronome is a special device that musicians often use. It looks something like this:

![metronome](https://raw.githubusercontent.com/pomponchik/metronomes/develop/docs/assets/image_2.gif)

Its task is to produce sounds regularly and monotonously, which is very convenient if you want to develop a sense of rhythm. Unlike a person for whom strict rhythmicity is unusual, the metronome counts down time very accurately and therefore is used as a "guide" to which other rhythmic actions that we want to do are attached, whether it's tapping on a drum or pressing keys.

When we write programs, we also sometimes want some action to be performed regularly. And sometimes it happens that it may take a different amount of time, but we need the next action to start on time. This is exactly the task this library solves. When you call the `start()` method on a metronome object, it starts calling the function you passed once in a certain period of time. This happens in a separate specially created thread, so you can use these function calls to orchestrate some other actions in the main thread or even in several different threads.

At the same time, it may be important to you that even if in some cases the function does not work well and raises exceptions, in general the metronome continues to work, and after a certain time it will try to call this function again, and will not break at the first exception. After all, it would be strange if your real metronome went silent when you made a mistake in the rhythm that you are tapping on the drum, right? You may also want the errors that have occurred not to be lost, but to be recorded in your log. This library also provides all these amenities.
