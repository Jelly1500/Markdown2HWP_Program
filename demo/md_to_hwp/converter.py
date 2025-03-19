# md_to_hwp/converter.py
"""
마크다운을 HWP 문서로 변환하는 모듈
"""
import re
import io
import markdown
from bs4 import BeautifulSoup, NavigableString
from md_to_hwp.hwpml_templates import HEADER, FOOTER, INTRO, TXT_END

class HWPMLConverter:
    """마크다운 텍스트를 HWPML로 변환하는 클래스"""
    
    def __init__(self, template_manager=None):
        """생성자"""
        from md_to_hwp.template_manager import MarkdownTemplate
        self.template_manager = template_manager or MarkdownTemplate()
        self.field_id_counter = 0  # FieldId와 InstId를 위한 카운터
    
    def convert_markdown_to_hwpml(self, md_text, title="제목 없음", author="작성자 없음", date="날짜 없음"):
        """마크다운 텍스트를 HWPML로 변환"""
        # YAML 헤더 제거 (있는 경우)
        md_text = re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)
        
        # 마크다운을 HTML로 변환
        html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'], tab_length=2)
        
        # 현재 템플릿 가져오기
        current_template = self.template_manager.get_current_template()
        
        # 템플릿에 따라 동적 HWPML 요소 생성
        char_shape_list = self.generate_charshapelist(current_template)
        
        # 기존 HEADER에서 CHARSHAPELIST 부분 교체
        header = re.sub(
            r'<CHARSHAPELIST.*?</CHARSHAPELIST>',
            char_shape_list,
            HEADER,
            flags=re.DOTALL
        )
        
        # HTML을 HWPML로 변환
        hwpml_content = self.convert_html_to_hwpml(html)
        
        # 문서 조합
        hwpml = header + INTRO + hwpml_content + FOOTER
        
        # 메타데이터 치환
        hwpml = hwpml.replace("___TITLE___", title)
        hwpml = hwpml.replace("___AUTHOR___", author)
        hwpml = hwpml.replace("___DATE___", date)
        
        return hwpml
    
    def generate_charshapelist(self, template_data):
        """템플릿 설정에 따라 CHARSHAPELIST를 동적으로 생성"""
        # 각 요소와 charShape ID 매핑 정의
        element_id_map = {
            "paragraph": "0",  # 일반 텍스트: charShape="0"
            "heading1": "1",   # H1 태그: charShape="1"
            "heading2": "2",   # H2 태그: charShape="2"
            "heading3": "3",   # H3 태그: charShape="3"
            "heading4": "4",   # H4 태그: charShape="4"
            "bold": "6",       # 굵게: charShape="6"
            "italic": "7",     # 기울임: charShape="7"
            "link": "8"        # 링크: charShape="8"
        }

        # charShapeList 생성
        charshape_entries = []

        # 각 요소 처리 (1~9번까지 항상 모든 ID 생성)
        for id_num in range(9):
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
                text_color = self.template_manager.rgb_to_hwp_color(color_hex)

                # 스타일 처리
                bold_tag = "<BOLD />" if settings.get("bold", False) else ""
                italic_tag = "<ITALIC />" if settings.get("italic", False) else ""
                underline_tag = f'<UNDERLINE Color="0" Shape="Solid" Type="Single" />' if settings.get("underline", False) else ""
            else:
                # 기본값 설정
                size = 1000
                text_color = 0
                bold_tag = "<BOLD />" if id_num in [1, 2, 3, 4, 5, 6] else ""
                italic_tag = "<ITALIC />" if id_num == 7 else ""
                underline_tag = f'<UNDERLINE Color="0" Shape="Solid" Type="Single" />' if id_num == 8 else ""

            # charShape 항목 생성
            charshape = f'''
    <CHARSHAPE BorderFillId="2" Height="{size}" Id="{id_str}" ShadeColor="4294967295" SymMark="0" TextColor="{text_color}" UseFontSpace="false" UseKerning="false">
    <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
    <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
    <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
    <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
    <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
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
    
    def convert_html_to_hwpml(self, html):
        """HTML을 HWPML로 변환"""
        soup = BeautifulSoup(html, 'html.parser')
        hwpml_content = ""
        
        # 모든 최상위 요소 처리
        for element in soup:
            if isinstance(element, NavigableString):
                text = element.strip()
                if text:
                    tmpl = self.template_manager.get_current_template().get("paragraph", {})
                    char_shape = tmpl.get("charShape", "0")
                    para_shape = tmpl.get("paraShape", "0")
                    hwpml_content += f'<P ParaShape="{para_shape}" Style="0"><TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT></P>\n'
            else:
                hwpml_content += self.convert_element_to_hwpml(element)
        
        return hwpml_content
    
    def convert_element_to_hwpml(self, element):
        """HTML 요소를 HWPML로 변환"""
        if element.name == 'h1':
            return self.template_manager.apply_template_to_element("heading1", element.text)
        elif element.name == 'h2':
            return self.template_manager.apply_template_to_element("heading2", element.text)
        elif element.name == 'h3':
            return self.template_manager.apply_template_to_element("heading3", element.text)
        elif element.name == 'h4':
            return self.template_manager.apply_template_to_element("heading4", element.text)
        elif element.name == 'p':
            return self.convert_paragraph_to_hwpml(element)
        elif element.name in ['ul', 'ol']:
            return self.convert_list_to_hwpml(element, depth=0)
        elif element.name == 'table':
            # 테이블 주변에 적절한 문단 구조 추가
            return '<P ParaShape="0" Style="0"><TEXT CharShape="0">' + self.convert_table_to_hwpml(element) + '<CHAR/></TEXT></P>'
        
        return ""
    
    def convert_paragraph_to_hwpml(self, p):
        """문단 요소 변환"""
        current_tmpl = self.template_manager.get_current_template()
        para_tmpl = current_tmpl.get("paragraph", {})
        para_shape = para_tmpl.get("paraShape", "0")

        hwpml = f'<P ParaShape="{para_shape}" Style="0">'
        has_content = False

        for child in p.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text:
                    # 일반 텍스트에는 paragraph 스타일의 charShape="0" 사용
                    hwpml += f'<TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT>'
                    has_content = True
            elif child.name == 'a':
                # 링크에는 link 스타일의 charShape="8" 사용
                hwpml += self.convert_a_to_hwpml(child)
                has_content = True
            elif child.name in ['b', 'strong']:
                # 굵게에는 bold 스타일의 charShape="6" 사용
                hwpml += f'<TEXT CharShape="6"><CHAR>{child.text}</CHAR></TEXT>'
                has_content = True
            elif child.name in ['i', 'em']:
                # 기울임에는 italic 스타일의 charShape="7" 사용
                hwpml += f'<TEXT CharShape="7"><CHAR>{child.text}</CHAR></TEXT>'
                has_content = True

        if not has_content:
            hwpml += '<TEXT CharShape="0"/>'

        hwpml += '</P>\n'
        return hwpml

    
    def convert_a_to_hwpml(self, a):
        """링크 요소 변환"""
        current_tmpl = self.template_manager.get_current_template()
        link_tmpl = current_tmpl.get("link", {})
        char_shape = link_tmpl.get("charShape", "8")
        
        self.field_id_counter += 1
        field_id = self.field_id_counter
        inst_id = self.field_id_counter + 1000000
        
        url = a.get('href', '').replace('/', '\\/')
        text = a.text
        command = f"{url};1;0;0;"
        
        field_begin = (
            f'<TEXT CharShape="0">'
            f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" '
            f'FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
            f'</TEXT>'
        )
        
        link_text = f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
        
        field_end = (
            f'<TEXT CharShape="0">'
            f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
            f'<CHAR/>'
            f'</TEXT>'
        )
        
        return field_begin + link_text + field_end
    
    def convert_list_to_hwpml(self, list_tag, depth=0):
        """목록 요소 변환"""
        hwpml = ""
        is_ordered = (list_tag.name == 'ol')
        item_counter = 1
        
        for li in list_tag.find_all('li', recursive=False):
            hwpml += self.convert_list_item_to_hwpml(li, depth, is_ordered, item_counter)
            if is_ordered:
                item_counter += 1
            
            # 중첩된 목록 처리
            for child_list in li.find_all(['ul', 'ol'], recursive=False):
                hwpml += self.convert_list_to_hwpml(child_list, depth + 1)
        
        return hwpml
    
    def convert_list_item_to_hwpml(self, li, depth, is_ordered, item_number):
        """목록 항목 변환"""
        current_tmpl = self.template_manager.get_current_template()
        list_type = "ordered_list" if is_ordered else "bullet_list"
        list_tmpl = current_tmpl.get(list_type, {})
        
        # 문단 모양 ID 결정 (들여쓰기에 따라)
        para_shape_id = min(depth + 1, 6)
        
        hwpml = f'<P ParaShape="{para_shape_id}" Style="0">'
        
        # 항목 기호 또는 번호 추가
        if is_ordered:
            format_str = list_tmpl.get("format", "%d. ")
            bullet_text = format_str.replace("%d", str(item_number))
        else:
            bullet_text = list_tmpl.get("symbol", "• ")
        
        char_shape = list_tmpl.get("charShape", "0")
        hwpml += f'<TEXT CharShape="{char_shape}"><CHAR>{bullet_text}</CHAR></TEXT>'
        
        # 목록 항목의 내용 처리
        for child in li.children:
            if isinstance(child, NavigableString):
                text = child.strip()
                if text:
                    hwpml += f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
            elif child.name == 'a':
                hwpml += self.convert_a_to_hwpml(child)
            elif child.name in ['b', 'strong']:
                bold_tmpl = current_tmpl.get("bold", {})
                bold_char_shape = bold_tmpl.get("charShape", "6")
                hwpml += f'<TEXT CharShape="{bold_char_shape}"><CHAR>{child.get_text()}</CHAR></TEXT>'
            elif child.name in ['i', 'em']:
                italic_tmpl = current_tmpl.get("italic", {})
                italic_char_shape = italic_tmpl.get("charShape", "7")
                hwpml += f'<TEXT CharShape="{italic_char_shape}"><CHAR>{child.get_text()}</CHAR></TEXT>'
            elif child.name in ['ul', 'ol']:
                # 중첩 목록은 convert_list_to_hwpml에서 별도 처리
                pass
            else:
                # 기타 요소는 재귀 처리
                hwpml += self.convert_element_to_hwpml(child)
        
        hwpml += '</P>\n'
        return hwpml
    
    def convert_table_to_hwpml(self, table):
        """표 요소 변환"""
        current_tmpl = self.template_manager.get_current_template()
        table_tmpl = current_tmpl.get("table", {})
        
        # 모든 행 찾기
        rows = table.find_all('tr')
        row_count = len(rows)
        
        # 열 수 결정
        col_count = max(len(row.find_all(['td', 'th'])) for row in rows) if rows else 0
        
        # 테이블 너비 설정
        total_table_width = 41950  # 테이블 총 너비
        cell_width = total_table_width // col_count if col_count > 0 else 20975  # 셀 너비 동적 조정
        
        # 테이블 구조 구축
        hwpml = f"""
<TABLE BorderFill="3" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="true" RowCount="{row_count}">
<SHAPEOBJECT InstId="1797984080" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1">
<SIZE Height="3846" HeightRelTo="Absolute" Protect="false" Width="{total_table_width}" WidthRelTo="Absolute"/>
<POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="true" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Column" TreatAsChar="false" VertAlign="Top" VertOffset="0" VertRelTo="Para"/>
<OUTSIDEMARGIN Bottom="283" Left="283" Right="283" Top="283"/>
</SHAPEOBJECT>
<INSIDEMARGIN Bottom="141" Left="510" Right="510" Top="141"/>"""
        
        # 행과 셀 처리
        for row_index, row in enumerate(rows):
            hwpml += f"\n<ROW>"
            cells = row.find_all(['td', 'th'])
            
            # 부족한 셀 채우기
            while len(cells) < col_count:
                cells.append(None)
            
            for cell_index in range(col_count):
                cell = cells[cell_index] if cell_index < len(cells) else None
                
                # 행 위치에 따라 테두리 스타일 결정
                if row_index == 0:
                    border_fill_id = table_tmpl.get("header_border", "3")  # 첫번째 행: 상하단 모두 실선
                elif row_index == row_count - 1:
                    border_fill_id = table_tmpl.get("last_border", "4")  # 마지막 행: 상단 점선, 하단 실선
                else:
                    border_fill_id = table_tmpl.get("middle_border", "6")  # 중간 행: 상하단 모두 점선
                
                hwpml += f"""
<CELL BorderFill="{border_fill_id}" ColAddr="{cell_index}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="false" Height="282" Protect="false" RowAddr="{row_index}" RowSpan="1" Width="{cell_width}">
<CELLMARGIN Bottom="141" Left="510" Right="510" Top="141"/>
<PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
<P ParaShape="0" Style="0">"""
                
                # 셀 내용 추가 (마크다운 서식 지원)
                hwpml += self.convert_cell_content_to_hwpml(cell)
                
                hwpml += """
</P>
</PARALIST>
</CELL>"""
            
            hwpml += f"\n</ROW>"
        
        hwpml += "\n</TABLE>"
        return hwpml
    
    def convert_cell_content_to_hwpml(self, cell):
        """셀 내용 변환 (마크다운 서식 지원)"""
        if cell is None:
            return '<TEXT CharShape="0"><CHAR>&#160;</CHAR></TEXT>'  # 빈 셀

        # 셀에서 직접 HTML 내용 추출 (text가 아닌 내부 태그 포함)
        hwpml = ''

        # 내용이 없으면 빈 태그 반환
        if len(list(cell.children)) == 0:
            content = cell.string if cell.string else "&#160;"
            return f'<TEXT CharShape="0"><CHAR>{content}</CHAR></TEXT>'

        # 내용 처리
        for child in cell.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    # 일반 텍스트에는 charShape="0" 사용
                    hwpml += f'<TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT>'
            elif child.name == 'strong' or child.name == 'b':
                # 굵게에는 charShape="6" 사용
                hwpml += f'<TEXT CharShape="6"><CHAR>{child.get_text()}</CHAR></TEXT>'
            elif child.name == 'em' or child.name == 'i':
                # 기울임에는 charShape="7" 사용
                hwpml += f'<TEXT CharShape="7"><CHAR>{child.get_text()}</CHAR></TEXT>'
            elif child.name == 'a':
                # 링크에는 charShape="8" 사용 (convert_a_to_hwpml 함수 호출)
                hwpml += self.convert_a_to_hwpml(child)

        return hwpml if hwpml else '<TEXT CharShape="0"><CHAR>&#160;</CHAR></TEXT>'

    def save_to_file(self, hwpml, file_path):
        """HWPML을 파일로 저장"""
        with io.open(file_path, "w", encoding="utf-8") as f:
            f.write(hwpml)
