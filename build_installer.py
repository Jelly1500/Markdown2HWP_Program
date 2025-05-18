#!/usr/bin/env python
"""
마크다운-HWP 변환기 EXE 빌드 및 인스톨러 패키징 스크립트
"""
import os
import sys
import subprocess
import platform
import time
import shutil

def check_inno_setup():
    """Inno Setup이 설치되어 있는지 확인"""
    print("Inno Setup 확인 중...")
    
    # Windows 운영체제인지 확인
    if platform.system() != "Windows":
        print("오류: 이 스크립트는 Windows에서만 실행 가능합니다.")
        sys.exit(1)
    
    # Inno Setup 기본 설치 경로 확인
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in inno_paths:
        if os.path.exists(path):
            print(f"Inno Setup 설치 확인됨: {path}")
            return path
    
    print("경고: Inno Setup을 찾을 수 없습니다.")
    print("인스톨러를 생성하려면 Inno Setup을 설치하세요: https://jrsoftware.org/isdl.php")
    return None

def build_exe():
    """PyInstaller를 사용하여 EXE 빌드"""
    print("\n===== EXE 빌드 시작 =====")
    
    try:
        # build_exe.py 실행
        if os.path.exists("build_exe.py"):
            print("빌드 스크립트 실행 중...")
            try:
                subprocess.check_call([sys.executable, "build_exe.py"])
                return True
            except subprocess.CalledProcessError as e:
                print(f"빌드 스크립트 실행 중 오류: {e}")
                
                # 결과물이 있는지 확인
                if os.path.exists("dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe"):
                    print("오류가 발생했지만 EXE 파일이 이미 존재합니다. 계속 진행합니다.")
                    return True
                return False
        else:
            # PyInstaller 설치
            print("PyInstaller 설치 중...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            
            # spec 파일을 사용하여 빌드
            print("spec 파일로 빌드 중...")
            if os.path.exists("마크다운_HWP_변환기.spec"):
                try:
                    subprocess.check_call([
                        "pyinstaller", "마크다운_HWP_변환기.spec", "--clean"
                    ])
                    return True
                except subprocess.CalledProcessError:
                    # 기본 명령어로 빌드 재시도
                    print("spec 파일 빌드 실패, 기본 명령어로 재시도합니다...")
            
            # 기본 명령어로 빌드
            print("기본 PyInstaller 명령어로 빌드 중...")
            cmd = [
                "pyinstaller",
                "--name=마크다운_HWP_변환기",
                "--windowed",
                "--onedir",
                "--clean",
                "--add-data=md2hwp/new_template;md2hwp/new_template",
                "--hidden-import=zstandard",
                "run.py"
            ]
            
            try:
                subprocess.check_call(cmd)
                return True
            except subprocess.CalledProcessError:
                # 결과물이 있는지 마지막으로 확인
                if os.path.exists("dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe"):
                    print("오류가 발생했지만 EXE 파일이 이미 존재합니다. 계속 진행합니다.")
                    return True
                return False
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        # 결과물이 있는지 확인
        if os.path.exists("dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe"):
            print("오류가 발생했지만 EXE 파일이 이미 존재합니다. 계속 진행합니다.")
            return True
        return False

def ensure_output_dirs():
    """출력 디렉토리가 존재하는지 확인하고 생성"""
    print("출력 디렉토리 확인 중...")
    
    # dist 디렉토리 확인
    dist_dir = os.path.join("dist", "마크다운_HWP_변환기")
    if not os.path.exists(dist_dir):
        print(f"출력 디렉토리 생성: {dist_dir}")
        try:
            os.makedirs(dist_dir, exist_ok=True)
        except Exception as e:
            print(f"출력 디렉토리 생성 중 오류: {e}")
            return False
    
    # convertedDocs 폴더 생성
    docs_dir = os.path.join(dist_dir, "convertedDocs")
    if not os.path.exists(docs_dir):
        print(f"convertedDocs 폴더 생성: {docs_dir}")
        try:
            os.makedirs(docs_dir, exist_ok=True)
        except Exception as e:
            print(f"convertedDocs 폴더 생성 중 오류: {e}")
    
    # new_template 폴더 복사 (전체 템플릿 파일 포함)
    template_src = os.path.join("md2hwp", "new_template")
    template_dest = os.path.join(dist_dir, "new_template")
    
    if os.path.exists(template_src) and not os.path.exists(template_dest):
        print(f"new_template 폴더 복사: {template_src} -> {template_dest}")
        try:
            shutil.copytree(template_src, template_dest)
        except Exception as e:
            print(f"템플릿 폴더 복사 중 오류: {e}")
            # 실패해도 계속 진행
    
    return True

def build_installer(inno_path):
    """Inno Setup을 사용하여 인스톨러 생성"""
    print("\n===== 인스톨러 빌드 시작 =====")
    
    if not inno_path:
        print("Inno Setup 경로가 제공되지 않아 인스톨러를 생성할 수 없습니다.")
        return False
    
    # 출력 디렉토리 확인
    if not ensure_output_dirs():
        print("출력 디렉토리 준비 실패, 인스톨러 생성을 건너뜁니다.")
        return False
    
    try:
        # Inno Setup 스크립트 실행
        if os.path.exists("installer.iss"):
            print("인스톨러 스크립트 빌드 중...")
            subprocess.check_call([inno_path, "installer.iss"])
            print("인스톨러 빌드 완료!")
            return True
        else:
            print("오류: installer.iss 파일을 찾을 수 없습니다.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"오류: 인스톨러 빌드 실패 - {e}")
        return False
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return False

def main():
    """메인 빌드 프로세스"""
    print("마크다운-HWP 변환기 통합 빌드 프로세스 시작...\n")
    
    # Inno Setup 확인
    inno_path = check_inno_setup()
    
    # 프로세스 실행 전 대기 (이전 프로세스가 종료될 시간 제공)
    print("빌드 준비 중... (3초 대기)")
    time.sleep(3)
    
    # EXE 빌드
    exe_success = build_exe()
    if not exe_success:
        print("EXE 빌드 실패로 인스톨러 생성을 건너뜁니다.")
        sys.exit(1)
        
    # 인스톨러 빌드
    if inno_path:
        installer_success = build_installer(inno_path)
        if installer_success:
            print("\n=== 빌드 결과 ===")
            print("EXE 위치: ./dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe")
            print("인스톨러 위치: ./Output/마크다운_HWP_변환기_설치프로그램.exe")
            print("\n빌드 프로세스가 성공적으로 완료되었습니다!")
        else:
            print("\n경고: EXE 빌드는 성공했으나 인스톨러 생성에 실패했습니다.")
            print("EXE 위치: ./dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe")
    else:
        print("\n경고: Inno Setup이 설치되지 않아 인스톨러를 생성할 수 없습니다.")
        print("EXE 위치: ./dist/마크다운_HWP_변환기/마크다운_HWP_변환기.exe")
        print("인스톨러 생성을 위해 Inno Setup을 설치하세요: https://jrsoftware.org/isdl.php")

if __name__ == "__main__":
    main() 