from pathlib  import Path
from iterpath import iterpath

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
