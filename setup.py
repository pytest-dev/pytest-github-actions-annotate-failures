from setuptools import setup, find_packages

with open("./README.md") as f:
    long_description = f.read()

setup(
    name="pytest-github-actions-annotate-failures",
    version="0.0.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="utgwkk",
    author_email="utagawakiki@gmail.com",
    url="https://github.com/utgwkk/pytest-github-actions-annotate-failures",
    license="MIT",
    classifiers=[
        "Framework :: Pytest",
    ],
    packages=find_packages(),
    entry_points={
        "pytest11": [
            "pytest_github_actions_annotate_failures = pytest_github_actions_annotate_failures.plugin",
        ],
    },
)
