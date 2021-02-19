import os
from   pathlib  import Path
import platform
from   shutil   import copytree, rmtree
from   typing   import Callable, List
import pytest
from   iterpath import iterpath

DATA_DIR = Path(__file__).with_name("data")

def name_startswith(prefix: str) -> Callable[["os.DirEntry[str]"], bool]:
    def func(e: "os.DirEntry[str]") -> bool:
        return e.name.startswith(prefix)
    return func

def not_name_startswith(prefix: str) -> Callable[["os.DirEntry[str]"], bool]:
    def func(e: "os.DirEntry[str]") -> bool:
        return not e.name.startswith(prefix)
    return func

def name_endswith(prefix: str) -> Callable[["os.DirEntry[str]"], bool]:
    def func(e: "os.DirEntry[str]") -> bool:
        return e.name.endswith(prefix)
    return func

def reverse_name(e: "os.DirEntry[str]") -> str:
    return e.name[::-1]

@pytest.fixture
def link_dir(tmp_path: Path) -> Path:
    # Sdists don't preserve symlinks, so this directory can't be distributed
    # the same way as the others.  Hence, we create it on-demand instead.
    (tmp_path / "apple.txt").touch()
    (tmp_path / "banana.txt").touch()
    (tmp_path / "link").symlink_to(DATA_DIR / "dir01", target_is_directory=True)
    (tmp_path / "mango.txt").touch()
    return tmp_path

def test_simple_iterpath_sort() -> None:
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

def test_simple_iterpath_sort_relpath_curdir(monkeypatch: pytest.MonkeyPatch) \
        -> None:
    monkeypatch.chdir(DATA_DIR / "dir01")
    assert list(iterpath(os.curdir, sort=True)) == [
        Path(".config"),
        Path(".config", "cfg.ini"),
        Path(".hidden"),
        Path("foo.txt"),
        Path("glarch"),
        Path("glarch", "bar.txt"),
        Path("gnusto"),
        Path("gnusto", "cleesh.txt"),
        Path("gnusto", "quux"),
        Path("gnusto", "quux", "quism.txt"),
        Path("xyzzy.txt"),
    ]

def test_simple_iterpath_sort_relpath_prefix(monkeypatch: pytest.MonkeyPatch) \
        -> None:
    monkeypatch.chdir(DATA_DIR)
    assert list(iterpath("dir01", sort=True)) == [
        Path("dir01", ".config"),
        Path("dir01", ".config", "cfg.ini"),
        Path("dir01", ".hidden"),
        Path("dir01", "foo.txt"),
        Path("dir01", "glarch"),
        Path("dir01", "glarch", "bar.txt"),
        Path("dir01", "gnusto"),
        Path("dir01", "gnusto", "cleesh.txt"),
        Path("dir01", "gnusto", "quux"),
        Path("dir01", "gnusto", "quux", "quism.txt"),
        Path("dir01", "xyzzy.txt"),
    ]

def test_simple_iterpath_sort_no_dirs() -> None:
    assert list(iterpath(DATA_DIR / "dir01", sort=True, dirs=False)) == [
        DATA_DIR / "dir01" / ".config" / "cfg.ini",
        DATA_DIR / "dir01" / ".hidden",
        DATA_DIR / "dir01" / "foo.txt",
        DATA_DIR / "dir01" / "glarch" / "bar.txt",
        DATA_DIR / "dir01" / "gnusto" / "cleesh.txt",
        DATA_DIR / "dir01" / "gnusto" / "quux" / "quism.txt",
        DATA_DIR / "dir01" / "xyzzy.txt",
    ]

def test_simple_iterpath_sort_no_topdown() -> None:
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

def test_simple_iterpath_sort_include_root() -> None:
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

def test_simple_iterpath_sort_include_root_no_topdown() -> None:
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

def test_simple_iterpath_sort_key() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        sort_key=reverse_name,
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

def test_simple_iterpath_sort_reverse() -> None:
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

def test_simple_iterpath_sort_key_reverse() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        sort_key=reverse_name,
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

def test_simple_iterpath_sort_filter_dirs() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        filter_dirs=not_name_startswith("."),
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

def test_simple_iterpath_sort_filter_files() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        filter_files=not_name_startswith("."),
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

def test_simple_iterpath_sort_filter_dirs_and_files() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        filter_dirs=not_name_startswith("."),
        filter_files=not_name_startswith("f"),
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

def test_simple_iterpath_sort_exclude_dirs() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        exclude_dirs=name_startswith("."),
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

def test_simple_iterpath_sort_exclude_files() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        exclude_files=name_startswith("."),
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

