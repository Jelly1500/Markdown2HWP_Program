"""
마크다운-HWP 변환기 애플리케이션 진입점
"""
import sys
from PySide6.QtWidgets import QApplication

from md2hwp.converter.markdown_parser import MarkdownParser
from md2hwp.converter.template_manager import TemplateManager
from md2hwp.converter.special_char import SpecialCharHandler
from md2hwp.converter.hwpml_generator import HWPMLGenerator
from md2hwp.converter.id_manager import IDManager
from md2hwp.gui.main_window import MainWindow
from md2hwp.config import APP_NAME

class MD2HWPConverter:
    """마크다운-HWP 변환 메인 클래스"""
    
    def __init__(self):
        # ID 관리자 생성
        self.id_manager = IDManager()
        
        # 구성 요소 초기화
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
        # 특수 문자 카운터 초기화
        self.special_char_handler.reset_counters()
        
        # 메타데이터 추출 (제목 등이 이미 전달되지 않은 경우)
        if title == "제목 없음":
            metadata = self.markdown_parser.extract_metadata(md_text)
            title = metadata.get('title', title)
            author = metadata.get('author', author)
            date = metadata.get('date', date)
            
            # 메타데이터 섹션 제거
            md_text = self.markdown_parser.remove_metadata_section(md_text)
        
        # 마크다운 파싱
        md_elements = self.markdown_parser.parse(md_text)
        
        # HWPML 생성
        return self.hwpml_generator.generate_hwpml(
            md_elements, 
            self.template_manager.template_content,
            title, author, date
        )

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