v0.4.1 (2024-12-01)
-------------------
- Support Python 3.11, 3.12, and 3.13
- Migrated from setuptools to hatch
- Drop support for Python 3.7

v0.4.0 (2022-06-25)
-------------------
- Add `return_relative` argument
- The return value of `iterpath()` can now be used as a context manager in
  order to clean up internal `os.scandir()` iterators
- Drop support for Python 3.6

v0.3.1 (2022-03-12)
-------------------
- Support Python 3.10
- Update for mypy 0.940

v0.3.0 (2021-06-23)
-------------------
- Add `filter` and `exclude` arguments
- Add `SelectNames`, `SelectGlob`, `SelectRegex`, `SELECT_DOTS`, `SELECT_VCS`,
  `SELECT_VCS_DIRS`, and `SELECT_VCS_FILES` for easy filtering by entry name

v0.2.0 (2021-02-19)
-------------------
- Set `dirpath` to the current directory if not specified

v0.1.0 (2021-02-18)
-------------------
Initial release
