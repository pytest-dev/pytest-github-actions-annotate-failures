
from __future__ import annotations

import os
import sys
from collections import OrderedDict

import pytest
from _pytest._code.code import ExceptionRepr

try:
    from xdist import is_xdist_worker

except ImportError:
    def is_xdist_worker(request_or_session):
        return hasattr(request_or_session.config, "workerinput")


# Reference:
# https://docs.pytest.org/en/latest/writing_plugins.html#hookwrapper-executing-around-other-hooks
# https://docs.pytest.org/en/latest/writing_plugins.html#hook-function-ordering-call-example
# https://docs.pytest.org/en/stable/reference.html#pytest.hookspec.pytest_runtest_logreport
#
# Inspired by:
# https://github.com/pytest-dev/pytest/blob/master/src/_pytest/terminal.py


class Reporter:
    def pytest_runtest_logreport(self, report: pytest.TestReport):
        if report.when == "call" and report.failed:
            # collect information to be annotated
            filesystempath, lineno, domaininfo = report.location

            runpath = os.environ.get("PYTEST_RUN_PATH")
            if runpath:
                filesystempath = os.path.join(runpath, filesystempath)

            # try to convert to absolute path in GitHub Actions
            workspace = os.environ.get("GITHUB_WORKSPACE")
            if workspace:
                full_path = os.path.abspath(filesystempath)
                try:
                    rel_path = os.path.relpath(full_path, workspace)
                except ValueError:
                    # os.path.relpath() will raise ValueError on Windows
                    # when full_path and workspace have different mount points.
                    # https://github.com/utgwkk/pytest-github-actions-annotate-failures/issues/20
                    rel_path = filesystempath
                if not rel_path.startswith(".."):
                    filesystempath = rel_path

            if lineno is not None:
                # 0-index to 1-index
                lineno += 1

            # get the name of the current failed test, with parametrize info
            longrepr = getattr(report, 'head_line', None)

            if not longrepr:
                # BaseReport.head_line currently does this
                longrepr = domaininfo

            if not longrepr:
                # Should not happen
                longrepr = _remove_prefix(report.nodeid, f'{report.fspath}::')

            # get the error message and line number from the actual error
            if isinstance(report.longrepr, ExceptionRepr):
                if report.longrepr.reprcrash is not None:
                    longrepr += "\n\n" + report.longrepr.reprcrash.message
                tb_entries = report.longrepr.reprtraceback.reprentries
                if len(tb_entries) > 1 and tb_entries[0].reprfileloc is not None:
                    # Handle third-party exceptions
                    lineno = tb_entries[0].reprfileloc.lineno
                elif report.longrepr.reprcrash is not None:
                    lineno = report.longrepr.reprcrash.lineno
            elif isinstance(report.longrepr, tuple):
                _, lineno, message = report.longrepr
                longrepr += "\n\n" + message
            elif isinstance(report.longrepr, str):
                longrepr += "\n\n" + report.longrepr

            print(
                _error_workflow_command(filesystempath, lineno, longrepr), file=sys.stderr
            )


def _error_workflow_command(filesystempath, lineno, longrepr):
    # Build collection of arguments. Ordering is strict for easy testing
    details_dict = OrderedDict()
    details_dict["file"] = filesystempath
    if lineno is not None:
        details_dict["line"] = lineno

    details = ",".join(f"{k}={v}" for k, v in details_dict.items())

    if longrepr is None:
        return f"\n::error {details}"

    longrepr = _escape(longrepr)
    return f"\n::error {details}::{longrepr}"


def _escape(s):
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _remove_prefix(s, prefix):
    # Replace with built-in `.removeprefix()` when Python 3.8 support is dropped
    return s[len(prefix):] if s.startswith(prefix) else s


def pytest_sessionstart(session: pytest.Session):
    # enable only in a workflow of GitHub Actions
    # ref: https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return

    # print commands only from the main xdist process
    if is_xdist_worker(session):
        return

    session.config.pluginmanager.register(Reporter())
