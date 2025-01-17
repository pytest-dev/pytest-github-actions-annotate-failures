from __future__ import annotations

import os

import pytest
from packaging import version

PYTEST_VERSION = version.parse(pytest.__version__)
pytest_plugins = "pytester"


# result.stderr.no_fnmatch_line() was added to testdir on pytest 5.3.0
# https://docs.pytest.org/en/stable/changelog.html#pytest-5-3-0-2019-11-19
def no_fnmatch_line(result: pytest.RunResult, pattern: str):
    result.stderr.no_fnmatch_line(pattern + "*")


def test_annotation_succeed_no_output(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_success():
            assert 1
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()

    no_fnmatch_line(result, "::error file=test_annotation_succeed_no_output.py")


def test_annotation_pytest_error(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        @pytest.fixture
        def fixture():
            return 1

        def test_error():
            assert fixture() == 1
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()

    result.stderr.re_match_lines(
        [
            r"::error file=test_annotation_pytest_error\.py,line=8::test_error.*",
        ]
    )


def test_annotation_fail(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_fail.py,line=5::test_fail*assert 0*",
        ]
    )


def test_annotation_exception(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            raise Exception('oops')
            assert 1
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_exception.py,line=5::test_fail*oops*",
        ]
    )


def test_annotation_warning(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import warnings
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            warnings.warn('beware', Warning)
            assert 1
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::warning file=test_annotation_warning.py,line=6::beware",
        ]
    )


def test_annotation_exclude_warnings(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import warnings
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            warnings.warn('beware', Warning)
            assert 1
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess("--exclude-warning-annotations")
    assert not result.stderr.lines


def test_annotation_third_party_exception(testdir: pytest.Testdir):
    testdir.makepyfile(
        my_module="""
        def fn():
            raise Exception('oops')
        """
    )

    testdir.makepyfile(
        """
        import pytest
        from my_module import fn
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            fn()
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_third_party_exception.py,line=6::test_fail*oops*",
        ]
    )


def test_annotation_third_party_warning(testdir: pytest.Testdir):
    testdir.makepyfile(
        my_module="""
        import warnings

        def fn():
            warnings.warn('beware', Warning)
        """
    )

    testdir.makepyfile(
        """
        import pytest
        from my_module import fn
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            fn()
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        # ["::warning file=test_annotation_third_party_warning.py,line=6::beware",]
        [
            "::warning file=my_module.py,line=4::beware",
        ]
    )


def test_annotation_fail_disabled_outside_workflow(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "")
    result = testdir.runpytest_subprocess()
    no_fnmatch_line(
        result, "::error file=test_annotation_fail_disabled_outside_workflow.py*"
    )


def test_annotation_fail_cwd(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    testdir.monkeypatch.setenv("GITHUB_WORKSPACE", os.path.dirname(str(testdir.tmpdir)))
    testdir.mkdir("foo")
    testdir.makefile(".ini", pytest="[pytest]\ntestpaths=..")
    result = testdir.runpytest_subprocess("--rootdir=foo")
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_fail_cwd0/test_annotation_fail_cwd.py,line=5::test_fail*assert 0*",
        ]
    )


def test_annotation_fail_runpath(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    testdir.monkeypatch.setenv("PYTEST_RUN_PATH", "some_path")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=some_path/test_annotation_fail_runpath.py,line=5::test_fail*assert 0*",
        ]
    )


def test_annotation_long(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def f(x):
            return x

        def test_fail():
            x = 1
            x += 1
            x += 1
            x += 1
            x += 1
            x += 1
            x += 1
            x += 1

            assert f(x) == 3
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_long.py,line=17::test_fail*assert 8 == 3*where 8 = f(8)*",
        ]
    )
    no_fnmatch_line(result, "::*assert x += 1*")


def test_class_method(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        class TestClass(object):
            def test_method(self):
                x = 1
                assert x == 2
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_class_method.py,line=7::TestClass.test_method*assert 1 == 2*",
        ]
    )
    no_fnmatch_line(result, "::*x = 1*")


def test_annotation_param(testdir: pytest.Testdir):
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        @pytest.mark.parametrize("a", [1])
        @pytest.mark.parametrize("b", [2], ids=["other"])
        def test_param(a, b):

            a += 1
            b += 1

            assert a == b
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_param.py,line=11::test_param?other?1*assert 2 == 3*",
        ]
    )


# Debugging / development tip:
# Add a breakpoint() to the place you are going to check,
# uncomment this example, and run it with:
#   GITHUB_ACTIONS=true pytest -k test_example
# def test_example():
#     x = 3
#     y = 4
#     assert x == y
