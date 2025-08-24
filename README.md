## 프로그램 실행 방법
### 프로그램 실행 전에 준비해야 할 사항
https://developer.hancom.com/hwpautomation
위 웹사이트에서 보안 모듈 해제에 대한 설명을 그대로 따라서 해야 오류가 없습니다.

#### 1. python 3.13.x 버전을 설치합니다.(해당 버전으로 통일 예정)
#### 2. 다음 명령어를 사용하여 해당 프로젝트를 로컬에 복제합니다.
git clone https://github.com/Jelly1500/Markdown2HWP_Program.git
#### 3. python -m venv venv 명령어를 실행해서 가상환경을 생성합니다.(python --version 명령어로 현재 활성화된 python이 3.13 버전이 맞는지 확인하기)
#### 3-1. 만약 현재 활성화된 python이 3.13이 아니라면 python 3.13 버전이 설치된 경로를 찾습니다.
#### 3-2. [3.13 버전 파이썬 응용프로그램 절대 경로] -m venv venv 명령어를 실행해서 가상환경을 생성합니다.
#### 4. '.\venv\Scripts\activate' 명령어를 실행하여 가상환경에 진입합니다.
#### 4-1. 다음과 같은 오류가 발생한다면 다음 명령어를 입력합니다.
```
+ CategoryInfo          : 보안 오류: (:) [], PSSecurityException
+ ErrorId : UnauthorizedAccess
```
```
Get-ExecutionPolicy
```
<br>
위의 명령어 실행 후 Restricted가 출력된다면 아래의 명령어를 실행합니다.

```
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```
이후 .\venv\Scripts\activate 명령어를 다시 실행합니다.

#### 5. pip install -r requirements.txt 명령어를 실행해서 필요한 의존성들을 설치합니다.
#### 6. 아래의 명령어를 실행합니다.
```
python run.py
```
#### 7.(선택사항) 보안을 위해 작업이 끝난 후 실행 정책을 원래대로 복구합니다.
```
Set-ExecutionPolicy Restricted -Scope CurrentUser
```

## 사용된 오픈소스 라이브러리

이 프로젝트는 다음과 같은 오픈소스 라이브러리들을 사용합니다:

### 주요 라이브러리
- **PySide6 (Qt for Python)**: LGPL v3 (선택됨) - The Qt Company Ltd.
- **PySide6_Addons**: LGPL v3 (선택됨) - The Qt Company Ltd.
- **PySide6_Essentials**: LGPL v3 (선택됨) - The Qt Company Ltd.
- **shiboken6**: LGPL v3 (선택됨) - The Qt Company Ltd.
- **requests**: Apache 2.0 - Kenneth Reitz
- **cryptography**: Apache 2.0 또는 BSD - Python Cryptographic Authority
- **certifi**: MPL 2.0 - Kenneth Reitz
- **numpy**: BSD - NumPy Developers
- **pandas**: BSD - Pandas Development Team
- **Pillow (PIL)**: HPND - Fredrik Lundh
- **lxml**: BSD - ElementTree contributors
- **keyring**: MIT - Jason R. Coombs
- **beautifulsoup4**: MIT - Leonard Richardson
- **Markdown**: BSD - Python-Markdown Project
- **cffi**: MIT - Armin Rigo
- **charset-normalizer**: MIT - TAHRI Ahmed
- **et_xmlfile**: MIT - Dave Kuhlman
- **idna**: BSD - Kim Davies
- **jaraco.classes**: MIT - Jason R. Coombs
- **jaraco.context**: MIT - Jason R. Coombs
- **jaraco.functools**: MIT - Jason R. Coombs
- **keyboard**: MIT - BoppreH
- **mistune**: BSD - Lei Zhou
- **more-itertools**: MIT - Erik Rose
- **olefile**: BSD - Philippe Lagadec
- **openpyxl**: MIT - Charlie Clark
- **pycparser**: BSD - Eli Bendersky
- **pyhwpx**: MIT - Mete0r
- **pyperclip**: BSD - Al Sweigart
- **python-dateutil**: Apache 2.0 또는 BSD - Gustavo Niemeyer
- **pytz**: MIT - Stuart Bishop
- **pywin32**: PSF License - Mark Hammond
- **pywin32-ctypes**: BSD - BreamoreBoy
- **six**: MIT - Benjamin Peterson
- **soupsieve**: MIT - Isaac Muse
- **typing_extensions**: PSF License - Guido van Rossum
- **tzdata**: Apache 2.0 - Python Software Foundation
- **urllib3**: MIT - Andrey Petrov
- **zstandard**: BSD - Yann Collet
- **emoji**: BSD - Taehoon Kim
- **nuitka**: Apache 2.0 - Kay Hayen

### 라이선스 고지
- **Qt와 Qt 로고는 The Qt Company Ltd.의 상표입니다.**
- **PySide6는 듀얼 라이선스 중 LGPL v3를 선택하여 사용합니다.**
- **certifi는 MPL 2.0 라이선스입니다 (수정 시에만 소스 공개 의무).**
- 각 라이브러리의 상세한 라이선스는 해당 프로젝트의 공식 웹사이트를 참조하세요.
- 이 프로젝트는 MIT 라이선스 하에 배포됩니다.
- **상세한 라이선스 정보**: [Third-Party Licenses](THIRD_PARTY_LICENSES.md)

### 📋 라이선스 정보 참조
이 프로그램은 오픈소스 소프트웨어를 포함합니다. 자세한 내용은 배포 폴더의 **THIRD_PARTY_LICENSES.md** 및 **licenses/** 폴더를 참조하십시오.

## 라이선스
이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.
