import os
from pyhwpx import Hwp
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
    hwp_path = file_path
    if not hwp_path:
        print("파일 선택이 취소되었습니다.")
        return

    # 저장할 hml 경로 생성
    hml_path = os.path.splitext(hwp_path)[0] + ".hml"

    # 한글 객체 생성
    hwp = Hwp(visible=False)
    
    # HWP 파일 열기 (open 메서드는 확장자를 신경쓰지 않아도 됩니다)
    hwp.open(hwp_path)

    # HML 형식으로 저장
    # format: "HWPML2X", arg: "" (또는 필요한 옵션)
    saved = hwp.save_as(hml_path, "HWPML2X")
    
    if saved:
        print(f"성공적으로 저장되었습니다: {hml_path}")
    else:
        print("저장에 실패했습니다.")

    hwp.quit()
    return hml_path

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
