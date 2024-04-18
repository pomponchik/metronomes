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
- ❌ Support for cancellation tokens.


## Table of contents

- [**Quick start**](#quick-start)


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
# go!
# go!
# go!
# go!
# go!
```