def test_simple_iterpath_sort_exclude_dirs_and_files() -> None:
    assert list(iterpath(
        DATA_DIR / "dir01",
        sort=True,
        exclude_dirs=name_startswith("."),
        exclude_files=name_startswith("f"),
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

def test_simple_iterpath_sort_filter_and_exclude_dirs_and_files() -> None:
    assert list(iterpath(
        DATA_DIR / "dir03",
        sort=True,
        filter_files=name_endswith(".txt"),
        filter_dirs=not_name_startswith("_"),
        exclude_dirs=name_startswith("."),
        exclude_files=name_startswith("x"),
    )) == [
        DATA_DIR / "dir03" / "foo.txt",
        DATA_DIR / "dir03" / "glarch",
        DATA_DIR / "dir03" / "glarch" / "gnusto.txt",
    ]

def test_simple_iterpath_sort_delete_dirs(tmp_path: Path) -> None:
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

def test_simple_iterpath_sort_delete_dirs_onerror_raise(tmp_path: Path) -> None:
    def raise_(e: OSError) -> None:
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

def test_simple_iterpath_sort_delete_dirs_onerror_record(tmp_path: Path) -> None:
    error_files: List[Path] = []

    def record(e: OSError) -> None:
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

@pytest.mark.xfail(
    platform.system() == "Windows" and platform.python_implementation() == "PyPy",
    reason='Symlinks are not handled properly on PyPy on Windows as of v7.3.3',
)
@pytest.mark.parametrize('dirs', [True, False])
def test_linked_iterpath_sort(dirs: bool, link_dir: Path) -> None:
    assert list(iterpath(link_dir, sort=True, dirs=dirs)) == [
        link_dir / "apple.txt",
        link_dir / "banana.txt",
        link_dir / "link",
        link_dir / "mango.txt",
    ]

@pytest.mark.xfail(
    platform.system() == "Windows" and platform.python_implementation() == "PyPy",
    reason='Symlinks are not handled properly on PyPy on Windows as of v7.3.3',
)
def test_linked_iterpath_sort_followlinks(link_dir: Path) -> None:
    assert list(iterpath(link_dir, sort=True, followlinks=True)) == [
        link_dir / "apple.txt",
        link_dir / "banana.txt",
        link_dir / "link",
        link_dir / "link" / ".config",
        link_dir / "link" / ".config" / "cfg.ini",
        link_dir / "link" / ".hidden",
        link_dir / "link" / "foo.txt",
        link_dir / "link" / "glarch",
        link_dir / "link" / "glarch" / "bar.txt",
        link_dir / "link" / "gnusto",
        link_dir / "link" / "gnusto" / "cleesh.txt",
        link_dir / "link" / "gnusto" / "quux",
        link_dir / "link" / "gnusto" / "quux" / "quism.txt",
        link_dir / "link" / "xyzzy.txt",
        link_dir / "mango.txt",
    ]

@pytest.mark.xfail(
    platform.system() == "Windows" and platform.python_implementation() == "PyPy",
    reason='Symlinks are not handled properly on PyPy on Windows as of v7.3.3',
)
def test_linked_iterpath_sort_followlinks_no_dirs(link_dir: Path) -> None:
    assert list(iterpath(
        link_dir,
        sort=True,
        followlinks=True,
        dirs=False,
    )) == [
        link_dir / "apple.txt",
        link_dir / "banana.txt",
        link_dir / "link" / ".config" / "cfg.ini",
        link_dir / "link" / ".hidden",
        link_dir / "link" / "foo.txt",
        link_dir / "link" / "glarch" / "bar.txt",
        link_dir / "link" / "gnusto" / "cleesh.txt",
        link_dir / "link" / "gnusto" / "quux" / "quism.txt",
        link_dir / "link" / "xyzzy.txt",
        link_dir / "mango.txt",
    ]

@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="bytes(Path) should only be used on POSIX",
)
def test_simple_iterpath_sort_bytes() -> None:
    assert list(iterpath(bytes(DATA_DIR / "dir01"), sort=True)) == [
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

def test_simple_iterpath_sort_default_curdir(monkeypatch: pytest.MonkeyPatch) \
        -> None:
    monkeypatch.chdir(DATA_DIR / "dir01")
    assert list(iterpath(sort=True)) == [
        Path(".config"),
        Path(".config", "cfg.ini"),
        Path(".hidden"),
        Path("foo.txt"),
        Path("glarch"),
        Path("glarch", "bar.txt"),
        Path("gnusto"),
        Path("gnusto", "cleesh.txt"),
        Path("gnusto", "quux"),
        Path("gnusto", "quux", "quism.txt"),
        Path("xyzzy.txt"),
    ]
