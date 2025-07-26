#!/usr/bin/env python
"""
마크다운-HWP 변환기 EXE 빌드 스크립트 (PyInstaller 버전 - Qt 충돌 해결)
"""
import os
import sys
import shutil
import subprocess
import time

def setup_env():
    """빌드에 필요한 패키지 설치"""
    print("빌드 환경 설정 중...")
    
    # 빌드용 requirements 파일이 있으면 사용
    if os.path.exists("requirements-build.txt"):
        print("빌드용 requirements 파일을 사용합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"])
    else:
        # 기본 requirements 파일 사용
        if os.path.exists("requirements.txt"):
            print("기본 requirements 파일을 사용합니다...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            # 개별 패키지 설치
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller 버전 확인
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    print(f"PyInstaller 버전: {version}")
                    break
    except Exception as e:
        print(f"PyInstaller 버전 확인 중 오류: {e}")
    
    print("패키지 설치 완료")

def check_qt_conflicts():
    """Qt 라이브러리 충돌 확인 및 해결"""
    print("Qt 라이브러리 충돌 확인 중...")
    
    # PySide6와 PyQt5 설치 여부 확인
    try:
        import PySide6
        pyside6_installed = True
    except ImportError:
        pyside6_installed = False
    
    try:
        import PyQt5
        pyqt5_installed = True
    except ImportError:
        pyqt5_installed = False
    
    if pyqt5_installed and pyside6_installed:
        print("경고: PyQt5와 PySide6이 모두 설치되어 있습니다.")
        print("PyInstaller 빌드 시 충돌이 발생할 수 있습니다.")
        print("해결 방법:")
        print("1. 가상환경을 새로 만들어서 필요한 Qt 라이브러리만 설치")
        print("2. 사용하지 않는 Qt 라이브러리 제거")
        print("3. --exclude-module 옵션으로 불필요한 모듈 제외")
        
        # 사용자에게 선택권 제공
        choice = input("계속 진행하시겠습니까? (y/n): ").lower()
        if choice != 'y':
            print("빌드를 중단합니다.")
            return False
    
    return True

def clean_build_dirs():
    """빌드 전 이전 빌드 파일 정리"""
    print("이전 빌드 파일 정리 중...")
    
    def retry_rmtree(path, max_retries=3, retry_delay=2):
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"재시도 {attempt}/{max_retries}...")
                    time.sleep(retry_delay)
                shutil.rmtree(path)
                return True
            except (PermissionError, OSError) as e:
                print(f"시도 {attempt+1}/{max_retries} 실패: {e}")
                if attempt == max_retries - 1:
                    print(f"경고: {path} 디렉토리를 삭제할 수 없습니다. 파일이 사용 중일 수 있습니다.")
                    return False
    
    # build 디렉토리 삭제
    if os.path.exists("build"):
        print("build 디렉토리 삭제 시도 중...")
        retry_rmtree("build")
    
    # dist 디렉토리 삭제
    if os.path.exists("dist"):
        print("dist 디렉토리 삭제 시도 중...")
        time.sleep(1)
        retry_rmtree("dist")
    
    # spec 파일 삭제
    for item in os.listdir("."):
        if item.endswith(".spec"):
            try:
                os.remove(item)
                print(f"{item} 파일 삭제 완료")
            except (PermissionError, OSError) as e:
                print(f"주의: {item} 파일 삭제 중 오류 발생: {e}")
    
    print("이전 빌드 파일 정리 완료")

def build_exe():
    """PyInstaller를 사용하여 EXE 빌드 (Qt 충돌 해결)"""
    print("EXE 파일 빌드 중...")
    
    # 아이콘 파일 유무 확인
    icon_option = []
    if os.path.exists("icon.ico"):
        icon_option = ["--icon", "icon.ico"]
    elif os.path.exists("icon.png"):
        icon_option = ["--icon", "icon.png"]
    
    # Qt 충돌 해결을 위한 exclude 옵션
    exclude_options = []
    
    # PyQt5가 설치되어 있으면 제외
    try:
        import PyQt5
        exclude_options.extend(["--exclude-module", "PyQt5"])
        print("PyQt5 모듈을 제외하고 빌드합니다.")
    except ImportError:
        pass
    
    # PySide6가 설치되어 있으면 제외 (반대 경우)
    try:
        import PySide6
        # PySide6는 사용할 것이므로 제외하지 않음
    except ImportError:
        pass
    
    # PyInstaller 명령행 옵션
    cmd = [
        "pyinstaller",
        "--name=마크다운_HWP_변환기",
        "--windowed",  # GUI 애플리케이션 (콘솔 창 없음)
        "--noconfirm", # 기존 빌드 파일 덮어쓰기
        "--clean",     # 임시 파일 정리
        "--add-data=md2hwp/new_template;md2hwp/new_template",  # 템플릿 파일 포함
        "--add-data=md2hwp/new_template/템플릿문서.hml;md2hwp/new_template",  # 기본 템플릿 파일 포함
        "--hidden-import=zstandard",  # zstandard 패키지 명시적 포함
        "--hidden-import=PySide6",  # PySide6 명시적 포함
        "--onedir",    # 폴더 형태로 빌드 (실행 속도 향상)
    ]
    
    # 아이콘 옵션 추가
    cmd.extend(icon_option)
    
    # exclude 옵션 추가
    cmd.extend(exclude_options)
    
    # 메인 스크립트 추가
    cmd.append("run.py")
    
    print(f"실행할 명령어: {' '.join(cmd)}")
    
    # 명령 실행
    subprocess.check_call(cmd)
    print("EXE 빌드 완료")

