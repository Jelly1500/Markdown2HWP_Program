1. 다음 명령어를 사용하여 해당 프로젝트를 로컬에 복제합니다.
git clone https://github.com/Jelly1500/Markdown2HWP_Program.git


2. python -m venv venv 명령어를 실행해서 가상환경을 생성합니다.


3. .\venv\Scripts\activate 명령어를 실행하여 가상환경에 진입합니다.

3-1. 다음과 같은 오류가 발생한다면 다음 명령어를 입력합니다.
+ CategoryInfo          : 보안 오류: (:) [], PSSecurityException
+ FullyQualifiedErrorId : UnauthorizedAccess

Get-ExecutionPolicy
위의 명령어 실행 후 Restricted가 출력된다면 아래의 명령어를 실행합니다.

Set-ExecutionPolicy Unrestricted -Scope CurrentUser

이후 3. .\venv\Scripts\activate 명령어를 다시 실행합니다.


4. pip install -r requirements.txt 명령어를 실행해서 필요한 의존성들을 설치합니다.
이후 파일들이 설치되었다면 5번으로 넘어갑니다.

4-1. requirements.txt가 존재하지 않을 경우 다음과 같은 과정을 진행합니다.
다음 명령어를 통해 requirements.txt의 위치를 확인합니다.

Get-ChildItem -Path C:\ -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "Markdown2HWP_Program" }

아래의 상황을 예로 들겠습니다.

    디렉터리: C:\Users\User\git


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----      2025-03-24   오후 5:39                Markdown2HWP_Program-1

cd.. 를 통해 현재 디렉터리를 전부 빠져 나온후 위에서 확인한 디렉터리로 이동합니다.
cd  C:\Users\User\git 
cd .\Markdown2HWP_Program\

이후 4번 명령어를 다시 실행합니다.
pip install -r requirements.txt


5. 아래의 명령어를 실행합니다.
cd demo
.\run.bat  


6.(선택사항) 보안을 위해 작업이 끝난 후 실행 정책을 원래대로 복구합니다.
Set-ExecutionPolicy Restricted -Scope CurrentUser
