from   pathlib  import Path
from   shutil   import copytree, rmtree
import pytest
from   iterpath import iterpath

DATA_DIR = Path(__file__).with_name("data")

def test_simple_iterpath_sort():
    assert list(iterpath(DATA_DIR / "dir01", sort=True)) == [
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_no_dirs():
    assert list(iterpath(DATA_DIR / "dir01", sort=True, dirs=False)) == [
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_no_topdown():
    assert list(iterpath(DATA_DIR / "dir01", sort=True, topdown=False)) == [
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_include_root():
    assert list(iterpath(DATA_DIR / "dir01", sort=True, include_root=True)) == [
        DATA_DIR / "dir01",
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_include_root_no_topdown():
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        include_root=True,
        topdown=False,
    )) == [
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "xyzzy.txt",
        DATA_DIR / "dir01",
    ]

def test_simple_iterpath_sort_key():
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        sort_key=lambda e: e.name[::-1],
    )) == [
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_reverse():
    assert list(iterpath(DATA_DIR / "dir01", sort=True, sort_reverse=True)) == [
        DATA_DIR / "dir01" / "xyzzy.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
    ]

def test_simple_iterpath_sort_key_reverse():
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        sort_key=lambda e: e.name[::-1],
        sort_reverse=True,
    )) == [
        DATA_DIR / "dir01" / "xyzzy.txt",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
    ]

def test_simple_iterpath_sort_filter_dirs():
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        filter_dirs=lambda e: not e.name.startswith("."),
    )) == [
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_filter_files():
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        filter_files=lambda e: not e.name.startswith("."),
    )) == [
        DATA_DIR / "dir01" / ".config",
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_filter_dirs_and_files():
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        filter_dirs=lambda e: not e.name.startswith("."),
        filter_files=lambda e: not e.name.startswith("f"),
    )) == [
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "glarch",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_delete_dirs(tmp_path):
    dirpath = tmp_path / "dir"
    copytree(DATA_DIR / "dir01", dirpath)
    paths = []
    for p in iterpath(dirpath, sort=True):
        paths.append(p)
        if p.is_dir():
            rmtree(p)
    assert paths == [
        dirpath / ".config",
        dirpath / ".hidden",
        dirpath / "foo.txt",
        dirpath / "glarch",
        dirpath / "gnusto",
        dirpath / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_delete_dirs_onerror_raise(tmp_path):
    def raise_(e):
        raise e
    dirpath = tmp_path / "dir"
    copytree(DATA_DIR / "dir01", dirpath)
    paths = []
    with pytest.raises(OSError) as excinfo:
        for p in iterpath(dirpath, sort=True, onerror=raise_):
            paths.append(p)
            if p.is_dir():
                rmtree(p)
    # Apply `Path` to `.filename` to get something predictable, as it's a str
    # on CPython but an os.DirEntry on PyPy:
    assert Path(excinfo.value.filename) == dirpath / ".config"
    assert paths == [dirpath / ".config"]

def test_simple_iterpath_sort_delete_dirs_onerror_record(tmp_path):
    error_files = []

    def record(e):
        error_files.append(Path(e.filename))

    dirpath = tmp_path / "dir"
    copytree(DATA_DIR / "dir01", dirpath)
    paths = []
    for p in iterpath(dirpath, sort=True, onerror=record):
        paths.append(p)
        if p.is_dir():
            rmtree(p)
    assert paths == [
        dirpath / ".config",
        dirpath / ".hidden",
        dirpath / "foo.txt",
        dirpath / "glarch",
        dirpath / "gnusto",
        dirpath / "xyzzy.txt",
    ]
    assert error_files == [
        dirpath / ".config",
        dirpath / "glarch",
        dirpath / "gnusto",
    ]
