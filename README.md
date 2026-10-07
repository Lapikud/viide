# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Lapikud/viide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                       |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------- | -------: | -------: | ------: | --------: |
| src/viide/\_\_init\_\_.py                  |        6 |        3 |     50% |     13-16 |
| src/viide/app/\_\_init\_\_.py              |        0 |        0 |    100% |           |
| src/viide/app/aka/\_\_init\_\_.py          |        0 |        0 |    100% |           |
| src/viide/app/aka/errors.py                |       22 |        0 |    100% |           |
| src/viide/app/aka/links.py                 |       24 |        0 |    100% |           |
| src/viide/app/aka/manager.py               |      110 |        0 |    100% |           |
| src/viide/app/aka/qr.py                    |       10 |        0 |    100% |           |
| src/viide/app/auth/\_\_init\_\_.py         |        0 |        0 |    100% |           |
| src/viide/app/auth/client.py               |        4 |        0 |    100% |           |
| src/viide/app/auth/clients/\_\_init\_\_.py |        0 |        0 |    100% |           |
| src/viide/app/auth/clients/freeipa.py      |       23 |       11 |     52% |     29-44 |
| src/viide/app/auth/clients/ldap.py         |       41 |       41 |      0% |      3-82 |
| src/viide/app/auth/errors.py               |       10 |        0 |    100% |           |
| src/viide/app/auth/manager.py              |       17 |        0 |    100% |           |
| src/viide/app/auth/user.py                 |        6 |        0 |    100% |           |
| src/viide/app/db.py                        |        4 |        0 |    100% |           |
| src/viide/app/storage.py                   |       11 |        0 |    100% |           |
| src/viide/config.py                        |       23 |        1 |     96% |        60 |
| src/viide/db/\_\_init\_\_.py               |        0 |        0 |    100% |           |
| src/viide/db/base.py                       |        4 |        0 |    100% |           |
| src/viide/db/engine.py                     |       14 |        2 |     86% |     24-25 |
| src/viide/db/models/\_\_init\_\_.py        |        2 |        0 |    100% |           |
| src/viide/db/models/link.py                |       13 |        0 |    100% |           |
| src/viide/db/models/qr.py                  |       10 |        0 |    100% |           |
| src/viide/db/models/user.py                |        0 |        0 |    100% |           |
| src/viide/db/repositories/\_\_init\_\_.py  |        0 |        0 |    100% |           |
| src/viide/db/repositories/link.py          |       31 |       16 |     48% |22-31, 35-37, 41-45, 49-56, 60-61 |
| src/viide/db/repositories/qr.py            |       19 |        8 |     58% |20-22, 26-28, 32-33 |
| src/viide/storage/\_\_init\_\_.py          |        0 |        0 |    100% |           |
| src/viide/storage/client.py                |       32 |       13 |     59% |38-43, 47-55, 59-62 |
| src/viide/web/\_\_init\_\_.py              |        0 |        0 |    100% |           |
| src/viide/web/app.py                       |       26 |        0 |    100% |           |
| src/viide/web/extensions.py                |       15 |        0 |    100% |           |
| src/viide/web/routes.py                    |       64 |        0 |    100% |           |
| **TOTAL**                                  |  **541** |   **95** | **82%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/Lapikud/viide/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Lapikud/viide/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Lapikud/viide/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/Lapikud/viide/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FLapikud%2Fviide%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/Lapikud/viide/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.