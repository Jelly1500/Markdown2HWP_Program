## 프로그램 실행 방법
#### 1.다음 명령어를 사용하여 해당 프로젝트를 로컬에 복제합니다.
git clone https://github.com/Jelly1500/Markdown2HWP_Program.git
#### 2. python -m venv venv 명령어를 실행해서 가상환경을 생성합니다.
#### 3. '.\venv\Scripts\activate' 명령어를 실행하여 가상환경에 진입합니다.
####3-1. 다음과 같은 오류가 발생한다면 다음 명령어를 입력합니다.
```
+ CategoryInfo          : 보안 오류: (:) [], PSSecurityException
+ FullyQualifiedErrorId : UnauthorizedAccess
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

#### 4. pip install -r requirements.txt 명령어를 실행해서 필요한 의존성들을 설치합니다.
#### 5. 아래의 명령어를 실행합니다.
```
python .\demo\new_template\demo.py
```
#### 6.(선택사항) 보안을 위해 작업이 끝난 후 실행 정책을 원래대로 복구합니다.
```
Set-ExecutionPolicy Restricted -Scope CurrentUser
```
