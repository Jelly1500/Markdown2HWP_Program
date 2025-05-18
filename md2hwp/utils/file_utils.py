"""
파일 관련 유틸리티 함수 모듈
"""
import os
import datetime
import io
import sys

import platform  # 추가
import subprocess # 추가
import time      # 추가
try:             # Windows 특정 기능이므로 try-except 추가
    import win32gui
except ImportError:
    win32gui = None # 다른 OS에서는 None으로 설정

try:
    from PySide6.QtCore import QTimer
except ImportError:
    QTimer = None # PySide6가 없는 환경 대비

explorer_handles = {
    'output': None,  # 한글 문서 경로용
    'template': None  # 템플릿 경로용
}

def ensure_directory(directory_path):
    """디렉토리가 존재하지 않으면 생성"""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        return directory_path
    except PermissionError:
        # 권한 오류 발생 시 사용자 문서 폴더 하위에 대체 경로 생성
        user_docs = get_user_documents_path()
        app_name = os.path.basename(directory_path)
        alt_path = os.path.join(user_docs, "마크다운_HWP_변환기", app_name)
        try:
            if not os.path.exists(alt_path):
                os.makedirs(alt_path, exist_ok=True)
            print(f"권한 문제로 인해 대체 경로를 사용합니다: {alt_path}")
            return alt_path
        except Exception as e:
            # 임시 폴더로 대체 (최후의 수단)
            temp_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "마크다운_HWP_변환기", app_name)
            os.makedirs(temp_path, exist_ok=True)
            print(f"임시 폴더로 대체합니다: {temp_path}")
            return temp_path
    except Exception as e:
        print(f"디렉토리 생성 오류: {e}")
        # 임시 폴더로 대체
        temp_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "마크다운_HWP_변환기")
        os.makedirs(temp_path, exist_ok=True)
        return temp_path

def get_user_documents_path():
    """사용자 문서 폴더 경로 반환"""
    if platform.system() == "Windows":
        import ctypes.wintypes
        CSIDL_PERSONAL = 5  # 내 문서
        SHGFP_TYPE_CURRENT = 0  # 현재 경로
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    else:
        # macOS, Linux 등에서는 사용자 홈 디렉토리 사용
        return os.path.join(os.path.expanduser("~"), "Documents")

