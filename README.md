# pytest-github-actions-annotate-failures
Pytest plugin to annotate failed tests with a workflow command for GitHub Actions

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
