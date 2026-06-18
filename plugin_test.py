from __future__ import annotations

from collections import Counter

import pytest
from packaging import version

PYTEST_VERSION = version.parse(pytest.__version__)
pytest_plugins = "pytester"


def test_annotation_succeed_no_output(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_success():
            assert 1
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.no_fnmatch_line("::error file=test_annotation_succeed_no_output.py*")


def test_annotation_pytest_error(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
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
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()

    result.stderr.re_match_lines(
        [
            r"::error file=test_annotation_pytest_error\.py,line=8::test_error.*",
        ]
    )


def test_annotation_fail(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_fail.py,line=5::test_fail*assert 0*",
        ]
    )


def test_annotation_exception(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            raise Exception('oops')
            assert 1
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_exception.py,line=5::test_fail*oops*",
        ]
    )


def test_annotation_warning(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
        """
        import warnings
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            warnings.warn('beware', Warning)
            assert 1
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::warning file=test_annotation_warning.py,line=6::beware",
        ]
    )


def test_annotation_exclude_warnings(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import warnings
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            warnings.warn('beware', Warning)
            assert 1
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess("--exclude-warning-annotations")
    assert not result.stderr.lines


def test_annotation_warning_cwd(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import warnings
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            warnings.warn('beware', Warning)
            assert 1
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_WORKSPACE", str(pytester.path.parent))
    pytester.mkdir("foo")
    pytester.makefile(".ini", pytest="[pytest]\ntestpaths=..")
    result = pytester.runpytest_subprocess("--rootdir=foo")
    result.stderr.fnmatch_lines(
        [
            "::warning file=test_annotation_warning_cwd0/test_annotation_warning_cwd.py,line=6::beware",
        ]
    )


def test_annotation_third_party_exception(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        my_module="""
        def fn():
            raise Exception('oops')
        """
    )

    pytester.makepyfile(
        """
        import pytest
        from my_module import fn
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            fn()
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_third_party_exception.py,line=6::test_fail*oops*",
        ]
    )


