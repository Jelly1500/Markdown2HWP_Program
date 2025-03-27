"""
파일 관련 유틸리티 함수 모듈
"""
import os
import datetime
import io
import platform
import subprocess
import time
import win32gui

# 전역 변수로 explorer_handle 초기화 (용도별로 분리)
explorer_handles = {
    'output': None,  # 한글 문서 경로용
    'template': None  # 템플릿 경로용
}

def ensure_directory(directory_path):
    """디렉토리가 존재하지 않으면 생성"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

def generate_output_filename(output_dir, prefix="converted", extension=".hml"):
    """타임스탬프가 포함된 출력 파일명 생성"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(output_dir, f"{prefix}_{timestamp}{extension}")

def save_text_file(file_path, content, encoding="utf-8"):
    """텍스트 파일 저장"""
    with io.open(file_path, "w", encoding=encoding) as f:
        f.write(content)
    return file_path

def open_file(file_path):
    """파일 열기 시도"""
    try:
        os.startfile(file_path)
        return True
    except Exception as e:
        print(f"파일 열기 오류: {str(e)}")
        return False 
    
def get_explorer_windows():
    """
    현재 열려 있는 Explorer 창(CabinetWClass)의 윈도우 핸들들을 집합으로 반환합니다.
    """
    handles = set()
    
    def enum_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            if win32gui.GetClassName(hwnd) == "CabinetWClass":
                handles.add(hwnd)
                print(f"발견된 Explorer 창 핸들: {hwnd}")
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
    """
    global explorer_handles

    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    system = platform.system()
    
    if system == "Windows":
        # 이미 열린 Explorer 창이 있는지 확인 (저장해 둔 핸들이 유효하면)
        if explorer_handles[handle_type] is not None and win32gui.IsWindow(explorer_handles[handle_type]):
            # 이미 열린 Explorer 창이 있으므로 새 창을 열지 않음.
            return
        
        # 새 Explorer 창을 열기 전, 현재 열린 Explorer 창 목록 기록
        print(f"현재 열린 Explorer 창 목록 기록 ({handle_type})")
        before_windows = get_explorer_windows()
        
        # Explorer를 실행하여 해당 파일이 선택된 상태로 열기
        subprocess.Popen(["explorer", "/select,", file_path])
        
        # 새 창이 감지될 때까지 대기 (최대 10초)
        max_attempts = 20  # 10초 (0.5초 * 20)
        attempts = 0
        new_windows = set()
        
        while attempts < max_attempts:
            after_windows = get_explorer_windows()
            new_windows = after_windows - before_windows
            if new_windows:
                break
            time.sleep(0.5)
            attempts += 1
            
        print(f"새로 열린 Explorer 창 목록 ({handle_type}): {new_windows}")

        if new_windows:
            # 새로 열린 Explorer 창의 핸들을 저장
            explorer_handles[handle_type] = new_windows.pop()
        else:
            explorer_handles[handle_type] = None

        print(f"새로 열린 Explorer 창의 핸들 ({handle_type}): {explorer_handles[handle_type]}")

    elif system == "Darwin":
        subprocess.Popen(["open", "-R", file_path])
    elif system == "Linux":
        folder = os.path.dirname(file_path)
        subprocess.Popen(["xdg-open", folder])
    else:
        raise OSError(f"지원하지 않는 운영체제: {system}")