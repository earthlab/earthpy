=======================
Contributing Guidelines
=======================

We welcome contributions to EarthPy. They are more likely to
be accepted if they follow the guidelines below.

At this stage of development, we are developing a set of
usable wrapper functions that help make working with earth
systems data easier. We are open to new functionality but are currently
trying to ensure our package is stable, operational and well documented.

When submitting a change to the repository, please first create an issue that
covers the item that you'd like to change, update or enhance. Once a discussion
has yielded a vote of support for that addition to the package, you are ready
to submit a pull request.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.


Get Started!
============

Ready to contribute? Here's how to set up EarthPy for local development.

1. Fork the repository on GitHub
--------------------------------

To create your own copy of the repository on GitHub, navigate to the
`earthlab/earthpy <https://github.com/earthlab/earthpy>`_ repository
and click the **Fork** button in the top-right corner of the page.

2. Clone your fork locally
--------------------------

Use ``git clone`` to get a local copy of your EarthPy repository on your
local filesystem::

    $ git clone git@github.com:your_name_here/earthpy.git
    $ cd earthpy/

3. Set up your fork for local development
-----------------------------------------

Create an environment
^^^^^^^^^^^^^^^^^^^^^

Using conda::

    $ conda create -n earthpy-dev python=3.7
    $ source activate earthpy-dev

Or, using virtualenv::

    $ virtualenv earthpy-dev
    $ source earthpy-dev/bin/activate

Install the package
^^^^^^^^^^^^^^^^^^^

Once the environment is activated, install EarthPy in editable
mode, along with the development requirements and pre-commit hooks::

    $ pip install -e .
    $ pip install -r dev-requirements.txt
    $ pre-commit install

4. Create a branch for local development
----------------------------------------

Use the ``git checkout`` command to create your own branch, and pick a name
that describes the changes that you are making::

    $ git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

5. Test the package
-------------------

Ensure that the tests pass, and the documentation builds successfully::

    $ pytest
    $ make docs

To test against multiple versions of python, you can use tox.
Note that if you are using conda - even with virtualenv - you may need to
install tox-conda (via ``pip install tox-conda``) for tox to work correctly.
Otherwise, you may get ``InterpreterNotFound`` errors when running tox.

Running tox is as simple as::

    $ tox

6. Commit and push your changes
-------------------------------

Once you are sure that all tests are passing, you can commit your changes
and push to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request on GitHub
----------------------------------

When submitting a pull request:

- All existing tests should pass. Please make sure that the test
  suite passes, both locally and on
  `Travis CI <https://travis-ci.org/earthlab/earthpy>`_
  Status on
  Travis will be visible on a pull request. If you want to enable
  Travis CI on your own fork, please read the
  `getting started docs <https://docs.travis-ci.com/user/getting-started/>`_.

- New functionality should include tests. Please write reasonable
  tests for your code and make sure that they pass on your pull request.

- Classes, methods, functions, etc. should have docstrings. The first
  line of a docstring should be a standalone summary. Parameters and
  return values should be documented explicitly.

- The API documentation is automatically generated from docstrings, which
  should conform to NumpPy styling. For examples, see the `Napoleon docs
  <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html>`_.

- Please note that tests are also run via Travis-CI on our documentation.
  So be sure that any ``.rst`` file submissions are properly formatted and
  tests are passing.


Documentation Updates
=====================

Improving the documentation and testing for code already in EarthPy
is a great way to get started if you'd like to make a contribution. Please note
that our documentation files are in
`ReStructuredText (.rst)
<http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
format and format your pull request
accordingly.

To build the documentation, use the command::

    $ make docs

By default ``make docs`` will only rebuild the documentation if source
files (e.g., .py or .rst files) have changed. To force a rebuild, use
``make -B docs``.
You can preview the generated documentation by opening
``docs/_build/html/index.html`` in a web browser.

Earthpy uses `doctest
<https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html>`_ to test
code in the documentation, which includes docstrings in EarthPy's modules, and
code chunks in the reStructuredText source files.
This enables the actual output of code examples to be checked against expected
output.
When the output of an example is not always identical (e.g., the
memory address of an object), use an `ellipsis
<https://docs.python.org/3.6/library/doctest.html#doctest.ELLIPSIS>`_
(``...``) to match any substring of the actual output, e.g.:

.. code-block:: python

  >>> print(list(range(20)))
  [0, 1, ..., 18, 19]

Earthpy also uses the `Matplotlib plot directive
<https://matplotlib.org/devel/plot_directive.html>`_ in the documentation to
generate figures.
To include a figure in an example, prefix the example with ``.. plot::``,
e.g.,::

    .. plot::

       >>> import matplotlib.pyplot as plt
       >>> plt.plot([1, 2, 3], [4, 5, 6])


Code style
==========

- EarthPy currently only supports Python 3 (3.5+). Please test code locally
  in Python 3 when possible (all supported versions will be automatically
  tested on Travis CI).

- EarthPy uses a pre-commit hook that runs the black code autoformatter.
  Be sure to execute `pre-commit install` as described above, which will cause
  black to autoformat code prior to commits. If this step is skipped, black
  may cause build failures on Travis CI due to formatting issues.

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ when possible.
  Some standards that we follow include:

    - The first word of a comment should be capitalized with a space following
      the ``#`` sign like this: ``# This is a comment here``
    - Variable and function names should be all lowercase with words separated
      by ``_``.
    - Class definitions should use camel case - example: ``ClassNameHere`` .

- Imports should be grouped with standard library imports first,
  3rd-party libraries next, and EarthPy imports third following PEP 8
  standards. Within each grouping, imports should be alphabetized. Always use
  absolute imports when possible, and explicit relative imports for local
  imports when necessary in tests.


Deploying
=========

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed, then run::

    $ bumpversion patch # possible: major / minor / patch

This will increment the version according to a major release (e.g., 0.1.0 to
1.0.0), a minor release (e.g., 0.1.0 to 0.2.0), or a patch (e.g., 0.1.0 to
0.1.1), following the guidelines for semantic versioning: https://semver.org/.


Bumpversion updates the version number throughout the
package, and generates a git commit along with an associated git tag for the
new version.
For more on bumpversion, see: https://github.com/peritus/bumpversion

To deploy EarthPy, push the commit and the version tags::

    $ git push
    $ git push --tags

Travis will then deploy to PyPI if the build succeeds.
Travis will only deploy to PyPI on tagged commits, so remember to push the tags.
Once that is done, create a release on GitHub for the new version.
