from unittest.mock import Mock
import pytest
from iterpath import (
    SELECT_DOTS,
    SELECT_VCS,
    SELECT_VCS_DIRS,
    SELECT_VCS_FILES,
    SelectAny,
    SelectGlob,
    SelectNames,
    SelectRegex,
)


@pytest.mark.parametrize(
    "name,r",
    [
        ("foo.txt", True),
        ("bar.png", True),
        (".gh", True),
        ("barfoo.txt", False),
        ("foo.png", False),
        ("", False),
        (".ghignore", False),
        ("foobar.txt", False),
        ("foo", False),
        ("FOO.TXT", False),
    ],
)
def test_select_names(name: str, r: bool) -> None:
    s = SelectNames("foo.txt", "bar.png", ".gh")
    entry = Mock()
    entry.configure_mock(name=name)
    assert s(entry) is r


@pytest.mark.parametrize(
    "name,r",
    [
        ("foo.txt", True),
        ("bar.png", True),
        (".gh", True),
        ("barfoo.txt", False),
        ("foo.png", False),
        ("", False),
        (".ghignore", False),
        ("foobar.txt", False),
        ("foo", False),
        ("FOO.TXT", True),
        (".GH", True),
        ("BaR.pNG", True),
    ],
)
def test_select_names_insensitive(name: str, r: bool) -> None:
    s = SelectNames("FOO.txt", "bar.png", ".gh", case_sensitive=False)
    entry = Mock()
    entry.configure_mock(name=name)
    assert s(entry) is r


def test_select_names_repr() -> None:
    s = SelectNames("FOO.txt", "bar.PNG", ".gh")
    assert repr(s) == "SelectNames('.gh', 'FOO.txt', 'bar.PNG', case_sensitive=True)"


def test_select_names_repr_insensitive() -> None:
    s = SelectNames("FOO.txt", "bar.PNG", ".gh", case_sensitive=False)
    assert repr(s) == "SelectNames('.gh', 'bar.png', 'foo.txt', case_sensitive=False)"


def test_select_names_eq() -> None:
    s = SelectNames("foo.txt", "bar.png", ".gh")
    assert s == SelectNames(".gh", "foo.txt", "bar.png")
    assert s != SelectNames(".gh", "foo.txt", "bar.png", case_sensitive=False)
    assert s != SelectNames(".gh", "foo.txt", "bar.png", "quux.pdf")
    assert s != SelectNames(".gh", "foo.txt")
    assert s != {"foo.txt", "bar.png", ".gh"}
    assert SelectNames("FOO", "BaR", case_sensitive=False) == SelectNames(
        "foo", "bar", case_sensitive=False
    )


@pytest.mark.parametrize(
    "name,r",
    [
        ("foo.txt", True),
        (".txt", True),
        ("foo.txtual", False),
        ("foo", False),
        ("txt", False),
        ("foo.bar.txt", True),
        ("foo.txt.bar", False),
        ("", False),
    ],
)
def test_select_glob(name: str, r: bool) -> None:
    s = SelectGlob("*.txt")
    entry = Mock()
    entry.configure_mock(name=name)
    assert s(entry) is r


@pytest.mark.parametrize(
    "name,r",
    [
        ("abab", True),
        ("abab.txt", True),
        ("foo.abab", True),
        ("ab", False),
        ("foo.ab", False),
        ("", False),
        ("baba", False),
        ("abababab", True),
        ("xababababy", True),
    ],
)
def test_select_regex(name: str, r: bool) -> None:
    s = SelectRegex(r"(abab)+")
    entry = Mock()
    entry.configure_mock(name=name)
    assert s(entry) is r


@pytest.mark.parametrize(
    "name,r",
    [
        (".foo", True),
        (".foo.txt", True),
        ("foo.txt", False),
        ("..foo", True),
    ],
)
def test_select_dots(name: str, r: bool) -> None:
    entry = Mock()
    entry.configure_mock(name=name)
    assert SELECT_DOTS(entry) is r


