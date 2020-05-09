pytest_plugins = 'pytester'
import pytest

def test_annotation_fail(testdir):
    testdir.makepyfile(
        '''
        import pytest
        pytest_plugins = 'pytest_github_actions_annotate_failures'

        def test_fail():
            assert 0
        '''
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        '::error file=test_annotation_fail.py,line=4::def test_fail():%0A*',
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
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        '::error file=test_annotation_exception.py,line=4::def test_fail():%0A*',
    ])
