"""
파일 관련 유틸리티 함수 모듈
"""
import os
import datetime
import io

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