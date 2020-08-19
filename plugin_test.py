pytest_plugins = 'pytester'
import pytest
from packaging import version

# result.stdout.no_fnmatch_line() is added to testdir on pytest 5.3.0
# https://docs.pytest.org/en/stable/changelog.html#pytest-5-3-0-2019-11-19
def no_fnmatch_line(result, pattern):
    if version.parse(pytest.__version__) >= version.parse('5.3.0'):
        result.stdout.no_fnmatch_line(
            pattern + '*',
        )
    else:
        assert pattern not in result.stdout.str()

def test_annotation_succeed_no_output(testdir):
    testdir.makepyfile(
        '''
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_success():
            assert 1
        '''
    )
    testdir.monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    result = testdir.runpytest_subprocess()

    no_fnmatch_line(result, '::error file=test_annotation_succeed_no_output.py')

def test_annotation_fail(testdir):
    testdir.makepyfile(
        '''
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        '''
    )
    testdir.monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines([
        '::error file=test_annotation_fail.py,line=4::def test_fail():*',
    ])

def test_annotation_exception(testdir):
    testdir.makepyfile(
        '''
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            raise Exception('oops')
            assert 1
        '''
    )
    testdir.monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines([
        '::error file=test_annotation_exception.py,line=4::def test_fail():*',
    ])

def test_annotation_fail_disabled_outside_workflow(testdir):
    testdir.makepyfile(
        '''
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        '''
    )
    testdir.monkeypatch.setenv('GITHUB_ACTIONS', '')
    result = testdir.runpytest_subprocess()
    no_fnmatch_line(result, '::error file=test_annotation_fail_disabled_outside_workflow.py')
