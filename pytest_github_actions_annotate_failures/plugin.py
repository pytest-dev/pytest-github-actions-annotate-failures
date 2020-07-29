import os

def pytest_runtest_logreport(report):
    if report.outcome != 'failed':
        return

    # collect information to be annotated
    filesystempath, lineno, _ = report.location

    # 0-index to 1-index
    lineno += 1

    longrepr = str(report.longrepr)

    print(_error_workflow_command(filesystempath, lineno, longrepr))

def _error_workflow_command(filesystempath, lineno, longrepr):
    if lineno is None:
        if longrepr is None:
            return '\n::error file={}'.format(filesystempath)
        else:
            longrepr = _escape(longrepr)
            return '\n::error file={}::{}'.format(filesystempath, longrepr)
    else:
        if longrepr is None:
            return '\n::error file={},line={}'.format(filesystempath, lineno)
        else:
            longrepr = _escape(longrepr)
            return '\n::error file={},line={}::{}'.format(filesystempath, lineno, longrepr)

def _escape(s: str):
    return s.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