def test_annotation_third_party_warning(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        my_module="""
        import warnings

        def fn():
            warnings.warn('beware', Warning)
        """
    )

    pytester.makepyfile(
        """
        import pytest
        from my_module import fn
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            fn()
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        # ["::warning file=test_annotation_third_party_warning.py,line=6::beware",]
        [
            "::warning file=my_module.py,line=4::beware",
        ]
    )


def test_annotation_warning_runpath(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import warnings
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_warning():
            warnings.warn('beware', Warning)
            assert 1
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("PYTEST_RUN_PATH", "some_path")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::warning file=some_path/test_annotation_warning_runpath.py,line=6::beware",
        ]
    )


def test_annotation_fail_disabled_outside_workflow(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "")
    result = pytester.runpytest_subprocess()
    result.stderr.no_fnmatch_line(
        "::error file=test_annotation_fail_disabled_outside_workflow.py*"
    )


def test_annotation_fail_cwd(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_WORKSPACE", str(pytester.path.parent))
    pytester.mkdir("foo")
    pytester.makefile(".ini", pytest="[pytest]\ntestpaths=..")
    result = pytester.runpytest_subprocess("--rootdir=foo")
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_fail_cwd0/test_annotation_fail_cwd.py,line=5::test_fail*assert 0*",
        ]
    )


def test_annotation_fail_runpath(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("PYTEST_RUN_PATH", "some_path")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=some_path/test_annotation_fail_runpath.py,line=5::test_fail*assert 0*",
        ]
    )


def test_annotation_long(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
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
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_long.py,line=17::test_fail*assert 8 == 3*where 8 = f(8)*",
        ]
    )
    result.stderr.no_fnmatch_line("::*assert x += 1*")


def test_class_method(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        class TestClass(object):
            def test_method(self):
                x = 1
                assert x == 2
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_class_method.py,line=7::TestClass.test_method*assert 1 == 2*",
        ]
    )
    result.stderr.no_fnmatch_line("::*x = 1*")


def test_annotation_param(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
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
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_param.py,line=11::test_param?other?1*assert 2 == 3*",
        ]
    )


@pytest.mark.skipif(
    version.parse("9.0.0") > PYTEST_VERSION,
    reason="subtests are only supported in pytest 9+",
)
def test_annotation_subtest(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test(subtests):
            for i in range(5):
                with subtests.test(msg="custom message", i=i):
                    assert i % 2 == 0
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess()

    assert len(result.stderr.lines) == 2
    result.stderr.fnmatch_lines(
        [
            "::error file=test_annotation_subtest.py,line=7::test *custom message* *i=1*assert (1 %25 2) == 0*",
            "::error file=test_annotation_subtest.py,line=7::test *custom message* *i=3*assert (3 %25 2) == 0*",
        ]
    )


def test_with_xdist(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch):
    pytester.makepyfile(
        """
        import pytest
        import warnings
        import sys
        pytest_plugins = ['pytest_github_actions_annotate_failures','xdist']

        @pytest.mark.parametrize("n", range(10))
        def test_fails(n):
            warnings.warn(f"running {n}th")
            assert n == 100
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess("-n", "10", "-s")
    lines = Counter(
        line for line in result.errlines if line.startswith(("::error ", "::warning "))
    )

    assert len(lines) == 20
    assert {*lines.values()} == {1}


def test_annotation_rerunfailures_all_fail(testdir: pytest.Testdir):
    """Intermediate rerun failures should also be annotated."""
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = ['pytest_github_actions_annotate_failures', 'rerunfailures']

        def test_always_fails():
            assert 0
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess("--reruns", "2")
    lines = [
        line
        for line in result.errlines
        if line.startswith("::error file=test_annotation_rerunfailures_all_fail.py")
    ]
    # 1 initial run + 2 reruns = 3 annotations
    assert len(lines) == 3


def test_annotation_rerunfailures_eventually_passes(testdir: pytest.Testdir):
    """Failures before a test eventually passes should still be annotated."""
    testdir.makepyfile(
        """
        import pytest
        pytest_plugins = ['pytest_github_actions_annotate_failures', 'rerunfailures']

        _attempt = 0

        def test_flaky():
            global _attempt
            _attempt += 1
            assert _attempt >= 2
        """
    )
    testdir.monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = testdir.runpytest_subprocess("--reruns", "2")
    lines = [
        line
        for line in result.errlines
        if line.startswith(
            "::error file=test_annotation_rerunfailures_eventually_passes.py"
        )
    ]
    # 1 initial failure, then passes on second attempt → 1 annotation
    assert len(lines) == 1


def test_with_xdist_and_rerunfailures(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
):
    """Rerun annotations are emitted when xdist and rerunfailures are used together.

    Under xdist, workers handle reruns and forward each rerun report to the
    controller. The plugin is only registered on the controller, so the
    controller's pytest_runtest_logreport sees both the intermediate 'rerun'
    outcomes and the final 'failed' outcome — exactly once each.
    """
    pytester.makepyfile(
        """
        import pytest
        pytest_plugins = ['pytest_github_actions_annotate_failures', 'xdist', 'rerunfailures']

        def test_always_fails():
            assert 0
        """
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    result = pytester.runpytest_subprocess("-n", "1", "--reruns", "2")
    lines = [
        line
        for line in result.errlines
        if line.startswith("::error file=test_with_xdist_and_rerunfailures.py")
    ]
    # 1 initial run + 2 reruns = 3 annotations, no duplicates
    assert len(lines) == 3


# Debugging / development tip:
# Add a breakpoint() to the place you are going to check,
# uncomment this example, and run it with:
#   GITHUB_ACTIONS=true pytest -k test_example
# def test_example():
#     x = 3
#     y = 4
#     assert x == y
