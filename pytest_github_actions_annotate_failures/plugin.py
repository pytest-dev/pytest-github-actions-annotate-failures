from __future__ import annotations

import contextlib
import os
import sys
from typing import TYPE_CHECKING

import pytest
from _pytest._code.code import ExceptionRepr, ReprEntry
from packaging import version

if TYPE_CHECKING:
    from warnings import WarningMessage

    from _pytest.reports import TestReport


# Reference:
# https://docs.pytest.org/en/latest/writing_plugins.html#hookwrapper-executing-around-other-hooks
# https://docs.pytest.org/en/latest/writing_plugins.html#hook-function-ordering-call-example
# https://docs.pytest.org/en/stable/reference.html#pytest.hookspec.pytest_runtest_makereport
#
# Inspired by:
# https://github.com/pytest-dev/pytest/blob/master/src/_pytest/terminal.py


PYTEST_VERSION = version.parse(pytest.__version__)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: TestReport):
    """Handle test reporting for all pytest versions."""

    # enable only in a workflow of GitHub Actions
    # ref: https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return

    # Only handle failed tests in call phase
    if report.when == "call" and report.failed:
        filesystempath, lineno, _ = report.location

        if lineno is not None:
            # 0-index to 1-index
            lineno += 1

        longrepr = report.head_line or "test"

        # get the error message and line number from the actual error
        if isinstance(report.longrepr, ExceptionRepr):
            if report.longrepr.reprcrash is not None:
                longrepr += "\n\n" + report.longrepr.reprcrash.message
            tb_entries = report.longrepr.reprtraceback.reprentries
            if tb_entries:
                entry = tb_entries[0]
                # Handle third-party exceptions
                if isinstance(entry, ReprEntry) and entry.reprfileloc is not None:
                    lineno = entry.reprfileloc.lineno
                    filesystempath = entry.reprfileloc.path

            elif report.longrepr.reprcrash is not None:
                lineno = report.longrepr.reprcrash.lineno
        elif isinstance(report.longrepr, tuple):
            filesystempath, lineno, message = report.longrepr
            longrepr += "\n\n" + message
        elif isinstance(report.longrepr, str):
            longrepr += "\n\n" + report.longrepr

        workflow_command = _build_workflow_command(
            "error",
            compute_path(filesystempath),
            lineno,
            message=longrepr,
        )
        print(workflow_command, file=sys.stderr)


def compute_path(filesystempath: str) -> str:
    """Extract and process location information from the report."""
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
            rel_path = filesystempath
        if not rel_path.startswith(".."):
            filesystempath = rel_path

    return filesystempath


class _AnnotateWarnings:
    def pytest_warning_recorded(
        self,
        warning_message: WarningMessage,
        when: str,  # noqa: ARG002
        nodeid: str,  # noqa: ARG002
        location: tuple[str, int, str],  # noqa: ARG002
    ):
        # enable only in a workflow of GitHub Actions
        # ref: https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
        if os.environ.get("GITHUB_ACTIONS") != "true":
            return

        filesystempath = warning_message.filename
        workspace = os.environ.get("GITHUB_WORKSPACE")

        if workspace:
            try:
                rel_path = os.path.relpath(filesystempath, workspace)
            except ValueError:
                # os.path.relpath() will raise ValueError on Windows
                # when full_path and workspace have different mount points.
                rel_path = filesystempath
            if not rel_path.startswith(".."):
                filesystempath = rel_path
        else:
            with contextlib.suppress(ValueError):
                filesystempath = os.path.relpath(filesystempath)

        workflow_command = _build_workflow_command(
            "warning",
            filesystempath,
            warning_message.lineno,
            message=str(warning_message.message),
        )
        print(workflow_command, file=sys.stderr)


def pytest_addoption(parser):
    group = parser.getgroup("pytest_github_actions_annotate_failures")
    group.addoption(
        "--exclude-warning-annotations",
        action="store_true",
        default=False,
        help="Annotate failures in GitHub Actions.",
    )


def pytest_configure(config):
    if not config.option.exclude_warning_annotations:
        config.pluginmanager.register(_AnnotateWarnings(), "annotate_warnings")


def _build_workflow_command(
    command_name: str,
    file: str,
    line: int,
    end_line: int | None = None,
    column: int | None = None,
    end_column: int | None = None,
    title: str | None = None,
    message: str | None = None,
):
    """Build a command to annotate a workflow."""
    result = f"::{command_name} "

    entries = [
        ("file", file),
        ("line", line),
        ("endLine", end_line),
        ("col", column),
        ("endColumn", end_column),
        ("title", title),
    ]

    result = result + ",".join(f"{k}={v}" for k, v in entries if v is not None)

    if message is not None:
        result = result + "::" + _escape(message)

    return result


def _escape(s: str) -> str:
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
