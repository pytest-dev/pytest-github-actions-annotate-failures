# pytest-github-actions-annotate-failures
[Pytest](https://pypi.org/project/pytest/) plugin to annotate failed tests with a [workflow command for GitHub Actions](https://help.github.com/en/actions/reference/workflow-commands-for-github-actions)

## Usage
Just install and run pytest with this plugin in your workflow. For example,

```yaml
name: test

on:
  push:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - uses: actions/setup-python@v1
      with:
        python-version: 3.7

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install plugin
      run: pip install pytest-github-actions-annotate-failures

    - run: pytest
```

If your test is running in a Docker container, you have to install this plugin and manually set `GITHUB_ACTIONS` environment variable to `true` inside of Docker container. (For example, `docker-compose run --rm -e GITHUB_ACTIONS=true app -- pytest`)

If your tests are run from a subdirectory of the git repository, you have to set the `PYTEST_RUN_PATH` environment variable to the path of that directory relative to the repository root in order for GitHub to identify the files with errors correctly.

## Screenshot
[![Image from Gyazo](https://i.gyazo.com/b578304465dd1b755ceb0e04692a57d9.png)](https://gyazo.com/b578304465dd1b755ceb0e04692a57d9)
