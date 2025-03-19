# md_to_hwp/template_manager.py
"""
마크다운 문법에 대한 스타일 템플릿을 관리하는 모듈
"""
import os
import json
from PySide6.QtGui import QColor

class MarkdownTemplate:
    """마크다운 요소의 스타일 템플릿을 관리하는 클래스"""
    
    def __init__(self):
        """생성자"""
        self.templates = {}
        self.current_template = "default"
        self.load_default_template()
    
    def load_default_template(self):
        """기본 템플릿 설정 로드"""
        self.templates = {
            "default": {
                "heading1": {
                    "prefix": "# ",
                    "font": "맑은 고딕",
                    "size": 20,          # pt 단위
                    "color": "#000000",  # RGB 색상값
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "paraShape": "0",
                    "template_type": "normal",
                    "charShape": "1"     # 내부적으로 사용되는 ID
                },
                "heading2": {
                    "prefix": "## ",
                    "font": "맑은 고딕", 
                    "size": 16,
                    "color": "#000000",
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "paraShape": "0",
                    "template_type": "normal",
                    "charShape": "2"
                },
                "heading3": {
                    "prefix": "### ",
                    "font": "맑은 고딕", 
                    "size": 14,
                    "color": "#000000",
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "paraShape": "0",
                    "template_type": "normal",
                    "charShape": "3"
                },
                "heading4": {
                    "prefix": "#### ",
                    "font": "맑은 고딕", 
                    "size": 12,
                    "color": "#000000",
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "paraShape": "0",
                    "template_type": "normal",
                    "charShape": "4"
                },
                "bullet_list": {
                    "symbol": "• ", 
                    "font": "맑은 고딕",
                    "size": 10,
                    "color": "#000000",
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "paraShape": "1",
                    "charShape": "0"
                },
                "ordered_list": {
                    "format": "%d. ", 
                    "font": "맑은 고딕",
                    "size": 10,
                    "color": "#000000",
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "paraShape": "1",
                    "charShape": "0"
                },
                "paragraph": {
                    "font": "맑은 고딕",
                    "size": 10,
                    "color": "#000000",
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "paraShape": "0",
                    "charShape": "0"
                },
                "bold": {
                    "prefix": "**", 
                    "suffix": "**", 
                    "font": "맑은 고딕",
                    "size": 10,
                    "color": "#000000",
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "charShape": "6"
                },
                "italic": {
                    "prefix": "_", 
                    "suffix": "_", 
                    "font": "맑은 고딕",
                    "size": 10,
                    "color": "#000000",
                    "bold": False,
                    "italic": True,
                    "underline": False,
                    "charShape": "7"
                },
                "link": {
                    "prefix": "[", 
                    "middle": "](", 
                    "suffix": ")", 
                    "font": "맑은 고딕",
                    "size": 10,
                    "color": "#0000FF",
                    "bold": False,
                    "italic": False,
                    "underline": True,
                    "charShape": "8"
                },
                "table": {
                    "header_border": "3", 
                    "middle_border": "6", 
                    "last_border": "4"
                }
            }
        }
    
    def save_template(self, name, template_data):
        """새 템플릿 저장"""
        self.templates[name] = template_data
        self.save_to_file()
    
    def load_template(self, name):
        """이름으로 템플릿 로드"""
        if name in self.templates:
            self.current_template = name
            return self.templates[name]
        return None
    
    def get_current_template(self):
        """현재 선택된 템플릿 반환"""
        return self.templates.get(self.current_template, self.templates["default"])
    
    def save_to_file(self, file_path="templates.json"):
        """파일로 템플릿 저장"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"templates": self.templates}, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path="templates.json"):
        """파일에서 템플릿 로드"""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get("templates", {})
                if "default" not in self.templates:
                    self.load_default_template()
    
    def apply_template_to_element(self, element_type, content, **kwargs):
        """특정 마크다운 요소에 템플릿 적용"""
        current_tmpl = self.get_current_template()
        element_tmpl = current_tmpl.get(element_type, {})
        
        # 템플릿 타입에 따라 다른 처리
        template_type = element_tmpl.get("template_type", "normal")
        
        if template_type == "normal":
            # 일반 서식 적용 (기본)
            char_shape = element_tmpl.get("charShape", "0")
            para_shape = element_tmpl.get("paraShape", "0")
            return f'<P ParaShape="{para_shape}" Style="0"><TEXT CharShape="{char_shape}"><CHAR>{content}</CHAR></TEXT></P>\n'
        
        elif template_type == "table":
            # 테이블 서식 적용 (복잡한 형태)
            from md_to_hwp.hwpml_templates import H2_TABLE_TEMPLATE
            replacements = {'content': content}
            replacements.update(kwargs)
            
            result = H2_TABLE_TEMPLATE
            for key, value in replacements.items():
                placeholder = '{' + key + '}'
                result = result.replace(placeholder, value)
            
            return result
        
        # 기본 서식 반환
        return f'<P ParaShape="0" Style="0"><TEXT CharShape="0"><CHAR>{content}</CHAR></TEXT></P>\n'
    
    def rgb_to_hwp_color(self, color_hex):
        """RGB 컬러 코드를 한글 색상값으로 변환"""
        color_hex = color_hex.lstrip('#')
        if len(color_hex) != 6:
            return 0  # 기본 검정색
        
        # RGB 순서가 아닌 BGR 순서로 변환해야 함
        r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
        return (b << 16) | (g << 8) | r
