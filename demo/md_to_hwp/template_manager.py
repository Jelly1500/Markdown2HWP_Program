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
        self.load_templates()
    
    def load_templates(self):
        """저장된 템플릿을 로드"""
        self.load_from_file("templates.json")
        if "default" not in self.templates:
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
                    "charShape": "2"  # h2에는 charShape="2" 사용
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
                    "charShape": "3"  # h3에는 charShape="3" 사용
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
                    "charShape": "4"  # h4에는 charShape="4" 사용
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
                    "charShape": "0"  # 일반 텍스트에는 charShape="0" 사용
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
                    "charShape": "6"  # 굵게에는 charShape="6" 사용
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
                    "charShape": "7"  # 기울임에는 charShape="7" 사용
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
                    "charShape": "8"  # 링크에는 charShape="8" 사용
                },
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

    def delete_template(self, name):
        """템플릿 삭제"""
        if name in self.templates and name != "default":  # Prevent deletion of default template
            del self.templates[name]
            if self.current_template == name:
                self.current_template = "default"  # Revert to default if current template is deleted
            self.save_to_file()
            return True
        return False

    def generate_charshapelist(self, template_data):
        """템플릿 설정에 따라 CHARSHAPELIST를 동적으로 생성"""
        # 각 요소와 charShape ID 매핑 정의
        element_id_map = {
            "paragraph": "0",  # 일반 텍스트: charShape="0"
            "heading1": "1",   # H1 태그: charShape="1"
            "heading2": "2",   # H2 태그: charShape="2"
            "heading3": "3",   # H3 태그: charShape="3"
            "heading4": "4",   # H4 태그: charShape="4"
            "link": "8"        # 링크: charShape="8"
        }
    
        # charShapeList 생성
        charshape_entries = []
        
        # 각 요소 처리 (0~9번까지 항상 모든 ID 생성)
        for id_num in range(18):  # 샘플 파일에서는 18개의 CharShape이 있음
            id_str = str(id_num)
            
            # 해당 ID에 매핑된 요소 찾기
            element_type = None
            for el_type, char_id in element_id_map.items():
                if char_id == id_str and el_type in template_data:
                    element_type = el_type
                    break
                
            # 매핑된 요소가 있으면 해당 설정 사용, 없으면 기본값 사용
            if element_type and element_type in template_data:
                settings = template_data[element_type]
                # pt 단위를 hwp 단위로 변환 (1pt = 100 hwp 단위)
                size = int(settings.get("size", 10) * 100)
                
                # 색상 처리
                color_hex = settings.get("color", "#000000")
                text_color = self.rgb_to_hwp_color(color_hex)
                
                # 글꼴 처리 - 이름으로 ID 찾기
                font_name = settings.get("font", "맑은 고딕")
                # 만약 해당 글꼴이 매핑에 없으면 기본값 사용
                font_id = self.font_id_map.get(font_name, "0")
                
                # 스타일 처리
                bold_tag = "<BOLD />" if settings.get("bold", False) else ""
                italic_tag = "<ITALIC />" if settings.get("italic", False) else ""
                underline_tag = f'<UNDERLINE Color="0" Shape="Solid" Type="Bottom" />' if settings.get("underline", False) else ""
            else:
                # 기본값 설정
                size = 1000
                text_color = 0
                font_id = "0"  # 기본 글꼴 ID
                bold_tag = "<BOLD />" if id_num in [1, 2, 3, 4] else ""
                italic_tag = ""
                underline_tag = f'<UNDERLINE Color="0" Shape="Solid" Type="Bottom" />' if id_num == 8 else ""
            
            # charShape 항목 생성 - 모든 FONTID 속성에 동일한 font_id 사용
            charshape = f'''<CHARSHAPE BorderFillId="2" Height="{size}" Id="{id_str}" ShadeColor="4294967295" SymMark="0" TextColor="{text_color}" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="{font_id}" Hanja="{font_id}" Japanese="{font_id}" Latin="{font_id}" Other="{font_id}" Symbol="{font_id}" User="{font_id}"/>
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100"/>
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0"/>
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100"/>
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0"/>
        {bold_tag}
        {italic_tag}
        {underline_tag}
    </CHARSHAPE>'''
            charshape_entries.append(charshape)
        
        # CHARSHAPELIST 전체 생성
        xml = f'<CHARSHAPELIST Count="{len(charshape_entries)}">\n'
        for charshape in charshape_entries:
            xml += charshape
        xml += '\n</CHARSHAPELIST>'
        
        return xml
