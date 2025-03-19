# md_to_hwp/main.py
"""
마크다운 변환기 실행 스크립트
"""
import sys
from PySide6.QtWidgets import QApplication
from md_to_hwp.gui import ConverterGUI

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    window = ConverterGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
