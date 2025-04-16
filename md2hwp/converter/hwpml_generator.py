"""
마크다운 요소를 HWPML로 변환하는 모듈
"""
import re
from md2hwp.converter.table_generator import TableGenerator
from md2hwp.utils.xml_utils import replace_section_content

class HWPMLGenerator:
    """마크다운 요소를 HWPML로 변환하는 클래스"""
    
    def __init__(self, template_manager, special_char_handler, id_manager):
        self.template_manager = template_manager
        self.special_char_handler = special_char_handler
        self.id_manager = id_manager
        self.table_generator = TableGenerator(template_manager, id_manager)
    
    def generate_hwpml(self, md_elements, template_content, title, author, date):
        """마크다운 요소를 HWPML로 변환"""
        # --- 수정: 첫 H1 처리 플래그 추가 ---
        is_first_h1 = True
        hwpml_body, is_first_h1 = self._convert_elements_to_hwpml(md_elements, is_first_h1)
        # ----------------------------------

        result = replace_section_content(
            template_content,
            r'<BODY>.*?<SECTION Id="0">(.*?)</SECTION>.*?</BODY>',
            f'<BODY><SECTION Id="0">{hwpml_body}</SECTION></BODY>'
        )

        result = result.replace("<TITLE>제목 없음</TITLE>", f"<TITLE>{title}</TITLE>")
        result = result.replace("<AUTHOR>작성자 없음</AUTHOR>", f"<AUTHOR>{author}</AUTHOR>")
        result = result.replace("<DATE>날짜 없음</DATE>", f"<DATE>{date}</DATE>")

        return result
    
    def _convert_elements_to_hwpml(self, elements, is_first_h1):
        """마크다운 요소를 HWPML로 변환"""
        hwpml = ""

        for element in elements:
            element_type = element['type']
            template_style = self.template_manager.template_styles.get(element_type, self.template_manager.template_styles.get('p'))

            if template_style is None:
                hwpml += self._create_default_hwpml(element)
                continue

            h1_structure_to_use = template_style['structure'] # 기본적으로 원본 구조 사용

            # --- 수정: H1 처리 로직 분기 ---
            if element_type == 'h1':
                if is_first_h1:
                    # 첫 번째 H1: 원본 구조 사용 및 플래그 업데이트
                    is_first_h1 = False
                    # 구조는 h1_structure_to_use (기본값) 그대로 사용
                else:
                    # 두 번째 이후 H1: 페이지/섹션 정의 제거
                    # 1. SECDEF 제거
                    modified_structure = re.sub(r'<SECDEF.*?</SECDEF>', '', h1_structure_to_use, flags=re.DOTALL)
                    # 2. COLDEF 제거
                    modified_structure = re.sub(r'<COLDEF.*?/>', '', modified_structure)
                    # 3. P 태그 속성 정리 (ParaShape, Style만 남김)
                    match_p = re.search(r'<P\s+(.*?)\s*>', modified_structure)
                    if match_p:
                        attrs_str = match_p.group(1)
                        para_shape_match = re.search(r'ParaShape="(\d+)"', attrs_str)
                        style_match = re.search(r'Style="(\d+)"', attrs_str)
                        if para_shape_match and style_match:
                            new_p_tag = f'<P ParaShape="{para_shape_match.group(1)}" Style="{style_match.group(1)}">'
                            # 기존 P 태그를 새 태그로 교체
                            modified_structure = re.sub(r'<P\s+.*?\s*>', new_p_tag, modified_structure, count=1)
                            h1_structure_to_use = modified_structure # 수정된 구조 사용
                        else:
                             # 필요한 속성을 못찾으면 안전하게 원본 사용 (혹은 기본 P 태그 생성)
                             print(f"경고: H1 스타일의 P 태그에서 ParaShape 또는 Style 속성을 찾을 수 없습니다. 원본 구조를 사용합니다.")
                             h1_structure_to_use = h1_structure_to_use # 원본 사용
                    else:
                         print(f"경고: H1 스타일에서 P 태그를 찾을 수 없습니다. 원본 구조를 사용합니다.")
                         h1_structure_to_use = h1_structure_to_use # 원본 사용

                # 헤딩 처리 (원본 또는 수정된 구조 사용)
                # Pass element_type as style_key
                hwpml += self._insert_text_into_template(h1_structure_to_use, element['content'], element_type)
            # ----------------------------------
            elif element_type == 'h2':
                # h2 태그에 문단 간격이 조정된 ParaShape 적용
                margin_para_shape = self.template_manager.margin_para_shapes.get('h2')
                if margin_para_shape:
                    # P 태그의 ParaShape 속성만 수정
                    modified_structure = re.sub(
                        r'ParaShape="(\d+)"',
                        f'ParaShape="{margin_para_shape}"',
                        h1_structure_to_use
                    )
                    # Pass element_type as style_key
                    hwpml += self._insert_text_into_template(modified_structure, element['content'], element_type)
                else:
                    # Pass element_type as style_key
                    hwpml += self._insert_text_into_template(h1_structure_to_use, element['content'], element_type)
            elif element_type in ['h3', 'h4', 'h5', 'h6']:
                # Pass element_type as style_key
                hwpml += self._insert_text_into_template(h1_structure_to_use, element['content'], element_type)
            elif element_type == 'p':
                if element.get('has_formatting', False):
                    hwpml += self._convert_formatted_paragraph(element, template_style)
                else:
                    # Pass element_type as style_key
                    hwpml += self._insert_text_into_template(h1_structure_to_use, element['content'], element_type)
            elif element_type == 'ul':
                hwpml += self._convert_list_to_hwpml(element, template_style)
            elif element_type == 'table':
                table_hwpml = self.table_generator.create_table(element)
                hwpml += table_hwpml

        # --- 수정: is_first_h1 상태 반환 ---
        return hwpml, is_first_h1
    
    def _convert_formatted_paragraph(self, paragraph, template_style):
        """강조 요소가 있는 단락을 변환"""
        p_start_match = re.search(r'<P ParaShape="(\d+)"[^>]*>', template_style['structure'])
        if not p_start_match:
            return self._create_default_hwpml(paragraph)
        
        para_shape = p_start_match.group(1)
        normal_char_shape = template_style['char_shape']
        
        hwpml = f'<P ParaShape="{para_shape}" Style="0">'
        
        for fragment in paragraph['fragments']:
            fragment_type = fragment['type']
            content = fragment['content']
            
            # &를 &amp;로 변환
            content = content.replace('&', '&amp;')
            
            if fragment_type == 'text':
                hwpml += f'<TEXT CharShape="{normal_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'strong':
                # 굵게: 복제된 CharShape 사용
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["strong"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'em':
                # 기울임: 복제된 CharShape 사용
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["em"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'a':
                field_id = self.id_manager.next_field_id()
                inst_id = self.id_manager.next_inst_id()
                
                href = fragment.get('href', '').replace('/', '\\/')
                command = f"{href};1;0;0;"
                
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["underline"]}">'
                hwpml += f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["underline"]}"><CHAR>{content}</CHAR></TEXT>'
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["underline"]}">'
                hwpml += f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'
        
        hwpml += '</P>'
        
        return hwpml
    
    def _insert_text_into_template(self, template, text, style_key, preserve_prefix=True):
        """텍스트를 템플릿의 CHAR 태그 내에 삽입"""
        # & 문자를 &amp;로 변환
        text = text.replace('&', '&amp;')
        
        # 특수 문자 처리 (스타일 키를 직접 사용)
        template = self.special_char_handler.process_special_chars_in_template(template, style_key)
        
        # 모든 <CHAR>...</CHAR> 태그 찾기
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
        matches = list(char_pattern.finditer(template))
        
        if matches:
            # 가장 긴 매치 선택 (주요 내용일 가능성이 높음)
            longest_match = max(matches, key=lambda m: len(m.group(1)))
            start, end = longest_match.span()
            original_text = longest_match.group(1)
            
            # 접두어 처리
            if preserve_prefix:
                prefix_match = re.match(r'^(\s*[^\w\s]+\s+)', original_text)
                if prefix_match:
                    prefix = prefix_match.group(1)
                    replacement = f'<CHAR>{prefix}{text}</CHAR>'
                else:
                    replacement = f'<CHAR>{text}</CHAR>'
            else:
                replacement = f'<CHAR>{text}</CHAR>'
            
            # 텍스트 길이 변화에 따른 셀 너비 조정
            original_len = len(original_text.strip())
            new_len = len(text.strip())
            
            new_template = template
            if new_len > original_len * 1.2:  # 새 텍스트가 20% 이상 길면 셀 너비 조정
                # 셀 너비 조정 로직 - 이 부분은 복잡하므로 기존 코드를 유지하되 클래스 변수 사용
                from md2hwp.config import MAX_TABLE_WIDTH  # 필요한 경우에만 임포트

                # 1. 먼저 CHAR 태그의 위치 확인
                char_pos = template.find(longest_match.group(0))

                # 2. CHAR 태그 이전의 가장 가까운 CELL 태그 찾기
                cell_start_pattern = re.compile(r'<CELL\s+[^>]*?Width="(\d+)"')
                cell_matches = list(cell_start_pattern.finditer(template[:char_pos]))

                # 모든 셀 태그 찾기 (전체 셀 너비 계산을 위해)
                all_cell_pattern = re.compile(r'<CELL\s+[^>]*?Width="(\d+)"')
                all_cell_matches = list(all_cell_pattern.finditer(template))
                total_cells_width = sum(int(m.group(1)) for m in all_cell_matches)
                
                if cell_matches:
                    nearest_cell = cell_matches[-1]  # 가장 마지막(가장 가까운) CELL
                    cell_width = int(nearest_cell.group(1))
                    
                    # 셀 인덱스 추출 시도 (콜 주소)
                    col_addr_match = re.search(r'ColAddr="(\d+)"', template[nearest_cell.start():nearest_cell.start()+200])
                    col_addr = int(col_addr_match.group(1)) if col_addr_match else 0
                    
                    # 새 너비 계산
                    ratio = new_len / max(original_len, 1)
                    multiplier = min(max(ratio, 1.2), 5.0)  # 최대 5배로 제한
                    new_cell_width = int(cell_width * multiplier)
                    width_diff = new_cell_width - cell_width
                    
                    # 테이블 전체 너비 계산 및 조정
                    size_pattern = re.compile(r'<SIZE\s+[^>]*?Width="(\d+)"[^>]*?>')
                    table_section = template[:nearest_cell.start()]
                    size_matches = list(size_pattern.finditer(table_section))
                    
                    if size_matches:
                        last_size = size_matches[-1]
                        table_width = int(last_size.group(1))
                        new_table_width = table_width + width_diff
                        
                        # 최대 테이블 너비를 초과하는 경우 조정
                        if new_table_width > MAX_TABLE_WIDTH:
                            # 사용 가능한 여유 공간 계산
                            available_width = MAX_TABLE_WIDTH - (total_cells_width - cell_width)
                            
                            # 셀에 할당 가능한 최대 너비 계산
                            new_cell_width = min(available_width, new_cell_width)
                            width_diff = new_cell_width - cell_width
                            new_table_width = table_width + width_diff
                            
                            # 너비가 음수가 되지 않도록 보호
                            if new_cell_width <= 0:
                                new_cell_width = cell_width
                                width_diff = 0
                                new_table_width = table_width
                        
                        # 셀 너비 변경
                        if width_diff > 0:  # 너비를 늘릴 필요가 있는 경우만 변경
                            new_template = template[:nearest_cell.start(1)] + str(new_cell_width) + template[nearest_cell.end(1):]
                            
                            # 테이블 너비 변경
                            new_template = new_template[:last_size.start(1)] + str(new_table_width) + new_template[last_size.end(1):]
                            
                            # 템플릿이 변경되었으므로 CHAR 태그 위치 업데이트
                            char_pos_new = new_template.find(longest_match.group(0))
                            if char_pos_new != -1:
                                start = char_pos_new
                                end = start + len(longest_match.group(0))
            
            # 내용 삽입
            new_template = new_template[:start] + replacement + new_template[end:]
            return new_template
        
        else:
            # CHAR 태그를 찾지 못한 경우: TEXT 태그 내의 CHAR 태그를 대상으로 처리
            text_pattern = re.compile(r'<TEXT CharShape="(\d+)">(.*?)</TEXT>')
            match = text_pattern.search(template)
            if match:
                char_shape = match.group(1)
                original_content = match.group(2)
                # TEXT 태그 내에 포함된 CHAR 태그 내용 추출
                char_content_match = re.search(r'<CHAR>(.*?)</CHAR>', original_content)
                if char_content_match and preserve_prefix:
                    original_text = char_content_match.group(1)
                    prefix_match = re.match(r'^(\s*[^\w\s]+\s+)', original_text)
                    if prefix_match:
                        prefix = prefix_match.group(1)
                        replacement = f'<TEXT CharShape="{char_shape}"><CHAR>{prefix}{text}</CHAR></TEXT>'
                        return template.replace(match.group(0), replacement, 1)
                replacement = f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
                return template.replace(match.group(0), replacement, 1)
        
        return template
    
    def _convert_list_to_hwpml(self, list_element, template_style):
        """리스트를 HWPML로 변환"""
        hwpml = ""
        
        ul_template = template_style['structure']
        char_shape = template_style['char_shape']
        
        top_level_counter = 1
        
        for item in list_element['items']:
            hwpml += self._process_list_item(item, ul_template, char_shape, top_level_counter, is_top_level=True)
            if item['is_ordered']:
                top_level_counter += 1
        
        return hwpml
    
    def _process_list_item(self, item, template, char_shape, top_level_counter, is_top_level=False, counter=None):
        """리스트 항목 처리"""
        if counter is None:
            counter = {}

        hwpml = ""
        fragments = item['fragments']
        level = item.get('level', 0)
        is_ordered = item.get('is_ordered', False)

        p_tag_match = re.search(r'<P\s+([^>]+)>', template)
        p_attributes = p_tag_match.group(1) if p_tag_match else 'Style="0"'

        # 글머리 기호 설정
        if is_ordered:
            if is_top_level:
                prefix = f"{top_level_counter}. "
            else:
                if level not in counter:
                    counter[level] = 1
                prefix = f"{counter[level]}. "
                counter[level] += 1
        else:
            prefix = f"{self.template_manager.bullet_symbol} "

        indent = "  " * level
        hwpml += f'<P {p_attributes}>'

        # 글머리 기호에는 템플릿의 char_shape 사용 (리스트 스타일)
        hwpml += f'<TEXT CharShape="{char_shape}"><CHAR>{indent}{prefix}</CHAR></TEXT>'

        # 텍스트 내용에는 일반 단락 스타일 사용
        p_style = self.template_manager.template_styles.get('p', {})
        text_char_shape = p_style.get('char_shape', "0")  # 일반 단락 스타일 또는 기본값 "0"

        for fragment in fragments:
            fragment_type = fragment['type']
            content = fragment['content']
            
            # &를 &amp;로 변환
            content = content.replace('&', '&amp;')

            if fragment_type == 'text':
                hwpml += f'<TEXT CharShape="{text_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'strong':
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["strong"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'em':
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["em"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'a':
                # 하이퍼링크 처리
                field_id = self.id_manager.next_field_id()
                inst_id = self.id_manager.next_inst_id()

                href = fragment.get('href', '').replace('/', '\\/')
                command = f"{href};1;0;0;"

                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["underline"]}">'
                hwpml += f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["underline"]}"><CHAR>{content}</CHAR></TEXT>'
                hwpml += f'<TEXT CharShape="{self.template_manager.special_formats["underline"]}">'
                hwpml += f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'

        hwpml += '</P>'

        # 중첩 리스트 처리
        if 'nested_items' in item and item['nested_items']:
            nested_counter = {}
            for nested_item in item['nested_items']:
                hwpml += self._process_list_item(nested_item, template, char_shape, top_level_counter, is_top_level=False, counter=nested_counter)

        return hwpml
    
    def _create_default_hwpml(self, element):
        """기본 HWPML 요소 생성"""
        element_type = element['type']
        content = element.get('content', '')
        
        # &를 &amp;로 변환
        content = content.replace('&', '&amp;')
        
        if element_type in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element_type[1])
            para_shape = "0"
            char_shape = str(level)
        elif element_type == 'p':
            para_shape = "0"
            char_shape = "1"
        else:
            para_shape = "0"
            char_shape = "0"
        
        return f'<P ParaShape="{para_shape}" Style="0"><TEXT CharShape="{char_shape}"><CHAR>{content}</CHAR></TEXT></P>'