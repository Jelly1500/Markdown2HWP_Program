# Third-Party Licenses

이 소프트웨어는 다음과 같은 오픈소스 소프트웨어를 포함하고 있으며, 각 라이브러리의 라이선스 조건을 준수합니다.
모든 라이선스 전문은 배포물의 `licenses/` 디렉토리에 포함되어 있습니다(자동 수집 스크립트 사용 시 `dist_licenses/licenses/`).

> **중요 고지**
>
> * 본 배포본은 **Qt for Python(PySide6)의 듀얼 라이선스 중 LGPL v3 옵션을 선택**합니다. 사용자는 LGPL v3에 따라 PySide6를 교체할 권리가 있습니다.
> * `certifi`는 **MPL 2.0**입니다. 라이브러리를 **수정한 경우에 한해** 수정 파일의 소스 공개 의무가 있습니다(수정하지 않았다면 고지로 충분).
> * MIT/BSD/Apache 2.0 등 **퍼미시브 라이선스**는 저작권 표시와 라이선스 전문 포함으로 조건이 충족됩니다.

---

## 라이브러리 목록

아래 표는 사용된 서드파티 라이브러리의 **이름, 버전, 라이선스, 출처/비고**를 정리한 것입니다.

| 라이브러리               |          버전 | 라이선스                                                 | 출처/비고                                 |
| ------------------- | ----------: | ---------------------------------------------------- | ------------------------------------- |
| beautifulsoup4      |      4.13.4 | MIT License                                          | PyPI, Beautiful Soup Documentation    |
| certifi             |   2025.7.14 | Mozilla Public License 2.0 (MPL 2.0)                 | PyPI, GitHub (certifi/python-certifi) |
| cffi                |      1.17.1 | MIT License                                          | PyPI                                  |
| charset-normalizer  |       3.4.2 | MIT License                                          | PyPI                                  |
| cryptography        |      45.0.5 | Apache License 2.0 또는 BSD 3-Clause License (듀얼 라이선스) | PyPI, GitHub (pyca/cryptography)      |
| et\_xmlfile         |       2.0.0 | MIT License                                          | PyPI                                  |
| idna                |        3.10 | BSD 3-Clause License                                 | PyPI                                  |
| jaraco.classes      |       3.4.0 | MIT License                                          | PyPI                                  |
| jaraco.context      |       6.0.1 | MIT License                                          | PyPI                                  |
| jaraco.functools    |       4.2.1 | MIT License                                          | PyPI                                  |
| keyboard            |      0.13.5 | MIT License                                          | PyPI                                  |
| keyring             |      25.6.0 | MIT License                                          | PyPI                                  |
| lxml                |       6.0.0 | BSD 3-Clause License                                 | PyPI                                  |
| Markdown            |       3.8.2 | BSD 3-Clause License                                 | PyPI                                  |
| mistune             |       3.1.3 | BSD 3-Clause License                                 | PyPI                                  |
| more-itertools      |      10.7.0 | MIT License                                          | PyPI                                  |
| numpy               |       2.3.2 | BSD 3-Clause License                                 | PyPI, GitHub (numpy/numpy)            |
| olefile             |        0.47 | BSD 2-Clause License                                 | PyPI                                  |
| openpyxl            |       3.1.5 | MIT License                                          | PyPI                                  |
| pandas              |       2.3.1 | BSD 3-Clause License                                 | PyPI, GitHub (pandas-dev/pandas)      |
| pillow              |      11.3.0 | Historical Permission Notice and Disclaimer (HPND)   | PyPI, GitHub (python-pillow/Pillow)   |
| pycparser           |        2.22 | BSD 3-Clause License                                 | PyPI                                  |
| pyhwpx              |       1.4.7 | MIT License                                          | PyPI                                  |
| pyperclip           |       1.9.0 | BSD 3-Clause License                                 | PyPI                                  |
| PySide6             |       6.9.1 | **LGPLv3 (선택)** *(또는 Qt 상용 라이선스)*                    | PyPI, Qt 공식 사이트                       |
| PySide6\_Addons     |       6.9.1 | **LGPLv3 (선택)** *(또는 Qt 상용 라이선스)*                    | PyPI, Qt 공식 사이트                       |
| PySide6\_Essentials |       6.9.1 | **LGPLv3 (선택)** *(또는 Qt 상용 라이선스)*                    | PyPI, Qt 공식 사이트                       |
| python-dateutil     | 2.9.0.post0 | Apache License 2.0 또는 BSD 3-Clause License (듀얼 라이선스) | PyPI                                  |
| pytz                |      2025.2 | MIT License                                          | PyPI                                  |
| pywin32             |         311 | Python Software Foundation License (PSF License)     | PyPI, GitHub (mhammond/pywin32)       |
| pywin32-ctypes      |       0.2.3 | BSD 3-Clause License                                 | PyPI                                  |
| requests            |      2.32.4 | Apache License 2.0                                   | PyPI                                  |
| shiboken6           |       6.9.1 | **LGPLv3 (선택)** *(또는 Qt 상용 라이선스)*                    | PyPI, Qt 공식 사이트                       |
| six                 |      1.17.0 | MIT License                                          | PyPI                                  |
| soupsieve           |         2.7 | MIT License                                          | PyPI                                  |
| typing\_extensions  |      4.14.1 | Python Software Foundation License (PSF License)     | PyPI                                  |
| tzdata              |      2025.2 | Apache License 2.0                                   | PyPI                                  |
| urllib3             |       2.5.0 | MIT License                                          | PyPI                                  |
| zstandard           |      0.23.0 | BSD 3-Clause License                                 | PyPI                                  |
| emoji               | 최신  | BSD 3-Clause License                                 | PyPI                                  |
| nuitka              | 최신  | Apache License 2.0                                   | PyPI                                  |

---

## 특별 고지

### PySide6 / PySide6\_Addons / PySide6\_Essentials / shiboken6 (LGPL v3 선택)

* 본 배포본은 위 패키지들의 **듀얼 라이선스 중 LGPL v3를 선택**합니다.
* 사용자는 LGPL v3에 따라 해당 라이브러리를 교체할 권리가 있습니다.
* LGPL v3 전문은 `licenses/LGPL-3.0.txt`와 각 패키지 폴더(`licenses/<패키지-버전>/LGPL-3.0.txt`)에 포함되어 있습니다.
* 원문: [https://www.gnu.org/licenses/lgpl-3.0.txt](https://www.gnu.org/licenses/lgpl-3.0.txt)

### certifi (MPL 2.0)

* **수정하지 않은 경우**: 라이선스 고지 및 전문 포함으로 충분합니다.
* **수정한 경우**: 수정한 파일에 한해 MPL 2.0에 따른 소스 공개 의무가 있습니다.
* 원문: [https://www.mozilla.org/MPL/2.0/](https://www.mozilla.org/MPL/2.0/)

---

## 준수 방법 요약

1. 배포물에 `THIRD_PARTY_LICENSES.md`와 `licenses/` 디렉토리를 포함합니다.
2. PySide6 관련 항목에 대해 **LGPL v3 선택 사실과 교체 가능성**을 고지합니다.
3. `certifi`(MPL 2.0) 등 카피레프트/약한 카피레프트 라이선스의 **조건을 문서화**합니다.
4. 퍼미시브 라이선스(MIT, BSD, Apache 2.0 등)는 **저작권 표시 및 라이선스 전문 포함**으로 충족합니다.

