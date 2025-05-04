"""
마크다운-HWP 변환기 애플리케이션 진입점
"""
# md2hwp/main.py
import sys
import os
import datetime
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(BASE_DIR)) 
    if BASE_DIR not in sys.path:
         sys.path.insert(0, BASE_DIR)

try:
    from md2hwp.converter.markdown_parser import MarkdownParser
    from md2hwp.converter.template_manager import TemplateManager
    from md2hwp.converter.special_char import SpecialCharHandler
    from md2hwp.converter.hwpml_generator import HWPMLGenerator
    from md2hwp.converter.id_manager import IDManager
    from md2hwp.gui.main_window import MainWindow 
    from md2hwp.gui.license_dialog import LicenseDialog
    from md2hwp.utils.license_utils import (load_license_info, save_license_info,
                                          validate_license_on_server, delete_license_info)
    from md2hwp.config import APP_NAME, LICENSE_CHECK_INTERVAL_DAYS
except ImportError as e:
    print(f"Import Error in main.py: {e}")
    app_temp = QApplication.instance() 
    if app_temp:
        QMessageBox.critical(None, "오류", f"프로그램 실행에 필요한 파일을 찾을 수 없습니다.\n오류: {e}\n프로그램을 종료합니다.")
    else:
        print(f"프로그램 실행에 필요한 파일을 찾을 수 없습니다. 오류: {e}")
    sys.exit(1)
# -------------------------------------------------------------
class MD2HWPConverter:
    """마크다운-HWP 변환 메인 클래스"""
    
    def __init__(self):
        self.id_manager = IDManager()
        
        self.template_manager = TemplateManager()
        self.special_char_handler = SpecialCharHandler()
        self.markdown_parser = MarkdownParser()
        self.hwpml_generator = HWPMLGenerator(
            self.template_manager, 
            self.special_char_handler,
            self.id_manager
        )
    
    def load_template(self, template_path):
        """템플릿 로드"""
        return self.template_manager.load_template(template_path)
    
    def convert_md_to_hwpml(self, md_text, title="제목 없음", author="작성자 없음", date="날짜 없음"):
        """마크다운 텍스트를 HWPML로 변환"""
        self.special_char_handler.reset_counters()
        
        if title == "제목 없음":
            metadata = self.markdown_parser.extract_metadata(md_text)
            title = metadata.get('title', title)
            author = metadata.get('author', author)
            date = metadata.get('date', date)
            
            md_text = self.markdown_parser.remove_metadata_section(md_text)
        
        md_elements = self.markdown_parser.parse(md_text)
        
        return self.hwpml_generator.generate_hwpml(
            md_elements, 
            self.template_manager.template_content,
            title, author, date
        )

# --- 라이선스 확인 함수 (run.py에서 호출됨) ---
def perform_license_check():
    """
    라이선스 확인 로직을 수행합니다.
    QApplication 인스턴스가 이미 생성되어 있어야 합니다.
    라이선스가 유효하지 않으면 메시지를 표시하고 프로그램을 종료합니다.
    """
    app = QApplication.instance() 
    if not app:
        print("오류: QApplication 인스턴스가 없습니다! 라이선스 확인 불가.")
        sys.exit(1)

    stored_info = load_license_info()
    current_time = datetime.datetime.now()
    needs_validation = True
    license_key_to_use = None
    is_first_run = False

    if stored_info and isinstance(stored_info, dict) and "key" in stored_info and "last_checked" in stored_info:
        license_key_to_use = stored_info["key"]
        try:
            last_checked_str = stored_info["last_checked"]
            last_checked_time = datetime.datetime.fromisoformat(last_checked_str)
            time_diff = current_time - last_checked_time
            if 0 <= time_diff.days < LICENSE_CHECK_INTERVAL_DAYS:
                print(f"라이선스 유효 기간({LICENSE_CHECK_INTERVAL_DAYS}일) 내입니다. 서버 검증 생략.")
                needs_validation = False
            else:
                print(f"라이선스 검증 주기({LICENSE_CHECK_INTERVAL_DAYS}일)가 지났습니다. 서버 검증 필요.")
                needs_validation = True
        except (ValueError, TypeError) as e:
            print(f"저장된 날짜 형식 오류 또는 타입 오류 ({e}). 재검증 필요.")
            needs_validation = True
            delete_license_info()
            license_key_to_use = None
            is_first_run = True
    else:
        print("저장된 라이선스 정보 없음. 첫 실행으로 간주.")
        is_first_run = True
        needs_validation = True

    if is_first_run:
        print("라이선스 키 입력 요청...")
        license_dialog = LicenseDialog() 
        result = license_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            entered_key = license_dialog.get_key()
            if not entered_key:
                QMessageBox.critical(None, "오류", "라이선스 키를 입력해야 합니다.")
                sys.exit(0) 
            license_key_to_use = entered_key
            needs_validation = True
        else:
            print("라이선스 키 입력 취소됨.")
            sys.exit(0) 
    if needs_validation:
        if not license_key_to_use:
            QMessageBox.critical(None, "오류", "검증할 라이선스 키가 없습니다.")
            sys.exit(0) 

        print("-" * 30)
        print(f"DEBUG [Client]: 서버로 전송할 라이선스 키: '{license_key_to_use}'") # 따옴표로 감싸서 공백 확인 용이하게
        print("-" * 30)
    
        print(f"라이선스 키 '{license_key_to_use[:4]}...' 서버 검증 시도...")
        validation_result = validate_license_on_server(license_key_to_use)

        if "status" not in validation_result:
            QMessageBox.critical(None, "오류", "라이선스 서버로부터 예상치 못한 응답을 받았습니다.")
            print(f"Unexpected server response: {validation_result}")
            delete_license_info()
            sys.exit(1)

        if validation_result["status"] == "valid":
            print(f"라이선스 검증 성공: {validation_result.get('message', '')}")
            save_license_info({"key": license_key_to_use, "last_checked": current_time.isoformat()})
        else:
            error_msg = validation_result.get("message", "알 수 없는 라이선스 오류")
            QMessageBox.critical(None, "라이선스 오류", f"라이선스 검증 실패: {error_msg}")
            delete_license_info()
            sys.exit(0) 
    else:
        pass 

def main():
    """애플리케이션 시작 함수"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    converter = MD2HWPConverter()
    window = MainWindow(converter)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 