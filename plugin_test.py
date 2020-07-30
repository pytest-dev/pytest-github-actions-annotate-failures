pytest_plugins = 'pytester'
import pytest

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
    testdir._method = 'subprocess'
    result = testdir.runpytest()
    result.stdout.no_fnmatch_line(
        '::error file=test_annotation_succeed_no_output.py*',
    )

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
    testdir._method = 'subprocess'
    result = testdir.runpytest()
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
    testdir._method = 'subprocess'
    result = testdir.runpytest()
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
    testdir._method = 'subprocess'
    result = testdir.runpytest()
    result.stdout.no_fnmatch_line(
        '::error file=test_annotation_fail_disabled_outside_workflow.py*',
    )