@pytest.mark.parametrize(
    "name,r",
    [
        ("foo", True),
        ("bar.txt", True),
        ("foo.txt", True),
        ("txt.foo", False),
        ("txt", False),
        (".foo", False),
        ("foo.png", True),
        ("foobar", True),
        ("barfoo", False),
        (".txt.png", False),
        (".txt.txt", True),
    ],
)
def test_select_any(name: str, r: bool) -> None:
    s1 = SelectRegex("^foo")
    s2 = SelectGlob("*.txt")
    sor = s1 | s2
    entry = Mock()
    entry.configure_mock(name=name)
    assert sor(entry) is r


def test_or() -> None:
    s1 = SelectRegex("^foo")
    s2 = SelectGlob("*.txt")
    sor = s1 | s2
    assert isinstance(sor, SelectAny)
    assert sor == SelectAny([s1, s2])


def test_or3() -> None:
    s1 = SelectRegex("^foo")
    s2 = SelectGlob("*.txt")
    s3 = SelectNames("foo.txt")
    sor = s1 | s2 | s3
    assert isinstance(sor, SelectAny)
    assert sor == SelectAny([s1, s2, s3])


def test_or_or() -> None:
    s1 = SelectRegex("^foo")
    s2 = SelectGlob("*.txt")
    s3 = SelectNames("foo.txt")
    s4 = SelectNames("gnusto", "cleesh")
    sor1 = s1 | s2
    sor2 = s3 | s4
    sor = sor1 | sor2
    assert sor == SelectAny([s1, s2, s3, s4])


@pytest.mark.parametrize(
    "name,r",
    [
        (".git", True),
        ("git", False),
        ("_git", False),
        (".gitignore", False),
        ("foo.git", False),
        (".hg", True),
        ("_darcs", True),
        (".darcs", False),
        (".bzr", True),
        (".svn", True),
        ("_svn", True),
        ("CVS", True),
        ("cvs", False),
        (".cvs", False),
        ("RCS", True),
        ("rcs", False),
        (".rcs", False),
        ("foo.txt", False),
    ],
)
def test_select_vcs_dirs(name: str, r: bool) -> None:
    entry = Mock()
    entry.configure_mock(name=name)
    assert SELECT_VCS_DIRS(entry) is r


@pytest.mark.parametrize(
    "name,r",
    [
        (".git", False),
        (".gitattributes", True),
        (".gitignore", True),
        ("_gitignore", False),
        (".gitmodules", True),
        (".gitfoo", False),
        (".mailmap", True),
        (".gitmailmap", False),
        (".hgignore", True),
        (".hgsigs", True),
        (".hgtags", True),
        (".binaries", True),
        (".boring", True),
        (".bzrignore", True),
        ("foo.txt,v", True),
        (",v", False),
        (".gitignore,v", True),
        ("foo.txt", False),
    ],
)
def test_select_vcs_files(name: str, r: bool) -> None:
    entry = Mock()
    entry.configure_mock(name=name)
    assert SELECT_VCS_FILES(entry) is r


@pytest.mark.parametrize(
    "name,r",
    [
        (".git", True),
        ("git", False),
        ("_git", False),
        ("foo.git", False),
        (".hg", True),
        ("_darcs", True),
        (".darcs", False),
        (".bzr", True),
        (".svn", True),
        ("_svn", True),
        ("CVS", True),
        ("cvs", False),
        (".cvs", False),
        ("RCS", True),
        ("rcs", False),
        (".rcs", False),
        (".gitattributes", True),
        (".gitignore", True),
        ("_gitignore", False),
        (".gitmodules", True),
        (".gitfoo", False),
        (".mailmap", True),
        (".gitmailmap", False),
        (".hgignore", True),
        (".hgsigs", True),
        (".hgtags", True),
        (".binaries", True),
        (".boring", True),
        (".bzrignore", True),
        ("foo.txt,v", True),
        (",v", False),
        (".gitignore,v", True),
        ("foo.txt", False),
    ],
)
def test_select_vcs(name: str, r: bool) -> None:
    entry = Mock()
    entry.configure_mock(name=name)
    assert SELECT_VCS(entry) is r
