[![DOI](https://zenodo.org/badge/122149160.svg)](https://zenodo.org/badge/latestdoi/122149160)
[![Build Status](https://travis-ci.org/earthlab/earthpy.svg?branch=master)](https://travis-ci.org/earthlab/earthpy)
[![Build status](https://ci.appveyor.com/api/projects/status/xgf5g4ms8qhgtp21?svg=true)](https://ci.appveyor.com/project/earthlab/earthpy)
[![codecov](https://codecov.io/gh/earthlab/earthpy/branch/master/graph/badge.svg)](https://codecov.io/gh/earthlab/earthpy)
[![Docs build](https://readthedocs.org/projects/earthpy/badge/?version=latest)](https://earthpy.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://img.shields.io/badge/code%20style-black-000000.svg)

# EarthPy

A package that supports working with spatial data in python teaching.

## Install

To install, use pip. `--upgrade` is optional but it ensures that the package overwrites
when you install and you have the current version. If you don't have the package
yet you can still use the `--upgrade` argument.

```bash
$ pip install --upgrade git+https://github.com/earthlab/earthpy.git
```

Then import it into python.

```python
>>> import earthpy as et
```

## Active Contributors

- Leah Wasser
- Max Joseph
- Joe McGlinchy
- Tim Head
- Chris Holdgraf
- Jenny Palomino

## Testing

This package uses [pytest](https://pytest.org/) for tests.
To run tests locally, execute the command `pytest` from the command line:

```bash
$ pytest --doctest-modules
```

The `--doctest-modules` syntax allows pytest to check examples in
docstrings contained in modules (e.g., if a function has an example section),
in addition to the normal tests that pytest would discover.

### Testing example code in the `docs` directory

To locally test examples in the `docs` directory (e.g., examples contained in
`.rst` files), you can run the following command from the top-level
`earthpy` directory:


```bash
$ make -C docs doctest
```

### Data generated for testing

If a test requires a data object such as a GeoDataFrame or numpy array, and
copies of that data object are required by multiple tests, we can use [pytest
fixtures](https://docs.pytest.org/en/latest/fixture.html) to cleanly create
and tear down those objects independently for each test.

See [`earthpy/tests/conftest.py`](earthpy/tests/conftest.py) for fixture
definitions, and [`earthpy/tests/test_clip.py`](earthpy/tests/test_clip.py)
for example usage of fixtures in tests.
