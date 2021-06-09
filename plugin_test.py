# -*- coding: utf-8 -*-
import os

from packaging import version

import pytest


pytest_plugins = "pytester"


# result.stderr.no_fnmatch_line() is added to testdir on pytest 5.3.0
# https://docs.pytest.org/en/stable/changelog.html#pytest-5-3-0-2019-11-19
def no_fnmatch_line(result, pattern):
    if version.parse(pytest.__version__) >= version.parse("5.3.0"):
        result.stderr.no_fnmatch_line(pattern + "*",)
    else:
        assert pattern not in result.stderr.str()


def test_annotation_succeed_no_output(testdir):
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


def test_annotation_fail(testdir):
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
        ["::error file=test_annotation_fail.py,line=5::test_fail*assert 0*",]
    )


def test_annotation_exception(testdir):
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
        ["::error file=test_annotation_exception.py,line=5::test_fail*oops*",]
    )


def test_annotation_fail_disabled_outside_workflow(testdir):
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


def test_annotation_fail_cwd(testdir):
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
        ["::error file=test_annotation_fail_cwd.py,line=5::test_fail*assert 0*",]
    )


def test_annotation_fail_runpath(testdir):
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
        ["::error file=some_path/test_annotation_fail_runpath.py,line=5::test_fail*assert 0*",]
    )


def test_annotation_long(testdir):
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


def test_class_method(testdir):
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


def test_annotation_param(testdir):
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