def copy_additional_resources():
    """필요한 추가 리소스 파일 복사"""
    print("추가 리소스 복사 중...")
    
    dist_dir = os.path.join("dist", "마크다운_HWP_변환기")
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # README 파일 복사
    if os.path.exists("README.md"):
        try:
            shutil.copy("README.md", os.path.join(dist_dir, "README.txt"))
        except (PermissionError, OSError) as e:
            print(f"주의: README.md 복사 중 오류 발생: {e}")
    
    # 라이센스 파일 복사
    if os.path.exists("LICENSE"):
        try:
            shutil.copy("LICENSE", os.path.join(dist_dir, "LICENSE.txt"))
        except (PermissionError, OSError) as e:
            print(f"주의: LICENSE 복사 중 오류 발생: {e}")
    
    # convertedDocs 폴더 생성 (사용자 편의성 개선)
    try:
        os.makedirs(os.path.join(dist_dir, "convertedDocs"), exist_ok=True)
        print("convertedDocs 폴더 생성 완료")
    except (PermissionError, OSError) as e:
        print(f"주의: convertedDocs 폴더 생성 중 오류 발생: {e}")
        
    # new_template 폴더 직접 복사 (모든 템플릿 파일 포함)
    src_template = os.path.join("md2hwp", "new_template")
    dst_template = os.path.join(dist_dir, "new_template")
    
    print(f"템플릿 폴더 복사 시도:")
    print(f"  - 소스 경로: {src_template}")
    print(f"  - 대상 경로: {dst_template}")
    print(f"  - 소스 폴더 존재: {os.path.exists(src_template)}")
    
    if os.path.exists(src_template):
        try:
            print(f"템플릿 폴더 복사: {src_template} → {dst_template}")
            shutil.copytree(src_template, dst_template)
            print("템플릿 폴더 복사 완료")
            
            # 복사된 파일 목록 출력
            if os.path.exists(dst_template):
                copied_files = os.listdir(dst_template)
                print(f"복사된 템플릿 파일들: {copied_files}")
        except (PermissionError, OSError) as e:
            print(f"주의: 템플릿 폴더 복사 중 오류 발생: {e}")
            
            # 대안: 빈 템플릿 폴더 생성
            try:
                os.makedirs(dst_template, exist_ok=True)
                print(f"빈 템플릿 폴더 생성: {dst_template}")
            except Exception as alt_e:
                print(f"빈 템플릿 폴더 생성도 실패: {alt_e}")
    else:
        print(f"경고: 소스 템플릿 폴더가 존재하지 않습니다: {src_template}")
        # 빈 템플릿 폴더 생성
        try:
            os.makedirs(dst_template, exist_ok=True)
            print(f"빈 템플릿 폴더 생성: {dst_template}")
        except Exception as e:
            print(f"빈 템플릿 폴더 생성 실패: {e}")
    
    print("추가 리소스 복사 완료")

def main():
    """메인 빌드 프로세스"""
    print("마크다운-HWP 변환기 EXE 빌드를 시작합니다...")
    
    try:
        # 환경 설정
        setup_env()
        
        # Qt 충돌 확인
        if not check_qt_conflicts():
            return False
        
        # 이전 빌드 정리
        clean_build_dirs()
        
        # EXE 빌드
        build_exe()
        
        # 추가 리소스 복사
        copy_additional_resources()
        
        print("빌드 프로세스 완료!")
        print("빌드된 EXE 파일 위치: ./dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe")
        return True
    except Exception as e:
        print(f"빌드 과정에서 오류가 발생했습니다: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 