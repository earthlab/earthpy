[![DOI](https://zenodo.org/badge/122149160.svg)](https://zenodo.org/badge/latestdoi/122149160)
[![Build Status](https://travis-ci.com/earthlab/earthpy.svg?branch=master)](https://travis-ci.com/earthlab/earthpy)
[![codecov](https://codecov.io/gh/earthlab/earthpy/branch/master/graph/badge.svg)](https://codecov.io/gh/earthlab/earthpy)
[![Docs build](https://readthedocs.org/projects/earthpy/badge/?version=latest)](https://earthpy.readthedocs.io/en/latest/?badge=latest)

# Earth Py

A package built to support python teaching in the Earth Lab earth analytics program
at University of Colorado, Boulder.

## Install

To install, use pip. `--upgrade` is optional but it ensures that the package overwrites
when you install and you have the current version. If you don't have the package
yet you can still use the `--upgrade` argument.

`pip install --upgrade git+https://github.com/earthlab/earthpy.git`

Then import it into python.

`import earthpy as et`


## Contributors

This package was originally developed by Chris Holdgraf.
Contributors:

- Carson Farmer

Contributing Breakers:

- Leah Wasser

## Testing

This package uses [pytest](https://pytest.org/) for tests.
To run tests locally, execute the command `pytest` from the command line.
