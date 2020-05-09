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
      env:
        PYTEST_PLUGINS: pytest_github_actions_annotate_failures
```

## Screenshot
[![Image from Gyazo](https://i.gyazo.com/b578304465dd1b755ceb0e04692a57d9.png)](https://gyazo.com/b578304465dd1b755ceb0e04692a57d9)
