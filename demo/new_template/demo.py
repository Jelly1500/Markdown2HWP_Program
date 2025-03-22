import sys
import re
import io
import mistune
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, NavigableString
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar)
from PySide6.QtGui import QIcon

class HWPMLConverter:
    def __init__(self):
        # 초기화 필드
        self.field_id_counter = 0
        self.inst_id_counter = 1000000

        # 순서대로 매핑할 마크다운 요소 목록 (순서있는 리스트 제거)
        self.style_mapping_order = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'a', 'strong', 'em'
        ]

        # 템플릿 스타일 정보를 저장할 딕셔너리
        self.template_styles = {key: None for key in self.style_mapping_order}
        
        # 순서 없는 리스트에 사용할 글머리표 특수기호
        self.bullet_symbol = "•"  # 기본 글머리표
        
    def load_template(self, template_path):
        """HWPML 템플릿 파일을 로드하고 서식 구조 추출"""
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                self.template_content = file.read()
            
            # 템플릿에서 서식 구조 추출 (순서대로)
            self._extract_template_styles()
            return True
            
        except Exception as e:
            print(f"템플릿 로드 오류: {e}")
            return False
    
    def _extract_template_styles(self):
        """템플릿에서 순서대로 서식 스타일 추출"""
        # BODY 섹션 찾기
        soup = BeautifulSoup(self.template_content, 'xml')
        body_section = soup.find('BODY')
        if not body_section:
            raise ValueError("템플릿에 BODY 섹션이 없습니다")
            
        section = body_section.find('SECTION')
        if not section:
            raise ValueError("템플릿에 SECTION 요소가 없습니다")
        
        # 모든 균형 잡힌 P 태그 구조 순서대로 추출
        balanced_p_tags = self._extract_balanced_p_tags(str(section))
        
        # 순서대로 마크다운 요소에 매핑
        for idx, tag_structure in enumerate(balanced_p_tags):
            if idx < len(self.style_mapping_order):
                style_key = self.style_mapping_order[idx]
                self.template_styles[style_key] = {
                    'structure': tag_structure,
                    'para_shape': self._extract_para_shape(tag_structure),
                    'char_shape': self._extract_char_shape(tag_structure),
                    'has_table': '<TABLE' in tag_structure,
                    'has_field': '<FIELDBEGIN' in tag_structure
                }
                
                # 순서 없는 리스트에서 글머리표 추출
                if style_key == 'ul':
                    bullet = self._extract_bullet_symbol(tag_structure)
                    if bullet:
                        self.bullet_symbol = bullet
        
        # 템플릿 스타일 매핑 결과 출력
        print("추출된 템플릿 스타일 매핑:")
        for key, value in self.template_styles.items():
            if value:
                print(f"  {key}: ParaShape={value['para_shape']}, CharShape={value['char_shape']}")
            else:
                print(f"  {key}: 매핑 없음")
        
        print(f"  추출된 글머리표 기호: '{self.bullet_symbol}'")
    
    def _extract_bullet_symbol(self, structure):
        """순서 없는 리스트 구조에서 글머리표 특수기호 추출"""
        # CHAR 태그 내용에서 첫 번째 특수기호 추출
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
        match = char_pattern.search(structure)
        
        if match:
            content = match.group(1).strip()
            # 콘텐츠의 첫 번째 문자가 특수기호일 가능성이 높음
            if content and not content[0].isalnum():
                # 기호와 다음 텍스트 사이의 공백 처리
                bullet_parts = re.match(r'([^\w\s]+)(\s*)(.*)', content)
                if bullet_parts:
                    return bullet_parts.group(1)  # 특수기호만 반환
        
        return None
    
    def _extract_balanced_p_tags(self, content):
        """균형 잡힌 P 태그 쌍을 순서대로 추출"""
        elements = []
        start_idx = 0
        
        while True:
            # P 태그 시작 찾기
            p_start = content.find('<P ', start_idx)
            if p_start == -1:
                break
                
            # 여는 태그와 닫는 태그 카운팅 초기화
            open_tags = 1
            close_tags = 0
            search_idx = p_start + 2  # '<P' 이후부터 탐색
            
            # 균형 잡힌 태그 찾기
            while open_tags > close_tags and search_idx < len(content):
                next_open = content.find('<P ', search_idx)
                next_close = content.find('</P>', search_idx)
                
                if next_close == -1:
                    # 닫는 태그가 없으면 종료
                    break
                    
                if next_open != -1 and next_open < next_close:
                    open_tags += 1
                    search_idx = next_open + 2
                else:
                    close_tags += 1
                    search_idx = next_close + 4
            
            # 하나의 완전한 서식 요소 추출
            if open_tags == close_tags:
                element = content[p_start:search_idx]
                elements.append(element)
                start_idx = search_idx
            else:
                # 균형이 맞지 않으면 다음 위치에서 다시 시작
                start_idx = p_start + 2
        
        return elements
    
    def _extract_para_shape(self, structure):
        """구조에서 단락 모양 ID 추출"""
        match = re.search(r'<P ParaShape="(\d+)"', structure)
        return match.group(1) if match else "0"
    
    def _extract_char_shape(self, structure):
        """구조에서 글자 모양 ID 추출"""
        match = re.search(r'<TEXT CharShape="(\d+)"', structure)
        return match.group(1) if match else "0"
    
    def convert_md_to_hwpml(self, md_text, title="제목 없음", author="작성자 없음", date="날짜 없음"):
        """마크다운 텍스트를 HWPML로 변환"""
        if not hasattr(self, 'template_content'):
            raise ValueError("템플릿이 로드되지 않았습니다. 먼저 load_template() 호출 필요")
        
        # 마크다운을 HTML로 변환
        html = mistune.html(md_text)        
        # HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')
        
        # 마크다운 요소 추출
        md_elements = self._extract_markdown_elements(soup)
        
        # HWPML 변환
        hwpml_body = self._convert_elements_to_hwpml(md_elements)
        
        # 템플릿 BODY 섹션 교체
        result = re.sub(
            r'<BODY>.*?<SECTION Id="0">(.*?)</SECTION>.*?</BODY>',
            f'<BODY><SECTION Id="0">{hwpml_body}</SECTION></BODY>',
            self.template_content,
            flags=re.DOTALL
        )
        
        # 제목, 작성자, 날짜 교체
        result = result.replace("<TITLE>제목 없음</TITLE>", f"<TITLE>{title}</TITLE>")
        result = result.replace("<AUTHOR>작성자 없음</AUTHOR>", f"<AUTHOR>{author}</AUTHOR>")
        result = result.replace("<DATE>날짜 없음</DATE>", f"<DATE>{date}</DATE>")
        
        return result
    
    def _extract_markdown_elements(self, soup):
        """HTML에서 마크다운 요소 추출"""
        elements = []
        
        for tag in soup.find_all(True, recursive=False):
            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                elements.append({
                    'type': tag.name,
                    'content': tag.get_text()
                })
            elif tag.name == 'p':
                # 단락 내부의 강조 요소 확인
                if tag.find(['strong', 'b', 'em', 'i', 'a']):
                    # 강조 요소가 있는 복합 단락
                    elements.append({
                        'type': 'p',
                        'content': tag.get_text(),
                        'has_formatting': True,
                        'fragments': self._extract_paragraph_fragments(tag)
                    })
                else:
                    # 단순 단락
                    elements.append({
                        'type': 'p',
                        'content': tag.get_text(),
                        'has_formatting': False
                    })
            elif tag.name in ['ul', 'ol']:
                elements.append({
                    'type': 'ul',  # 순서 있는/없는 리스트 모두 ul로 처리
                    'items': self._extract_list_items(tag),
                    'is_ordered': tag.name == 'ol'  # 순서 있는 리스트 여부 저장
                })
            elif tag.name == 'table':
                elements.append({
                    'type': 'table',
                    'rows': self._extract_table_rows(tag)
                })
        
        return elements
    
    def _extract_paragraph_fragments(self, p_tag):
        """단락 내 텍스트와 강조 요소를 조각으로 추출"""
        fragments = []
        
        for child in p_tag.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text:  # 빈 문자열이 아닌 경우에만 추가
                    fragments.append({
                        'type': 'text',
                        'content': text
                    })
            elif child.name in ['strong', 'b']:
                fragments.append({
                    'type': 'strong',
                    'content': child.get_text()
                })
            elif child.name in ['em', 'i']:
                fragments.append({
                    'type': 'em',
                    'content': child.get_text()
                })
            elif child.name == 'a':
                fragments.append({
                    'type': 'a',
                    'content': child.get_text(),
                    'href': child.get('href', '')
                })
        
        return fragments
    
    def _extract_list_items(self, list_tag):
        items = []
        is_ordered = list_tag.name == 'ol'

        for li in list_tag.find_all('li', recursive=False):
            item_fragments = []
            nested_lists = []

            for child in li.children:
                if isinstance(child, NavigableString):
                    text = str(child).strip()
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
                elif child.name in ['strong', 'b']:
                    item_fragments.append({'type': 'strong', 'content': child.get_text()})
                elif child.name in ['em', 'i']:
                    item_fragments.append({'type': 'em', 'content': child.get_text()})
                elif child.name == 'a':
                    item_fragments.append({'type': 'a', 'content': child.get_text(), 'href': child.get('href', '')})
                elif child.name not in ['ul', 'ol']:
                    text = child.get_text().strip()
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
                else:
                    nested_lists.append(child)

            item_info = {
                'fragments': item_fragments,
                'is_ordered': is_ordered,
                'level': 0
            }

            if nested_lists:
                item_info['nested_items'] = []
                for nested_list in nested_lists:
                    nested_items = self._extract_nested_list_items(nested_list, 1)
                    item_info['nested_items'].extend(nested_items)

            items.append(item_info)
        return items
    
    def _extract_nested_list_items(self, list_tag, level):
        items = []
        is_ordered = list_tag.name == 'ol'

        for li in list_tag.find_all('li', recursive=False):
            item_fragments = []
            nested_lists = []

            for child in li.children:
                if isinstance(child, NavigableString):
                    text = str(child).strip()
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
                elif child.name in ['strong', 'b']:
                    item_fragments.append({'type': 'strong', 'content': child.get_text()})
                elif child.name in ['em', 'i']:
                    item_fragments.append({'type': 'em', 'content': child.get_text()})
                elif child.name == 'a':
                    item_fragments.append({'type': 'a', 'content': child.get_text(), 'href': child.get('href', '')})
                elif child.name not in ['ul', 'ol']:
                    text = child.get_text().strip()
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
                else:
                    nested_lists.append(child)

            item_info = {
                'fragments': item_fragments,
                'is_ordered': is_ordered,
                'level': level
            }

            if nested_lists:
                item_info['nested_items'] = []
                for nested_list in nested_lists:
                    nested_items = self._extract_nested_list_items(nested_list, level + 1)
                    item_info['nested_items'].extend(nested_items)

            items.append(item_info)
        return items
    
    def _extract_table_rows(self, table_tag):
        """표 행과 셀 데이터 추출"""
        rows = []
        
        # 표 헤더 처리
        thead = table_tag.find('thead')
        if thead:
            for tr in thead.find_all('tr'):
                row = []
                for th in tr.find_all(['th']):
                    row.append({
                        'content': th.get_text(),
                        'is_header': True
                    })
                if row:
                    rows.append(row)
        
        # 표 본문 처리
        tbody = table_tag.find('tbody') or table_tag
        for tr in tbody.find_all('tr'):
            row = []
            for td in tr.find_all(['td']):
                row.append({
                    'content': td.get_text(),
                    'is_header': False
                })
            if row:
                rows.append(row)
                
        return rows
    
    def _convert_elements_to_hwpml(self, elements):
        """마크다운 요소를 HWPML로 변환"""
        hwpml = ""
        
        for element in elements:
            element_type = element['type']
            
            # 매핑된 템플릿 스타일 가져오기
            template_style = self.template_styles.get(element_type)
            
            if template_style is None:
                # 템플릿에 매핑이 없는 경우 기본 단락 스타일 사용
                template_style = self.template_styles.get('p')
                if template_style is None:
                    # 기본 단락도 없는 경우 기본값 생성
                    hwpml += self._create_default_hwpml(element)
                    continue
            
            # 요소 유형에 따른 변환
            if element_type in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                hwpml += self._insert_text_into_template(template_style['structure'], element['content'])
            elif element_type == 'p':
                if element.get('has_formatting', False):
                    # 강조 요소가 있는 복합 단락
                    hwpml += self._convert_formatted_paragraph(element, template_style)
                else:
                    # 단순 단락
                    hwpml += self._insert_text_into_template(template_style['structure'], element['content'])
            elif element_type == 'ul':
                hwpml += self._convert_list_to_hwpml(element, template_style)
            elif element_type == 'table':
                if template_style['has_table']:
                    hwpml += self._convert_table_to_hwpml(element, template_style)
                else:
                    hwpml += self._create_default_table_hwpml(element)
        
        return hwpml
    
    def _convert_formatted_paragraph(self, paragraph, template_style):
        """강조 요소가 있는 단락을 변환 - 하나의 단락으로 유지"""
        # 단락의 기본 서식 추출 (P 태그 시작 부분)
        p_start_match = re.search(r'<P ParaShape="(\d+)"[^>]*>', template_style['structure'])
        if not p_start_match:
            return self._create_default_hwpml(paragraph)
        
        para_shape = p_start_match.group(1)
        
        # 기본 문자 모양 추출
        normal_char_shape = template_style['char_shape']
        
        # 강조 요소 문자 모양 추출
        strong_style = self.template_styles.get('strong')
        em_style = self.template_styles.get('em')
        a_style = self.template_styles.get('a')
        
        strong_char_shape = strong_style['char_shape'] if strong_style else "8"  # 기본 굵게 스타일
        em_char_shape = em_style['char_shape'] if em_style else "9"  # 기본 기울임 스타일
        link_char_shape = a_style['char_shape'] if a_style else "10"  # 기본 링크 스타일
        
        # 단락 시작
        hwpml = f'<P ParaShape="{para_shape}" Style="0">'
        
        # 각 텍스트 조각 처리
        for fragment in paragraph['fragments']:
            fragment_type = fragment['type']
            content = fragment['content']
            
            if fragment_type == 'text':
                # 일반 텍스트
                hwpml += f'<TEXT CharShape="{normal_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'strong':
                # 굵은 텍스트
                hwpml += f'<TEXT CharShape="{strong_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'em':
                # 기울임 텍스트
                hwpml += f'<TEXT CharShape="{em_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'a':
                # 링크
                if a_style and a_style.get('has_field', False):
                    # 링크 필드 생성
                    field_id = str(self.field_id_counter + 1)
                    inst_id = str(self.inst_id_counter + 1)
                    self.field_id_counter += 1
                    self.inst_id_counter += 1
                    
                    href = fragment.get('href', '')
                    href = href.replace('/', '\\/')
                    command = f"{href};1;0;0;"
                    
                    # 링크 필드 시작
                    hwpml += f'<TEXT CharShape="{link_char_shape}">'
                    hwpml += f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
                    hwpml += '</TEXT>'
                    
                    # 링크 텍스트
                    hwpml += f'<TEXT CharShape="{link_char_shape}"><CHAR>{content}</CHAR></TEXT>'
                    
                    # 링크 필드 종료
                    hwpml += f'<TEXT CharShape="{link_char_shape}">'
                    hwpml += f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
                    hwpml += '</TEXT>'
                else:
                    # 링크 필드가 없으면 일반 텍스트로 처리
                    hwpml += f'<TEXT CharShape="{link_char_shape}"><CHAR>{content}</CHAR></TEXT>'
        
        # 단락 종료
        hwpml += '</P>'
        
        return hwpml
    
    def _insert_text_into_template(self, template, text):
        """텍스트를 템플릿의 CHAR 태그 내에 삽입"""
        # CHAR 태그 찾기
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
        match = char_pattern.search(template)
        
        if match:
            # 첫 번째 CHAR 태그 내용 교체
            return template.replace(match.group(0), f'<CHAR>{text}</CHAR>', 1)
        else:
            # CHAR 태그가 없으면 TEXT 태그 내에 새로 추가
            text_pattern = re.compile(r'<TEXT CharShape="(\d+)">(.*?)</TEXT>')
            match = text_pattern.search(template)
            if match:
                char_shape = match.group(1)
                return template.replace(match.group(0), f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>', 1)
        
        # 적절한 위치를 찾을 수 없으면 원본 반환
        return template
    
    def _convert_list_to_hwpml(self, list_element, template_style):
        hwpml = ""
        ul_template = template_style['structure']
        char_shape = template_style['char_shape']
        top_level_counter = 1  # 최상단 리스트용 카운터 초기화

        # 최상단 리스트 항목 처리
        for item in list_element['items']:
            hwpml += self._process_list_item(item, ul_template, char_shape, top_level_counter, is_top_level=True)
            if item['is_ordered']:  # 순서 있는 리스트라면 카운터 증가
                top_level_counter += 1

        return hwpml


    def _process_list_item(self, item, template, char_shape, top_level_counter, is_top_level=False, counter=None):
        if counter is None:
            counter = {}  # 중첩 리스트용 카운터 초기화
            
        hwpml = ""
        fragments = item['fragments']
        level = item.get('level', 0)
        is_ordered = item.get('is_ordered', False)
        
        # 템플릿에서 P 태그 속성 추출
        p_tag_match = re.search(r'<P\s+([^>]+)>', template)
        p_attributes = p_tag_match.group(1) if p_tag_match else 'Style="0"'
        
        # 접두사 생성
        if is_ordered:
            if is_top_level:
                # 최상위 리스트면 top_level_counter 사용
                prefix = f"{top_level_counter}. "
            else:
                # 중첩 리스트면 레벨별 카운터 사용, 새 레벨 시작 시 초기화
                if level not in counter:
                    counter[level] = 1  # 새로운 레벨 시작 시 1로 초기화
                prefix = f"{counter[level]}. "
                counter[level] += 1
        else:
            prefix = f"{self.bullet_symbol} "  # 순서 없는 리스트의 경우
        
        # 들여쓰기
        indent = "  " * level
        
        # 단락 시작
        hwpml += f'<P {p_attributes}>'
        
        # 접두사 추가 (기본 char_shape 사용)
        hwpml += f'<TEXT CharShape="{char_shape}"><CHAR>{indent}{prefix}</CHAR></TEXT>'
        
        # 서식 스타일 가져오기
        strong_style = self.template_styles.get('strong')
        em_style = self.template_styles.get('em')
        a_style = self.template_styles.get('a')
        
        strong_char_shape = strong_style['char_shape'] if strong_style else "8"
        em_char_shape = em_style['char_shape'] if em_style else "9"
        link_char_shape = a_style['char_shape'] if a_style else "10"
        
        # 각 조각 처리
        for fragment in fragments:
            fragment_type = fragment['type']
            content = fragment['content']
            
            if fragment_type == 'text':
                hwpml += f'<TEXT CharShape="{char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'strong':
                hwpml += f'<TEXT CharShape="{strong_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'em':
                hwpml += f'<TEXT CharShape="{em_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'a':
                if a_style and a_style.get('has_field', False):
                    field_id = str(self.field_id_counter + 1)
                    inst_id = str(self.inst_id_counter + 1)
                    self.field_id_counter += 1
                    self.inst_id_counter += 1
                    
                    href = fragment.get('href', '')
                    href = href.replace('/', '\\/')
                    command = f"{href};1;0;0;"
                    
                    hwpml += f'<TEXT CharShape="{link_char_shape}">'
                    hwpml += f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
                    hwpml += '</TEXT>'
                    hwpml += f'<TEXT CharShape="{link_char_shape}"><CHAR>{content}</CHAR></TEXT>'
                    hwpml += f'<TEXT CharShape="{link_char_shape}">'
                    hwpml += f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
                    hwpml += '</TEXT>'
                else:
                    hwpml += f'<TEXT CharShape="{link_char_shape}"><CHAR>{content}</CHAR></TEXT>'
        
        # 단락 종료
        hwpml += '</P>'
        
        # 중첩 항목 처리
        if 'nested_items' in item and item['nested_items']:
            # 중첩 리스트 처리 전에 새 counter 전달 (레벨별 독립성 보장)
            nested_counter = {}
            for nested_item in item['nested_items']:
                hwpml += self._process_list_item(nested_item, template, char_shape, top_level_counter, is_top_level=False, counter=nested_counter)
        
        return hwpml

    
    def _convert_table_to_hwpml(self, table_element, template_style):
        """표를 HWPML로 변환"""
        # 템플릿 구조에서 표 추출
        table_pattern = re.compile(r'<TABLE.*?</TABLE>', re.DOTALL)
        match = table_pattern.search(template_style['structure'])
        
        if not match:
            return self._create_default_table_hwpml(table_element)
            
        table_template = match.group(0)
        rows = table_element['rows']
        
        # 표 행 수와 열 수 결정
        row_count = len(rows)
        col_count = max(len(row) for row in rows) if rows else 0
        
        # 템플릿 표 크기 조정
        table_template = re.sub(r'ColCount="\d+"', f'ColCount="{col_count}"', table_template)
        table_template = re.sub(r'RowCount="\d+"', f'RowCount="{row_count}"', table_template)
        
        # 기존 행 추출
        row_pattern = re.compile(r'<ROW>.*?</ROW>', re.DOTALL)
        row_match = row_pattern.search(table_template)
        
        if row_match:
            row_template = row_match.group(0)
            
            # 새 행 생성
            new_rows = ""
            for row_idx, row in enumerate(rows):
                new_row = row_template
                
                # 셀 패턴 찾기
                cell_pattern = re.compile(r'<CELL.*?</CELL>', re.DOTALL)
                cell_matches = list(cell_pattern.finditer(new_row))
                
                # 새 셀 콘텐츠로 교체
                for cell_idx, cell in enumerate(row):
                    if cell_idx < len(cell_matches):
                        cell_template = cell_matches[cell_idx].group(0)
                        # 셀 내용 교체
                        cell_content = cell['content']
                        # CHAR 태그 내용 교체
                        new_cell = re.sub(
                            r'<CHAR>.*?</CHAR>',
                            f'<CHAR>{cell_content}</CHAR>',
                            cell_template,
                            flags=re.DOTALL
                        )
                        new_row = new_row.replace(cell_template, new_cell, 1)
                
                # 행 번호 업데이트
                new_row = re.sub(r'RowAddr="\d+"', f'RowAddr="{row_idx}"', new_row)
                new_rows += new_row
            
            # 모든 행 교체
            table_template = row_pattern.sub(new_rows, table_template)
            
            # 전체 템플릿 구조에 표 삽입
            full_structure = re.sub(
                r'<TABLE.*?</TABLE>',
                table_template,
                template_style['structure'],
                flags=re.DOTALL
            )
            
            return full_structure
        
        # 행 템플릿을 찾지 못한 경우 기본 표 생성
        return self._create_default_table_hwpml(table_element)
    
    def _create_default_table_hwpml(self, table_element):
        """기본 HWPML 표 생성"""
        rows = table_element['rows']
        row_count = len(rows)
        col_count = max(len(row) for row in rows) if rows else 0
        
        # 기본 표 크기 설정
        total_table_width = 41950
        cell_width = total_table_width // col_count if col_count > 0 else 20975
        
        # 고유 ID 생성
        inst_id = self.inst_id_counter
        self.inst_id_counter += 1
        
        # 표 구조 생성
        hwpml = f"""<P ParaShape="0" Style="0"><TEXT CharShape="0">
<TABLE BorderFill="3" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="true" RowCount="{row_count}">
<SHAPEOBJECT InstId="{inst_id}" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1">
  <SIZE Height="3846" HeightRelTo="Absolute" Protect="false" Width="{total_table_width}" WidthRelTo="Absolute"/>
  <POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="true" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Column" TreatAsChar="false" VertAlign="Top" VertOffset="0" VertRelTo="Para"/>
  <OUTSIDEMARGIN Bottom="283" Left="283" Right="283" Top="283"/>
</SHAPEOBJECT>
<INSIDEMARGIN Bottom="141" Left="510" Right="510" Top="141"/>"""
        
        # 행과 셀 생성
        for row_idx, row in enumerate(rows):
            hwpml += f"\n<ROW>"
            
            # 테두리 스타일 결정
            if row_idx == 0:
                border_fill_id = 3  # 첫 번째 행: 위/아래 실선
            elif row_idx == row_count - 1:
                border_fill_id = 4  # 마지막 행: 위 점선, 아래 실선
            else:
                border_fill_id = 6  # 중간 행: 위/아래 점선
            
            for cell_idx, cell in enumerate(row):
                hwpml += f"""
<CELL BorderFill="{border_fill_id}" ColAddr="{cell_idx}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="{str(cell.get('is_header', False)).lower()}" Height="282" Protect="false" RowAddr="{row_idx}" RowSpan="1" Width="{cell_width}">
  <CELLMARGIN Bottom="141" Left="510" Right="510" Top="141"/>
  <PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
    <P ParaShape="0" Style="0">
      <TEXT CharShape="0"><CHAR>{cell['content']}</CHAR></TEXT>
    </P>
  </PARALIST>
</CELL>"""
            
            hwpml += f"\n</ROW>"
        
        hwpml += "\n</TABLE><CHAR/></TEXT></P>"
        return hwpml
    
    def _create_default_hwpml(self, element):
        """기본 HWPML 요소 생성"""
        element_type = element['type']
        content = element.get('content', '')
        
        # 요소 유형에 따른 기본 스타일 적용
        if element_type in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element_type[1])
            para_shape = "0"
            char_shape = str(level)
        elif element_type == 'p':
            para_shape = "0"
            char_shape = "1"
        elif element_type == 'strong':
            para_shape = "0"
            char_shape = "8"  # 굵은 텍스트 기본 스타일
        elif element_type == 'em':
            para_shape = "0"
            char_shape = "9"  # 기울임 텍스트 기본 스타일
        else:
            para_shape = "0"
            char_shape = "0"
        
        return f'<P ParaShape="{para_shape}" Style="0"><TEXT CharShape="{char_shape}"><CHAR>{content}</CHAR></TEXT></P>'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("마크다운 → HWP 변환기")
        self.setGeometry(100, 100, 600, 400)
        
        self.converter = HWPMLConverter()
        self.template_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        # 중앙 위젯 및 레이아웃 생성
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 텍스트 편집 영역 생성
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("여기에 마크다운 텍스트를 붙여넣거나 클립보드에서 불러오세요")
        self.layout.addWidget(self.text_edit)
        
        # 버튼 레이아웃
        self.button_layout = QHBoxLayout()
        
        # 버튼 추가
        self.template_button = QPushButton("템플릿 선택")
        self.clipboard_button = QPushButton("클립보드에서 불러오기")
        self.save_button = QPushButton("출력 경로 선택")
        self.convert_button = QPushButton("변환")
        
        self.button_layout.addWidget(self.template_button)
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.convert_button)
        
        self.layout.addLayout(self.button_layout)
        
        # 상태 표시줄
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")
        
        # 신호 연결
        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.save_button.clicked.connect(self.select_output_path)
        self.convert_button.clicked.connect(self.convert)
        
        # 변수 초기화
        self.output_path = ""
        
    def select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "템플릿 파일 선택", "", "HWP 파일 (*.hml)")
        if file_path:
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            if success:
                self.status_bar.showMessage(f"템플릿 로드 완료: {file_path}")
            else:
                self.status_bar.showMessage("템플릿 로드 오류")
    
    def load_from_clipboard(self):
        clipboard = QApplication.clipboard()
        md_text = clipboard.text()
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_bar.showMessage("클립보드에서 텍스트 로드 완료")
        else:
            self.status_bar.showMessage("클립보드에 텍스트 없음")
    
    def select_output_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "HWP 파일 저장", "", "HWP 파일 (*.hml)")
        if file_path:
            self.output_path = file_path
            self.status_bar.showMessage(f"출력 경로 설정: {file_path}")
    
    def convert(self):
        if not self.template_path:
            self.status_bar.showMessage("오류: 먼저 템플릿을 선택하세요")
            return
        
        if not self.output_path:
            self.status_bar.showMessage("오류: 출력 경로를 선택하세요")
            return
        
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_bar.showMessage("오류: 변환할 텍스트가 없습니다")
            return
        
        self.status_bar.showMessage("변환 중...")
        
        try:
            # YAML 프론트매터 확인
            title = "제목 없음"
            author = "작성자 없음"
            date = "날짜 없음"
            
            # 제목, 작성자, 날짜 찾기
            t = re.search(r"(?<=title: ).*", md_text)
            a = re.search(r"(?<=author: ).*", md_text)
            d = re.search(r"(?<=date: ).*", md_text)
            
            if t:
                title = t.group(0).strip()
            if a:
                author = a.group(0).strip()
            if d:
                date = d.group(0).strip()
            
            # YAML 프론트매터 제거
            md_text = re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)
            
            # 마크다운을 HWPML로 변환
            hwpml_content = self.converter.convert_md_to_hwpml(md_text, title, author, date)
            
            # 결과 저장
            with io.open(self.output_path, "w", encoding="utf-8") as f:
                f.write(hwpml_content)
            
            self.status_bar.showMessage(f"변환 완료: {self.output_path}")
            
        except Exception as e:
            self.status_bar.showMessage(f"변환 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
