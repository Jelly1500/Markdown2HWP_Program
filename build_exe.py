#!/usr/bin/env python
"""
마크다운-HWP 변환기 EXE 빌드 스크립트
"""
import os
import sys
import shutil
import subprocess
import time

def setup_env():
    """빌드에 필요한 패키지 설치"""
    print("빌드 환경 설정 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("PyInstaller 설치 완료")

def clean_build_dirs():
    """빌드 전 이전 빌드 파일 정리"""
    print("이전 빌드 파일 정리 중...")
    
    # 파일 사용 중일 때 재시도 함수
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
        # 파일 사용 중일 수 있으므로 잠시 대기
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
    
    print("이전 빌드 파일 정리 완료 (일부 파일은 남아있을 수 있음)")

def build_exe():
    """PyInstaller를 사용하여 EXE 빌드"""
    print("EXE 파일 빌드 중...")
    
    # 아이콘 파일 유무 확인
    icon_option = []
    if os.path.exists("icon.png") or os.path.exists("icon.ico"):
        # .ico 파일이 있으면 사용, 없으면 .png 사용
        icon_file = "icon.ico" if os.path.exists("icon.ico") else "icon.png"
        icon_option = ["--icon", icon_file]
    
    # 기존 dist 디렉토리가 남아있으면 다른 이름으로 백업
    if os.path.exists("dist"):
        backup_name = f"dist_backup_{int(time.time())}"
        print(f"기존 dist 디렉토리를 {backup_name}으로 백업합니다.")
        try:
            os.rename("dist", backup_name)
        except (PermissionError, OSError) as e:
            print(f"주의: dist 디렉토리 백업 중 오류 발생: {e}")
    
    # PyInstaller 명령행 옵션
    cmd = [
        "pyinstaller",
        "--name=마크다운_HWP_변환기",
        "--windowed",  # GUI 애플리케이션 (콘솔 창 없음)
        "--noconfirm", # 기존 빌드 파일 덮어쓰기
        "--clean",     # 임시 파일 정리
        "--add-data=md2hwp/new_template;md2hwp/new_template",  # 템플릿 파일 포함 (경로 수정)
        "--hidden-import=zstandard",  # zstandard 패키지 명시적 포함
    ]
    
    # 아이콘 옵션 추가
    cmd.extend(icon_option)
    
    # onefile 옵션 (단일 exe 파일로 빌드)
    cmd.append("--onedir")  # 폴더 형태로 빌드 (실행 속도 향상)
    
    # 메인 스크립트 추가
    cmd.append("run.py")
    
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
    
    if os.path.exists(src_template) and not os.path.exists(dst_template):
        try:
            print(f"템플릿 폴더 복사: {src_template} → {dst_template}")
            shutil.copytree(src_template, dst_template)
            print("템플릿 폴더 복사 완료")
        except (PermissionError, OSError) as e:
            print(f"주의: 템플릿 폴더 복사 중 오류 발생: {e}")
    
    print("추가 리소스 복사 완료")

def main():
    """메인 빌드 프로세스"""
    print("마크다운-HWP 변환기 EXE 빌드를 시작합니다...")
    
    try:
        # 환경 설정
        setup_env()
        
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