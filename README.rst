.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP — Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://github.com/jwodder/iterpath/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/iterpath/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/iterpath/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/iterpath

.. image:: https://img.shields.io/github/license/jwodder/iterpath.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/iterpath>`_
| `Issues <https://github.com/jwodder/iterpath/issues>`_

``iterpath`` lets you iterate over a file tree as a single iterator of
``pathlib.Path`` objects, eliminating the need to combine lists returned by
``os.walk()`` or recursively call ``Path.iterdir()`` or ``os.scandir()``.
Besides the standard ``os.walk()`` options, the library also includes options
for sorting & filtering entries.


Installation
============
``iterpath`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``iterpath`` and its dependencies::

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

    iterpath(dirpath: Union[AnyStr, os.PathLike[AnyStr]], **kwargs) -> Iterator[pathlib.Path]

Iterate through the file tree rooted at the directory ``dirpath`` in
depth-first order, yielding the files & directories within.  If ``dirpath`` is
an absolute path, the generated ``Path`` objects will be absolute; otherwise,
if ``dirpath`` is a relative path, the ``Path`` objects will be relative and
will have ``dirpath`` as a prefix.

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

``filter_dirs: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all directories encountered; only
    those for which the predicate returns a true value will be yielded &
    descended into

``filter_files: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all files encountered; only those for
    which the predicate returns a true value will be yielded

``exclude_dirs: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all directories encountered; only
    those for which the predicate returns a false value will be yielded &
    descended into

``exclude_files: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None``
    Specify a predicate to be applied to all files encountered; only those for
    which the predicate returns a false value will be yielded