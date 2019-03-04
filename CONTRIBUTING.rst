Contributing Guidelines
=======================

We welcome contributions of many kinds to ``earthpy``.
When contributing, please follow the guidelines below and adhere to the
`EarthPy Code of Conduct <code-of-conduct.html>`_.

At this stage of development, we are developing a set of
usable wrapper functions that help make working with earth
systems data easier. We are open to new functionality but are currently
trying to ensure our package is stable, operational and well documented.

Edits & Updates
~~~~~~~~~~~~~~~

When submitting a change to the repository, please first create an issue that
covers the item that you'd like to change, update or enhance. Once a discussion
has yielded a vote of support for that addition to the package, you are ready
to submit a pull request.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.


Get Started!
------------

Ready to contribute? Here's how to set up `earthpy` for local development.

1. Fork the `earthpy` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/earthpy.git

3. Set up your fork for local development with conda::

    $ cd earthpy/
    $ conda env create -f environment.yml
    $ source activate earthpy-dev
    $ pip install -e .
    $ pip install -r dev-requirements.txt
    $ pre-commit install

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that tests pass, docs build, and examples run::

    $ pytest --doctest-modules
    $ make docs

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

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
~~~~~~~~~~~~~~~~~~~~~

Improving the documentation and testing for code already in ``earthpy``
is a great way to get started if you'd like to make a contribution. Please note
that our documentation files are in
`ReStructuredText (.rst) <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
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
code in the documentation, which includes docstrings in earthpy's modules, and
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


Style
~~~~~

- ``Earthpy`` currently only supports Python 3 (3.2+). Please test code locally
  in Python 3 when possible (all supported versions will be automatically
  tested on Travis CI).

- ``Earthpy`` uses a pre-commit hook that runs the black code autoformatter.
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
  3rd-party libraries next, and ``earthpy`` imports third following PEP 8
  standards. Within each grouping, imports should be alphabetized. Always use
  absolute imports when possible, and explicit relative imports for local
  imports when necessary in tests.

Deploying
~~~~~~~~~

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

To deploy earthpy, push the commit and the version tags::

    $ git push
    $ git push --tags

Travis will then deploy to PyPI if the build succeeds.
Travis will only deploy to PyPI on tagged commits, so remember to push the tags.
Once that is done, create a release on GitHub for the new version.
