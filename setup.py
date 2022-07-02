# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


with open("./README.md") as f:
    long_description = f.read()

setup(
    name="pytest-github-actions-annotate-failures",
    version="0.1.7",
    description="pytest plugin to annotate failed tests with a workflow command for GitHub Actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="utgwkk",
    author_email="utagawakiki@gmail.com",
    url="https://github.com/utgwkk/pytest-github-actions-annotate-failures",
    license="MIT",
    classifiers=["Framework :: Pytest",],
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    packages=find_packages(),
    entry_points={
        "pytest11": [
            "pytest_github_actions_annotate_failures = pytest_github_actions_annotate_failures.plugin",
        ],
    },
    install_requires=["pytest>=4.0.0",],
)
