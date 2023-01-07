# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


with open("./README.md") as f:
    long_description = f.read()

setup(
    name="pytest-github-actions-annotate-failures",
    version="0.1.8",
    description="pytest plugin to annotate failed tests with a workflow command for GitHub Actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="utgwkk",
    author_email="utagawakiki@gmail.com",
    url="https://github.com/pytest-dev/pytest-github-actions-annotate-failures",
    license="MIT",
    classifiers=[
        "Framework :: Pytest",
    ],
    python_requires=">=3.7",
    packages=find_packages(),
    entry_points={
        "pytest11": [
            "pytest_github_actions_annotate_failures = pytest_github_actions_annotate_failures.plugin",
        ],
    },
    install_requires=[
        "pytest>=4.0.0",
    ],
)
