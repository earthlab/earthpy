Guidelines
==========

Contributions to `earthpy` are welcome. They are likely to
be accepted more quickly if they follow these guidelines.

At this stage of development, we are developing a set of
usable wrapper functions that help make working with earth
systems data easier.

Edits & Updates
===============

When submitting a change to the repository, please do the following:

- Please first create an issue that covers the item that you'd like to change, update or enhance. Once a discussion has yielded a vote of support for that addition to the package, you are ready to submit a pull request.

When submitting a pull request:

- All existing tests should pass. Please make sure that the test
  suite passes, both locally and on
  [Travis CI](https://travis-ci.org/earthlab/earthpy). Status on
  Travis will be visible on a pull request. If you want to enable
  Travis CI on your own fork, please read the pandas guidelines link
  above or the
  [getting started docs](http://about.travis-ci.org/docs/user/getting-started/).

- New functionality should include tests. Please write reasonable
  tests for your code and make sure that they pass on your pull request.

- Classes, methods, functions, etc. should have docstrings. The first
  line of a docstring should be a standalone summary. Parameters and
  return values should be documented explicitly.

Improving the documentation and testing for code already in `earthpy`
is a great way to get started if you'd like to make a contribution.

Style
-----

- `Earthpy` supports python 3 (3.2+) with a single
  code base. Use modern python idioms when possible that are
  compatible with both major versions, and use the
  [six](https://pythonhosted.org/six) library where helpful to smooth
  over the differences.  Use `from __future__ import` statements where
  appropriate. Test code locally in both python 2 and python 3 when
  possible (all supported versions will be automatically tested on
  Travis CI).

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) when possible. Some standards that we follow include
    - The first word of a comment should be capitalized with a space   following the `#` sign like this: `# This is a comment here`
    - Variable and function names should be all lowercase with words separated by `_`.
    - Class definitions should use camel case - example: `ClassNameHere` .

- Imports should be grouped with standard library imports first,
  3rd-party libraries next, and `earthpy` imports third following PEP 8 standards. Within each
  grouping, imports should be alphabetized. Always use absolute
  imports when possible, and explicit relative imports for local
  imports when necessary in tests.
