from __future__ import annotations
from collections.abc import Callable
import os
from pathlib import Path
import platform
from shutil import copytree, rmtree
import pytest
from iterpath import SELECT_DOTS, iterpath


def name_startswith(prefix: str) -> Callable[[os.DirEntry[str]], bool]:
    def func(e: os.DirEntry[str]) -> bool:
        return e.name.startswith(prefix)

    return func


def not_name_startswith(prefix: str) -> Callable[[os.DirEntry[str]], bool]:
    def func(e: os.DirEntry[str]) -> bool:
        return not e.name.startswith(prefix)

    return func


def name_endswith(prefix: str) -> Callable[[os.DirEntry[str]], bool]:
    def func(e: os.DirEntry[str]) -> bool:
        return e.name.endswith(prefix)

    return func


def reverse_name(e: os.DirEntry[str]) -> str:
    return e.name[::-1]


@pytest.fixture(scope="session")
def tree01(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dirpath = tmp_path_factory.mktemp("tree01")
    for p in [
        Path(".config", "cfg.ini"),
        Path(".hidden"),
        Path("foo.txt"),
        Path("glarch", "bar.txt"),
        Path("gnusto", "cleesh.txt"),
        Path("gnusto", "quux", "quism.txt"),
        Path("xyzzy.txt"),
    ]:
        (dirpath / p).parent.mkdir(parents=True, exist_ok=True)
        (dirpath / p).touch()
    return dirpath


@pytest.fixture(scope="session")
def link_dir(tmp_path_factory: pytest.TempPathFactory, tree01: Path) -> Path:
    dirpath = tmp_path_factory.mktemp("link_dir")
    (dirpath / "apple.txt").touch()
    (dirpath / "banana.txt").touch()
    (dirpath / "link").symlink_to(tree01, target_is_directory=True)
    (dirpath / "mango.txt").touch()
    return dirpath


@pytest.fixture(scope="session")
def tree03(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dirpath = tmp_path_factory.mktemp("tree03")
    for p in [
        Path(".config", "options.txt"),
        Path(".config", "subdir", "settings.txt"),
        Path("_cache", "stuff.txt"),
        Path("_cache", "subcache", "data.txt"),
        Path("bar.dat"),
        Path("foo.txt"),
        Path("glarch", "cleesh.dat"),
        Path("glarch", "gnusto.txt"),
        Path("glarch", "xxx.dat"),
        Path("glarch", "xxx.txt"),
        Path("xyz.dat"),
        Path("xyz.txt"),
    ]:
        (dirpath / p).parent.mkdir(parents=True, exist_ok=True)
        (dirpath / p).touch()
    return dirpath


def test_iterpath(tree01: Path) -> None:
    with iterpath(tree01) as ip:
        assert sorted(ip) == [
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort(tree01: Path) -> None:
    with iterpath(tree01, sort=True) as ip:
        assert list(ip) == [
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_relpath_curdir(
    monkeypatch: pytest.MonkeyPatch, tree01: Path
) -> None:
    monkeypatch.chdir(tree01)
    with iterpath(os.curdir, sort=True) as ip:
        assert list(ip) == [
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


def test_iterpath_sort_relpath_prefix(
    monkeypatch: pytest.MonkeyPatch, tree01: Path
) -> None:
    monkeypatch.chdir(tree01.parent)
    with iterpath(tree01.name, sort=True) as ip:
        assert list(ip) == [
            Path(tree01.name, ".config"),
            Path(tree01.name, ".config", "cfg.ini"),
            Path(tree01.name, ".hidden"),
            Path(tree01.name, "foo.txt"),
            Path(tree01.name, "glarch"),
            Path(tree01.name, "glarch", "bar.txt"),
            Path(tree01.name, "gnusto"),
            Path(tree01.name, "gnusto", "cleesh.txt"),
            Path(tree01.name, "gnusto", "quux"),
            Path(tree01.name, "gnusto", "quux", "quism.txt"),
            Path(tree01.name, "xyzzy.txt"),
        ]


def test_iterpath_sort_no_dirs(tree01: Path) -> None:
    with iterpath(tree01, sort=True, dirs=False) as ip:
        assert list(ip) == [
            tree01 / ".config" / "cfg.ini",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_no_topdown(tree01: Path) -> None:
    with iterpath(tree01, sort=True, topdown=False) as ip:
        assert list(ip) == [
            tree01 / ".config" / "cfg.ini",
            tree01 / ".config",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch" / "bar.txt",
            tree01 / "glarch",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_include_root(tree01: Path) -> None:
    with iterpath(tree01, sort=True, include_root=True) as ip:
        assert list(ip) == [
            tree01,
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_include_root_no_topdown(tree01: Path) -> None:
    with iterpath(tree01, sort=True, include_root=True, topdown=False) as ip:
        assert list(ip) == [
            tree01 / ".config" / "cfg.ini",
            tree01 / ".config",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch" / "bar.txt",
            tree01 / "glarch",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto",
            tree01 / "xyzzy.txt",
            tree01,
        ]


def test_iterpath_sort_key(tree01: Path) -> None:
    with iterpath(tree01, sort=True, sort_key=reverse_name) as ip:
        assert list(ip) == [
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / ".hidden",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "foo.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_reverse(tree01: Path) -> None:
    with iterpath(tree01, sort=True, sort_reverse=True) as ip:
        assert list(ip) == [
            tree01 / "xyzzy.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "foo.txt",
            tree01 / ".hidden",
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
        ]


def test_iterpath_sort_key_reverse(tree01: Path) -> None:
    with iterpath(tree01, sort=True, sort_key=reverse_name, sort_reverse=True) as ip:
        assert list(ip) == [
            tree01 / "xyzzy.txt",
            tree01 / "foo.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / ".hidden",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
        ]


def test_iterpath_sort_filter_dirs(tree01: Path) -> None:
    with iterpath(tree01, sort=True, filter_dirs=not_name_startswith(".")) as ip:
        assert list(ip) == [
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_filter_files(tree01: Path) -> None:
    with iterpath(tree01, sort=True, filter_files=not_name_startswith(".")) as ip:
        assert list(ip) == [
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_filter_dirs_and_files(tree01: Path) -> None:
    with iterpath(
        tree01,
        sort=True,
        filter_dirs=not_name_startswith("."),
        filter_files=not_name_startswith("f"),
    ) as ip:
        assert list(ip) == [
            tree01 / ".hidden",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_filter(tree01: Path) -> None:
    with iterpath(tree01, sort=True, filter=not_name_startswith(".")) as ip:
        assert list(ip) == [
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_filter_filter_dirs(tree01: Path) -> None:
    with pytest.raises(TypeError) as excinfo:
        iterpath(
            tree01,
            filter=not_name_startswith("."),
            filter_dirs=not_name_startswith("f"),
        )
    assert str(excinfo.value) == "filter and filter_dirs are mutually exclusive"


def test_iterpath_filter_filter_files(tree01: Path) -> None:
    with pytest.raises(TypeError) as excinfo:
        iterpath(
            tree01,
            filter=not_name_startswith("."),
            filter_files=not_name_startswith("f"),
        )
    assert str(excinfo.value) == "filter and filter_files are mutually exclusive"


def test_iterpath_sort_exclude_dirs(tree01: Path) -> None:
    with iterpath(tree01, sort=True, exclude_dirs=name_startswith(".")) as ip:
        assert list(ip) == [
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_exclude_files(tree01: Path) -> None:
    with iterpath(tree01, sort=True, exclude_files=name_startswith(".")) as ip:
        assert list(ip) == [
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_exclude_dirs_and_files(tree01: Path) -> None:
    with iterpath(
        tree01,
        sort=True,
        exclude_dirs=name_startswith("."),
        exclude_files=name_startswith("f"),
    ) as ip:
        assert list(ip) == [
            tree01 / ".hidden",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_exclude(tree01: Path) -> None:
    with iterpath(tree01, sort=True, exclude=name_startswith(".")) as ip:
        assert list(ip) == [
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_sort_exclude_selector(tree01: Path) -> None:
    with iterpath(tree01, sort=True, exclude=SELECT_DOTS) as ip:
        assert list(ip) == [
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


def test_iterpath_exclude_exclude_dirs(tree01: Path) -> None:
    with pytest.raises(TypeError) as excinfo:
        iterpath(
            tree01, exclude=name_startswith("."), exclude_dirs=name_startswith("f")
        )
    assert str(excinfo.value) == "exclude and exclude_dirs are mutually exclusive"


def test_iterpath_exclude_exclude_files(tree01: Path) -> None:
    with pytest.raises(TypeError) as excinfo:
        iterpath(
            tree01, exclude=name_startswith("."), exclude_files=name_startswith("f")
        )
    assert str(excinfo.value) == "exclude and exclude_files are mutually exclusive"


def test_iterpath_sort_filter_and_exclude_dirs_and_files(tree03: Path) -> None:
    with iterpath(
        tree03,
        sort=True,
        filter_files=name_endswith(".txt"),
        filter_dirs=not_name_startswith("_"),
        exclude_dirs=name_startswith("."),
        exclude_files=name_startswith("x"),
    ) as ip:
        assert list(ip) == [
            tree03 / "foo.txt",
            tree03 / "glarch",
            tree03 / "glarch" / "gnusto.txt",
        ]


def test_iterpath_sort_delete_dirs(tree01: Path, tmp_path: Path) -> None:
    dirpath = tmp_path / "dir"
    copytree(tree01, dirpath)
    paths = []
    with iterpath(dirpath, sort=True) as ip:
        for p in ip:
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


def test_iterpath_sort_delete_dirs_onerror_raise(tmp_path: Path, tree01: Path) -> None:
    def raise_(e: OSError) -> None:
        raise e

    dirpath = tmp_path / "dir"
    copytree(tree01, dirpath)
    paths = []
    with pytest.raises(OSError) as excinfo:
        with iterpath(dirpath, sort=True, onerror=raise_) as ip:
            for p in ip:
                paths.append(p)
                if p.is_dir():
                    rmtree(p)
    # Apply `Path` to `.filename` to get something predictable, as it's a str
    # on CPython, an os.DirEntry on PyPy-3.6, and a bytes on PyPy-3.7:
    assert Path(os.fsdecode(excinfo.value.filename)) == dirpath / ".config"
    assert paths == [dirpath / ".config"]


def test_iterpath_sort_delete_dirs_onerror_record(tmp_path: Path, tree01: Path) -> None:
    error_files: list[Path] = []

    def record(e: OSError) -> None:
        error_files.append(Path(os.fsdecode(e.filename)))

    dirpath = tmp_path / "dir"
    copytree(tree01, dirpath)
    paths = []
    with iterpath(dirpath, sort=True, onerror=record) as ip:
        for p in ip:
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
    reason="Symlinks are not implemented on PyPy on Windows as of v7.3.3",
)
@pytest.mark.parametrize("dirs", [True, False])
def test_linked_iterpath_sort(dirs: bool, link_dir: Path) -> None:
    with iterpath(link_dir, sort=True, dirs=dirs) as ip:
        assert list(ip) == [
            link_dir / "apple.txt",
            link_dir / "banana.txt",
            link_dir / "link",
            link_dir / "mango.txt",
        ]


@pytest.mark.xfail(
    platform.system() == "Windows" and platform.python_implementation() == "PyPy",
    reason="Symlinks are not implemented on PyPy on Windows as of v7.3.3",
)
def test_linked_iterpath_sort_followlinks(link_dir: Path) -> None:
    with iterpath(link_dir, sort=True, followlinks=True) as ip:
        assert list(ip) == [
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
    reason="Symlinks are not implemented on PyPy on Windows as of v7.3.3",
)
def test_linked_iterpath_sort_followlinks_no_dirs(link_dir: Path) -> None:
    with iterpath(link_dir, sort=True, followlinks=True, dirs=False) as ip:
        assert list(ip) == [
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
def test_iterpath_sort_bytes(tree01: Path) -> None:
    with iterpath(bytes(tree01), sort=True) as ip:
        assert list(ip) == [
            tree01 / ".config",
            tree01 / ".config" / "cfg.ini",
            tree01 / ".hidden",
            tree01 / "foo.txt",
            tree01 / "glarch",
            tree01 / "glarch" / "bar.txt",
            tree01 / "gnusto",
            tree01 / "gnusto" / "cleesh.txt",
            tree01 / "gnusto" / "quux",
            tree01 / "gnusto" / "quux" / "quism.txt",
            tree01 / "xyzzy.txt",
        ]


@pytest.mark.parametrize("return_relative", [False, True])
def test_iterpath_sort_default_curdir(
    monkeypatch: pytest.MonkeyPatch, tree01: Path, return_relative: bool
) -> None:
    monkeypatch.chdir(tree01)
    with iterpath(sort=True, return_relative=return_relative) as ip:
        assert list(ip) == [
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


def test_iterpath_sort_return_relative(tree01: Path) -> None:
    with iterpath(tree01, sort=True, return_relative=True) as ip:
        assert list(ip) == [
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


def test_iterpath_sort_return_relative_include_root(tree01: Path) -> None:
    with iterpath(tree01, sort=True, return_relative=True, include_root=True) as ip:
        assert list(ip) == [
            Path(),
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


def test_iterpath_sort_return_relative_no_topdown(tree01: Path) -> None:
    with iterpath(tree01, sort=True, return_relative=True, topdown=False) as ip:
        assert list(ip) == [
            Path(".config", "cfg.ini"),
            Path(".config"),
            Path(".hidden"),
            Path("foo.txt"),
            Path("glarch", "bar.txt"),
            Path("glarch"),
            Path("gnusto", "cleesh.txt"),
            Path("gnusto", "quux", "quism.txt"),
            Path("gnusto", "quux"),
            Path("gnusto"),
            Path("xyzzy.txt"),
        ]


def test_iterpath_break_early(tree01: Path) -> None:
    # Test that no ResourceWarning is raised
    with iterpath(tree01) as ip:
        next(ip)