def generate_output_filename(output_dir, prefix="converted", extension=".hml"):
    """타임스탬프가 포함된 출력 파일명 생성"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(output_dir, f"{prefix}_{timestamp}{extension}")

def save_text_file(file_path, content, encoding="utf-8"):
    """텍스트 파일 저장"""
    try:
        with io.open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return file_path
    except PermissionError:
        # 권한 문제가 발생한 경우 사용자 문서 폴더에 저장 시도
        user_docs = get_user_documents_path()
        alt_path = os.path.join(user_docs, "마크다운_HWP_변환기", os.path.basename(file_path))
        os.makedirs(os.path.dirname(alt_path), exist_ok=True)
        with io.open(alt_path, "w", encoding=encoding) as f:
            f.write(content)
        print(f"원본 경로에 저장할 수 없어 대체 경로에 저장했습니다: {alt_path}")
        return alt_path
    except Exception as e:
        print(f"파일 저장 오류: {e}")
        # 임시 폴더에 저장 시도
        temp_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "마크다운_HWP_변환기", os.path.basename(file_path))
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with io.open(temp_path, "w", encoding=encoding) as f:
            f.write(content)
        print(f"임시 폴더에 저장했습니다: {temp_path}")
        return temp_path

def open_file(file_path):
    """파일 열기 시도"""
    try:
        # os.startfile은 Windows 전용이므로 플랫폼별 분기 처리
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin": # macOS
            subprocess.Popen(["open", file_path])
        else: # Linux 등
            subprocess.Popen(["xdg-open", file_path])
        return True
    except Exception as e:
        print(f"파일 열기 오류: {str(e)}")
        return False

# --- 추가된 함수들 ---
def get_explorer_windows():
    """
    현재 열려 있는 Explorer 창(CabinetWClass)의 윈도우 핸들들을 집합으로 반환합니다. (Windows 전용)
    """
    if not win32gui: # win32gui가 임포트되지 않았으면 빈 집합 반환
        return set()

    handles = set()


    def enum_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            if win32gui.GetClassName(hwnd) == "CabinetWClass":
                handles.add(hwnd)

                # print(f"발견된 Explorer 창 핸들: {hwnd}") # 디버깅용 출력은 주석 처리
        return True


    win32gui.EnumWindows(enum_callback, None)
    return handles

def open_file_explorer(file_path, handle_type='output'):
    """
    파일의 절대 경로를 기준으로 파일 탐색기를 실행합니다.
    Windows의 경우, 이미 Explorer 창(새로 열린 창)이 있으면 새 창을 열지 않습니다.


    Args:
        file_path (str): 파일의 경로 (절대 경로 권장)
        handle_type (str): 핸들러 타입 ('output' 또는 'template')

    Raises:
        FileNotFoundError: file_path가 존재하지 않을 경우
        OSError: 지원하지 않는 운영체제일 경우
        ImportError: Windows가 아닌 환경에서 Windows 관련 기능을 사용하려 할 때

    """
    global explorer_handles

    file_path = os.path.abspath(file_path)

    # 파일 대신 폴더를 열어야 하는 경우를 위해, 경로가 폴더인지 파일인지 확인
    if not os.path.exists(file_path):
         # 파일이 없다면 상위 폴더라도 존재하는지 확인
         dir_path = os.path.dirname(file_path)
         if os.path.isdir(dir_path):
             file_path = dir_path # 상위 폴더 경로 사용
         else:
             raise FileNotFoundError(f"파일 또는 상위 폴더를 찾을 수 없습니다: {file_path}")

    system = platform.system()

    if system == "Windows":
        if not win32gui:
             raise ImportError("Windows 환경이 아니거나 'pywin32' 라이브러리가 설치되지 않았습니다.")
        if not QTimer:
             print("경고: QTimer를 임포트할 수 없어 탐색기 핸들 캡처가 비활성화됩니다.")
             if os.path.isdir(file_path):
                 subprocess.Popen(["explorer", file_path])
             else:
                 subprocess.Popen(["explorer", "/select,", file_path])
             return

        if explorer_handles[handle_type] is not None and win32gui.IsWindow(explorer_handles[handle_type]):
            try:
                 win32gui.SetForegroundWindow(explorer_handles[handle_type])
            except Exception as e:
                 print(f"기존 창 활성화 실패: {e}") # 실패해도 계속 진행 (새로 열기 시도)
                 explorer_handles[handle_type] = None # 핸들 무효화
            else:
                 return 

        before_windows = get_explorer_windows()

        if os.path.isdir(file_path):
             subprocess.Popen(["explorer", file_path])
        else:
             subprocess.Popen(["explorer", "/select,", file_path])
        
        def _capture_handle():
            nonlocal handle_type, before_windows # 외부 변수 참조
            try:
                after_windows = get_explorer_windows()
                new_windows = after_windows - before_windows
                if new_windows:
                    explorer_handles[handle_type] = new_windows.pop()
                else:
                    explorer_handles[handle_type] = None
            except Exception as e:
                print(f"핸들 캡처 중 오류: {e}")
                explorer_handles[handle_type] = None

        QTimer.singleShot(1000, _capture_handle)
        

    elif system == "Darwin": # macOS
         if os.path.isdir(file_path):
             subprocess.Popen(["open", file_path])
         else:
             subprocess.Popen(["open", "-R", file_path]) # -R 옵션은 파일을 포함하는 폴더를 열고 파일을 선택
    elif system == "Linux":
        # 리눅스에서는 파일 경로든 폴더 경로든 상위 폴더를 열어주는 것이 일반적
        folder = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)

        subprocess.Popen(["xdg-open", folder])
    else:
        raise OSError(f"지원하지 않는 운영체제: {system}")