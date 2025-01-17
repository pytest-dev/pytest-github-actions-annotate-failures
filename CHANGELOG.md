# Changelog

## Unreleased

### Incompatible changes

- Test on Python 3.13 #89
- Support pytest 7.4+ #97 (thanks to @edgarrmondragon)
- Require Python 3.8+ #87 (thanks to @edgarrmondragon)
- Require pytest 6+ #86 (thanks to @edgarrmondragon)
- Speed up CI and testing #93
- Use Ruff formatter #96
- Use dependency-groups for tests #99

## 0.2.0 (2023-05-04)

### Incompatible changes

- Require python 3.7+ #66 (thanks to @ssbarnea)

### Other changes

- Fix publish package workflow #74
- Handle cases where pytest itself fails #70 (thanks to @edgarrmondragon)
- Adopt PEP-621 for packaging #65 (thanks to @ssbarnea)
- Bump pre-commit/action from 2.0.0 to 3.0.0 #56

## 0.1.8 (2022-12-20)

No functionality change.
- Change URL of PyPI project link #61
- Fix CI environment #62 (thanks to @henryiii, @nicoddemus)

## 0.1.7 (2022-07-02)

- add longrepr from plugin tests #50 (thanks to @helpmefindaname)
- Use latest major version for actions #51

## 0.1.6 (2021-12-8)

- Handle test failures without a line number #47 (thanks to @Tenzer)

## 0.1.5 (2021-10-24)

- Revert changes of version 0.1.4 #42

## 0.1.4 (2021-10-24)

- Ignore failures that are retried using [`pytest-rerunfailures`](https://pypi.org/project/pytest-rerunfailures/) plugin #40 (thanks to @billyvg)

## 0.1.3 (2021-07-31)

- Allow specifying a run path with `PYTEST_RUN_PATH` environment variable #29 (thanks to @michamos)

## 0.1.2 (2021-03-21)

- Fall back file path when ValueError on Windows #24
- ci: change Python version set #25
- doc: notice for Docker environments #27

## 0.1.1 (2020-10-13)

- Fix #21: stdout is captured by pytest-xdist #22 (thanks to @yihuang)

## 0.1.0 (2020-08-22)

- feat: better annotation structure (PR #14, thanks to @henryiii)

## 0.0.8 (2020-08-20)

- Convert relative path to path from repository root (fix #8 with PR #11 and #12, thanks to @henryiii)

## 0.0.7 (2020-08-20)

- Python 2.7 support

## 0.0.6 (2020-07-30)

- Enable this plugin only in GitHub Actions workflow

## 0.0.5 (2020-05-10)

- Remove unnecessary environment (PYTEST_PLUGINS) variable in README (thanks to @AlphaMycelium)

## 0.0.4 (2020-05-09)

- Always enabled whether or not in GitHub Actions workflow

## 0.0.3 (2020-05-09)

- Requires pytest >= 4.0.0

## 0.0.2 (2020-05-09)

- Add short description

## 0.0.1 (2020-05-09)

- First release
