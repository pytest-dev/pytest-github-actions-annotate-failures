# Changelog

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
