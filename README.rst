.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://github.com/jwodder/iterpath/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/iterpath/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/iterpath/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/iterpath

.. image:: https://img.shields.io/pypi/pyversions/iterpath.svg
    :target: https://pypi.org/project/iterpath/

.. image:: https://img.shields.io/github/license/jwodder/iterpath.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/iterpath>`_
| `PyPI <https://pypi.org/project/iterpath/>`_
| `Issues <https://github.com/jwodder/iterpath/issues>`_
| `Changelog <https://github.com/jwodder/iterpath/blob/master/CHANGELOG.md>`_

``iterpath`` lets you iterate over a file tree as a single iterator of
``pathlib.Path`` objects, eliminating the need to combine lists returned by
``os.walk()`` or recursively call ``Path.iterdir()`` or ``os.scandir()``.
Besides the standard ``os.walk()`` options, the library also includes options
for sorting & filtering entries.


Installation
============
``iterpath`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install iterpath


Example
=======

Iterate over this library's source repository, skipping the ``.git`` and
``test/data`` folders:

>>> import os.path
>>> from iterpath import iterpath
>>> def filterer(dir_entry):
...     if dir_entry.name == ".git":
...         return False
...     elif dir_entry.path == os.path.join(".", "test", "data"):
...         return False
...     else:
...         return True
...
>>> for p in iterpath(".", sort=True, filter_dirs=filterer):
...     print(p)
...
.github
.github/workflows
.github/workflows/test.yml
.gitignore
LICENSE
MANIFEST.in
README.rst
TODO.md
pyproject.toml
setup.cfg
src
src/iterpath
src/iterpath/__init__.py
src/iterpath/__pycache__
src/iterpath/__pycache__/__init__.cpython-39.pyc
src/iterpath/py.typed
test
test/test_iterpath.py
tox.ini


API
===

The ``iterpath`` module provides a single function, also named ``iterpath``:

.. code:: python

    iterpath(dirpath: Union[AnyStr, os.PathLike[AnyStr]] = os.curdir, **kwargs) -> Iterator[pathlib.Path]

Iterate through the file tree rooted at the directory ``dirpath`` (by default,
the current directory) in depth-first order, yielding the files & directories
within.  If ``dirpath`` is an absolute path, the generated ``Path`` objects
will be absolute; otherwise, if ``dirpath`` is a relative path, the ``Path``
objects will be relative and will have ``dirpath`` as a prefix.

Note that, although ``iterpath()`` yields ``pathlib.Path`` objects, it operates
internally on ``os.DirEntry`` objects, and so any function supplied as the
``sort_key`` parameter or as a filter/exclude parameter must accept
``os.DirEntry`` instances.

Keyword arguments:

``dirs: bool = True``
    Whether to include directories in the output

``topdown: bool = True``
    Whether to yield each directory before (``True``) or after (``False``) its
    contents

``include_root: bool = False``
    Whether to include the ``dirpath`` argument passed to ``iterpath()`` in the
    output

``followlinks: bool = False``
    Whether to treat a symlink to a directory as a directory

``onerror: Optional[Callable[[OSError], Any]] = None``
    Specify a function to be called whenever an ``OSError`` is encountered
    while iterating over a directory.  If the function reraises the exception,
    ``iterpath()`` aborts; otherwise, it continues with the next directory.  By
    default, ``OSError`` exceptions are ignored.

``sort: bool = False``
    Sort the entries in each directory.  When ``False``, entries are yielded in
    the order returned by ``os.scandir()``.  When ``True``, entries are sorted,
    by default, by filename in ascending order, but this can be changed via the
    ``sort_key`` and ``sort_reverse`` arguments.

``sort_key: Optional[Callable[[os.DirEntry[AnyStr]], _typeshed.SupportsLessThan]] = None``
    Specify a custom key function for sorting directory entries.  Only has an
    effect when ``sort`` is ``True``.

``sort_reverse: bool = False``
    Sort directory entries in reverse order.  Only has an effect when ``sort``
    is ``True``.

``filter: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all files & directories encountered;
    only those for which the predicate returns a true value will be yielded
    (and, for directories, descended into).

    If ``filter`` is specified, it is an error to also specify ``filter_dirs``
    or ``filter_files``.

``filter_dirs: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all directories encountered; only
    those for which the predicate returns a true value will be yielded &
    descended into

``filter_files: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all files encountered; only those for
    which the predicate returns a true value will be yielded

``exclude: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all files & directories encountered;
    only those for which the predicate returns a false value will be yielded
    (and, for directories, descended into).

    If ``exclude`` is specified, it is an error to also specify ``exclude_dirs``
    or ``exclude_files``.

``exclude_dirs: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all directories encountered; only
    those for which the predicate returns a false value will be yielded &
    descended into

``exclude_files: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all files encountered; only those for
    which the predicate returns a false value will be yielded

If both ``filter`` and ``exclude`` are set, a given entry will only be included
if ``filter`` returns true and ``exclude`` returns false (that is, exclusions
take priority over inclusions), and likewise for the directory- and
file-specific arguments.

**Warnings:**

- If ``dirpath`` is a relative path, changing the working directory while
  ``iterpath()`` is in progress will lead to errors, or at least inaccurate
  results.

- Setting ``followlinks`` to ``True`` can result in infinite recursion if a
  symlink points to a parent directory of itself.

Selectors
---------

*New in version 0.3.0*

``iterpath`` also provides a selection of "selector" classes & constants for
easy construction of ``filter`` and ``exclude`` arguments.  Selectors are
callables that return true for ``DirEntry``'s whose (base) names match given
criteria.

Selectors can even be combined using the ``|`` operator:

.. code:: python

    # This only returns entries whose names end in ".txt" or equal "foo.png" or
    # ".hidden":
    iterpath(
        dirpath,
        filter=SelectGlob("*.txt") | SelectNames("foo.png", ".hidden")
    )

    # Exclude all dot-directories and VCS directories:
    iterpath(dirpath, exclude_dirs=SELECT_DOTS | SELECT_VCS_DIRS)

The selectors:

.. code:: python

    class SelectNames(*names: AnyStr, case_sensitive: bool = True)

Selects ``DirEntry``'s whose names are one of ``names``.  If ``case_sensitive``
is ``False``, the check is performed case-insensitively.

.. code:: python

    class SelectGlob(pattern: AnyStr)

Selects ``DirEntry``'s whose names match the given fileglob pattern

.. code:: python

    class SelectRegex(pattern: Union[AnyStr, re.Pattern[AnyStr]])

Selects ``DirEntry``'s whose names match (using ``re.search()``) the given
regular expression

.. code:: python

    SELECT_DOTS

Selects ``DirEntry``'s whose names begin with a period

.. code:: python

    SELECT_VCS

Selects ``DirEntry``'s matched by either ``SELECT_VCS_DIRS`` or
``SELECT_VCS_FILES`` (see below)

.. code:: python

    SELECT_VCS_DIRS

Selects the following names of version-control directories: ``.git``, ``.hg``,
``_darcs``, ``.bzr``, ``.svn``, ``_svn``, ``CVS``, ``RCS``

.. code:: python

    SELECT_VCS_FILES

Selects the following names of version-control-specific files:
``.gitattributes``, ``.gitignore``, ``.gitmodules``, ``.mailmap``,
``.hgignore``, ``.hgsigs``, ``.hgtags``, ``.binaries``, ``.boring``,
``.bzrignore``, and all nonempty filenames that end in ``,v``
