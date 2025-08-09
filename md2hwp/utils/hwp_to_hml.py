import os
from pyhwpx import Hwp
import re
import datetime
from PySide6.QtWidgets import QApplication, QFileDialog

# 파일 탐색기로 hwp 파일 경로 선택
def get_hwp_file_path():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    file_path, _ = QFileDialog.getOpenFileName(None, "HWP 파일 선택", "", "HWP files (*.hwp)")
    return file_path

# 파일 탐색기로 hml 파일 경로 선택
def get_hml_file_path():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    file_path, _ = QFileDialog.getOpenFileName(None, "HML 파일 선택", "", "HML files (*.hml)")
    return file_path

# HWP 파일을 열고 HML로 저장하는 함수
def convert_hwp_to_hml(file_path):
    """
    HWP/HWPX/HWT 파일을 HML(HWPML2X)로 저장합니다.
    - .hwp   → open(file)
    - .hwpx  → open(file, "HWPX")
    - .hwt   → open(file, "HWT")
    저장은 공통으로 save_as(hml_path, "HWPML2X").

    이미 .hml 인 경우는 그대로 경로를 반환합니다.
    실패 시 None 반환.
    """
    src_path = file_path
    if not src_path:
        print("파일 선택이 취소되었습니다.")
        return None

    ext = os.path.splitext(src_path)[1].lower()
    if ext == ".hml":
        # 이미 HML이면 그대로 사용
        return src_path

    # 출력 경로 (기본값)
    hml_path = os.path.splitext(src_path)[0] + ".hml"

    def make_safe_output_path(preferred_path: str) -> str:
        """파일명에 문제가 있을 때 ASCII-safe한 대체 경로를 생성합니다."""
        out_dir = os.path.dirname(preferred_path)
        base = os.path.splitext(os.path.basename(preferred_path))[0]
        # 비 ASCII/특수문자 제거(숫자/영문/._-만 허용)
        safe_base = re.sub(r"[^0-9A-Za-z._-]+", "_", base)
        if not safe_base:
            safe_base = "converted"
        candidate = os.path.join(out_dir, safe_base + ".hml")
        if not os.path.exists(candidate):
            return candidate
        # 중복 시 타임스탬프 부여
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(out_dir, f"{safe_base}_{ts}.hml")

    def make_temp_output_path() -> str:
        temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "md2hwp")
        os.makedirs(temp_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(temp_dir, f"converted_{ts}.hml")

    # 확장자별 open 포맷 매핑
    open_format = None
    if ext == ".hwp":
        open_format = None            # 기본
    elif ext == ".hwpx":
        open_format = "HWPX"         # HWPX 문서 포맷
    elif ext == ".hwt":
        open_format = "HWT"          # 템플릿 포맷
    else:
        print(f"지원하지 않는 파일 형식입니다: {ext}")
        return None

    hwp = None
    try:
        hwp = Hwp(visible=False)
        # 파일 열기 (필요 시 포맷 지정)
        try:
            if open_format:
                hwp.open(src_path, open_format)
            else:
                hwp.open(src_path)
        except Exception as open_err:
            print(f"열기 실패(포맷={open_format}): {open_err}. 기본 모드로 재시도합니다.")
            # 포맷 미지정으로 재시도
            hwp.open(src_path)

        # HML(HWPML2X)로 저장
        saved = hwp.save_as(hml_path, "HWPML2X")
        if not saved:
            print(f"HML 저장 실패(원경로): {hml_path}. 안전한 파일명으로 재시도합니다.")
            safe_path = make_safe_output_path(hml_path)
            saved = hwp.save_as(safe_path, "HWPML2X")
            if not saved:
                print(f"HML 저장 실패(안전경로): {safe_path}. 임시 폴더로 재시도합니다.")
                temp_path = make_temp_output_path()
                saved = hwp.save_as(temp_path, "HWPML2X")
                if not saved:
                    print("HML 형식 저장에 최종 실패했습니다.")
                    return None
                print(f"임시 폴더에 저장되었습니다: {temp_path}")
                return temp_path
            print(f"성공적으로 HML로 저장되었습니다(안전경로): {safe_path}")
            return safe_path

        print(f"성공적으로 HML로 저장되었습니다: {hml_path}")
        return hml_path

    except Exception as e:
        print(f"변환 중 오류 발생: {e}")
        return None
    finally:
        try:
            if hwp:
                hwp.quit()
        except Exception:
            pass

# HML 파일을 열고 HWP로 저장하는 함수
def convert_hml_to_hwp(file_path):
    hml_path = file_path
    if not hml_path:
        print("파일 선택이 취소되었습니다.")
        return

    # 저장할 hwp 경로 생성
    hwp_path = os.path.splitext(hml_path)[0] + ".hwp"

    # 한글 객체 생성
    hwp = Hwp()
    
    # HML 파일 열기
    hwp.open(hml_path, "HWPML2X")
    
    # HWP 형식으로 저장
    saved = hwp.save_as(hwp_path, "HWP")
    
    if saved:
        print(f"성공적으로 저장되었습니다: {hwp_path}")
    else:
        print("저장에 실패했습니다.")

    hwp.quit()

# 실행
if __name__ == "__main__":
    # 사용자에게 변환 방향 선택하도록 함
    print("1: HWP -> HML 변환")
    print("2: HML -> HWP 변환")
    choice = input("변환 방향을 선택하세요 (1 또는 2): ")
    file_path = get_hwp_file_path()
    if choice == "1":
        convert_hwp_to_hml(file_path)
    elif choice == "2":
        convert_hml_to_hwp(file_path)
    else:
        print("잘못된 선택입니다.")
