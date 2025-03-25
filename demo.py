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
        
        # 특별 서식 ID를 저장할 딕셔너리
        self.special_formats = {}
        
        # 순서대로 매핑할 마크다운 요소 목록 (strong, em, a 제거)
        self.style_mapping_order = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul'
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
            
            # 템플릿에서 서식 구조 추출
            self._extract_template_styles()
            
            # CharShape 추출 및 특별 서식 복제
            self.special_formats = self._extract_and_clone_charshapes()
            
            # 테이블용 테두리 스타일 추가
            self.table_border_fills = {'header': "3", 'footer': "4", 'body': "6"}  # 기본값
            self.add_table_borderfills()  # 테이블 테두리 추가 및 ID 갱신
        
            return True
        except Exception as e:
            print(f"템플릿 로드 오류: {e}")
            return False
    
    def _clone_and_add_formatting(self, base_charshape, new_id, formatting_tags):
        """기본 CharShape을 복제하고 서식 태그를 추가하여 새 CharShape 생성"""
        soup = BeautifulSoup(features='xml')
        
        # 새 CharShape 태그 생성
        new_charshape = soup.new_tag("CHARSHAPE")
        
        # 기존 CharShape의 모든 속성 복사
        for attr, value in base_charshape.attrs.items():
            new_charshape[attr] = value
        
        # 새로운 ID 할당
        new_charshape['Id'] = new_id
        
        # 서식 태그 추가
        for tag in formatting_tags:
            if isinstance(tag, dict):
                # 속성이 있는 태그 추가
                new_tag = soup.new_tag(tag.pop('tag'))
                for attr, value in tag.items():
                    new_tag[attr] = value
                new_charshape.append(new_tag)
            else:
                # 일반 서식 태그 추가
                new_tag = soup.new_tag(tag)
                new_charshape.append(new_tag)

        # 기존 CharShape의 자식 요소 복사
        for child in base_charshape.children:
            if isinstance(child, NavigableString):
                new_charshape.append(child.copy())
            else:
                new_child = soup.new_tag(child.name)
                for attr, value in child.attrs.items():
                    new_child[attr] = value
                new_charshape.append(new_child)
        
        return new_charshape

    def _extract_and_clone_charshapes(self):
        """템플릿에서 CharShape을 추출하고 특별 서식이 적용된 복제본 생성"""
        soup = BeautifulSoup(self.template_content, 'xml')

        # HWPML 문서의 CHARSHAPE 찾기 - 경로 수정
        docinfo = soup.find('MAPPINGTABLE')
        if not docinfo:
            raise ValueError("템플릿에 DOCINFO 섹션이 없습니다")

        charshapepool = docinfo.find('CHARSHAPELIST')
        if not charshapepool:
            raise ValueError("템플릿에 CHARSHAPEPOOL 섹션이 없습니다")

        # 모든 CharShape 요소 가져오기
        charshapes = charshapepool.find_all('CHARSHAPE')
        if not charshapes:
            raise ValueError("템플릿에 CHARSHAPE 정의가 없습니다")

        # 일반 단락과 리스트의 CharShape ID 찾기
        base_charshape_id = self.template_styles.get('p', {}).get('char_shape') or self.template_styles.get('ul', {}).get('char_shape')
        base_charshape = next((cs for cs in charshapes if cs.get('Id') == base_charshape_id), None)

        if base_charshape is None:
            print(f"경고: ID {base_charshape_id}에 해당하는 CHARSHAPE을 찾을 수 없습니다. 첫 번째 CHARSHAPE을 사용합니다.")
            base_charshape = charshapes[0]

        # 새로운 CharShape ID 생성
        last_id = max(int(cs.get('Id', '0')) for cs in charshapes)

        # 특별 서식 정의를 위한 새로운 CharShape 복제
        special_formats = {
            'strong': str(last_id + 1),      # 굵게
            'em': str(last_id + 2),          # 기울임
            'underline': str(last_id + 3),   # 밑줄
            'strong_em': str(last_id + 4),   # 굵게+기울임
            'strong_underline': str(last_id + 5),  # 굵게+밑줄
            'em_underline': str(last_id + 6),      # 기울임+밑줄
            'strong_em_underline': str(last_id + 7)  # 굵게+기울임+밑줄
        }

        # 굵게 스타일 CharShape 복제
        strong_charshape = self._clone_charshape(base_charshape, special_formats['strong'])
        bold_tag = soup.new_tag("BOLD")
        strong_charshape.append(bold_tag)
        charshapepool.append(strong_charshape)

        # 기울임 스타일 CharShape 복제
        em_charshape = self._clone_charshape(base_charshape, special_formats['em'])
        italic_tag = soup.new_tag("ITALIC")
        em_charshape.append(italic_tag)
        charshapepool.append(em_charshape)

        # 밑줄 스타일 CharShape 복제
        underline_charshape = self._clone_charshape(base_charshape, special_formats['underline'])
        underline_tag = soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")
        underline_charshape.append(underline_tag)
        charshapepool.append(underline_charshape)

        # 굵게+기울임 스타일 CharShape 복제
        strong_em_charshape = self._clone_charshape(base_charshape, special_formats['strong_em'])
        strong_em_charshape.append(soup.new_tag("BOLD"))
        strong_em_charshape.append(soup.new_tag("ITALIC"))
        charshapepool.append(strong_em_charshape)

        # 굵게+밑줄 스타일 CharShape 복제
        strong_underline_charshape = self._clone_charshape(base_charshape, special_formats['strong_underline'])
        strong_underline_charshape.append(soup.new_tag("BOLD"))
        strong_underline_charshape.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom"))
        charshapepool.append(strong_underline_charshape)

        # 기울임+밑줄 스타일 CharShape 복제
        em_underline_charshape = self._clone_charshape(base_charshape, special_formats['em_underline'])
        em_underline_charshape.append(soup.new_tag("ITALIC"))
        em_underline_charshape.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom"))
        charshapepool.append(em_underline_charshape)

        # 굵게+기울임+밑줄 스타일 CharShape 복제
        all_formats_charshape = self._clone_charshape(base_charshape, special_formats['strong_em_underline'])
        all_formats_charshape.append(soup.new_tag("BOLD"))
        all_formats_charshape.append(soup.new_tag("ITALIC"))
        all_formats_charshape.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom"))
        charshapepool.append(all_formats_charshape)

        # 템플릿 내용 업데이트
        self.template_content = str(soup)

        return special_formats

    def _clone_charshape(self, base_charshape, new_id):
        """CharShape 요소를 복제하고 새 ID 할당"""
        soup = BeautifulSoup(features='xml')
        
        # 새 CharShape 태그 생성
        new_charshape = soup.new_tag("CHARSHAPE")
        
        # 모든 속성 복사
        for attr, value in base_charshape.attrs.items():
            new_charshape[attr] = value
        
        # ID 업데이트
        new_charshape['Id'] = new_id
        
        # 모든 하위 요소 복사 (BOLD, ITALIC, UNDERLINE 등 제외)
        for child in base_charshape.children:
            if isinstance(child, NavigableString):
                new_charshape.append(child.copy())
            else:
                # 기존 서식 태그는 복사하지 않음 (새로 추가할 예정)
                if child.name not in ['BOLD', 'ITALIC', 'UNDERLINE']:
                    new_child = soup.new_tag(child.name)
                    for attr, value in child.attrs.items():
                        new_child[attr] = value
                    for grandchild in child.children:
                        if isinstance(grandchild, NavigableString):
                            new_child.append(grandchild.copy())
                        else:
                            new_grandchild = soup.new_tag(grandchild.name)
                            for attr, value in grandchild.attrs.items():
                                new_grandchild[attr] = value
                            new_child.append(new_grandchild)
                    new_charshape.append(new_child)
        
        return new_charshape

    
    def _extract_template_styles(self):
        """템플릿에서 순서대로 서식 스타일 추출"""
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
    
    def _extract_bullet_symbol(self, structure):
        """순서 없는 리스트 구조에서 글머리표 특수기호 추출"""
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
        match = char_pattern.search(structure)
        
        if match:
            content = match.group(1).strip()
            if content and not content[0].isalnum():
                bullet_parts = re.match(r'([^\w\s]+)(\s*)(.*)', content)
                if bullet_parts:
                    return bullet_parts.group(1)
        return None
    
    def _extract_balanced_p_tags(self, content):
        """균형 잡힌 P 태그 쌍을 순서대로 추출"""
        elements = []
        start_idx = 0
        
        while True:
            p_start = content.find('<P ', start_idx)
            if p_start == -1:
                break
            
            open_tags = 1
            close_tags = 0
            search_idx = p_start + 2
            
            while open_tags > close_tags and search_idx < len(content):
                next_open = content.find('<P ', search_idx)
                next_close = content.find('</P>', search_idx)
                
                if next_close == -1:
                    break
                
                if next_open != -1 and next_open < next_close:
                    open_tags += 1
                    search_idx = next_open + 2
                else:
                    close_tags += 1
                    search_idx = next_close + 4
            
            if open_tags == close_tags:
                element = content[p_start:search_idx]
                elements.append(element)
                start_idx = search_idx
            else:
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
        
        html = mistune.html(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        md_elements = self._extract_markdown_elements(soup)
        hwpml_body = self._convert_elements_to_hwpml(md_elements)
        
        result = re.sub(
            r'<BODY>.*?<SECTION Id="0">(.*?)</SECTION>.*?</BODY>',
            f'<BODY><SECTION Id="0">{hwpml_body}</SECTION></BODY>',
            self.template_content,
            flags=re.DOTALL
        )
        
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
                if tag.find(['strong', 'b', 'em', 'i', 'a']):
                    elements.append({
                        'type': 'p',
                        'content': tag.get_text(),
                        'has_formatting': True,
                        'fragments': self._extract_paragraph_fragments(tag)
                    })
                else:
                    elements.append({
                        'type': 'p',
                        'content': tag.get_text(),
                        'has_formatting': False
                    })
            elif tag.name in ['ul', 'ol']:
                elements.append({
                    'type': 'ul',
                    'items': self._extract_list_items(tag),
                    'is_ordered': tag.name == 'ol'
                })
            elif tag.name == 'table':
                elements.append({
                    'type': 'table',
                    'rows': self._extract_table_rows(tag)
                })
        
        return elements
    
    def _extract_paragraph_fragments(self, p_tag):
        """단락 내 텍스트와 강조 요소를 조각으로 추출하면서 공백 보존"""
        fragments = []

        for child in p_tag.children:
            if isinstance(child, NavigableString):
                text = str(child)  # 공백을 포함한 원본 텍스트 유지
                if text:  # 빈 문자열이 아니면 추가
                    fragments.append({'type': 'text', 'content': text})
            elif child.name in ['strong', 'b']:
                # 앞뒤 공백 확인 및 보존
                prev_space = ''
                next_space = ''

                # 앞쪽 공백 확인
                if child.previous_sibling and isinstance(child.previous_sibling, NavigableString):
                    prev_text = str(child.previous_sibling)
                    if prev_text and prev_text[-1].isspace():
                        # 이미 앞 텍스트에 공백이 있으므로 여기서는 추가하지 않음
                        prev_space = ''

                # 뒤쪽 공백 확인
                if child.next_sibling and isinstance(child.next_sibling, NavigableString):
                    next_text = str(child.next_sibling)
                    if next_text and next_text[0].isspace():
                        # 이미 뒤 텍스트에 공백이 있으므로 여기서는 추가하지 않음
                        next_space = ''

                fragments.append({'type': 'strong', 'content': prev_space + child.get_text() + next_space})
            elif child.name in ['em', 'i']:
                # 기울임체도 동일하게 처리
                prev_space = ''
                next_space = ''

                if child.previous_sibling and isinstance(child.previous_sibling, NavigableString):
                    prev_text = str(child.previous_sibling)
                    if prev_text and prev_text[-1].isspace():
                        prev_space = ''

                if child.next_sibling and isinstance(child.next_sibling, NavigableString):
                    next_text = str(child.next_sibling)
                    if next_text and next_text[0].isspace():
                        next_space = ''

                fragments.append({'type': 'em', 'content': prev_space + child.get_text() + next_space})
            elif child.name == 'a':
                # 링크도 동일하게 처리
                prev_space = ''
                next_space = ''

                if child.previous_sibling and isinstance(child.previous_sibling, NavigableString):
                    prev_text = str(child.previous_sibling)
                    if prev_text and prev_text[-1].isspace():
                        prev_space = ''

                if child.next_sibling and isinstance(child.next_sibling, NavigableString):
                    next_text = str(child.next_sibling)
                    if next_text and next_text[0].isspace():
                        next_space = ''

                fragments.append({
                    'type': 'a', 
                    'content': prev_space + child.get_text() + next_space, 
                    'href': child.get('href', '')
                })

        return fragments

    
    def _extract_list_items(self, list_tag):
        """리스트 항목 추출 (공백 보존)"""
        items = []
        is_ordered = list_tag.name == 'ol'
        
        for li in list_tag.find_all('li', recursive=False):
            item_fragments = []
            nested_lists = []
            
            for child in li.children:
                if isinstance(child, NavigableString):
                    text = str(child)  # 공백 보존
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
                elif child.name in ['strong', 'b']:
                    # 앞뒤 공백 보존
                    prev_space = ''
                    next_space = ''
                    
                    if child.previous_sibling and isinstance(child.previous_sibling, NavigableString):
                        prev_text = str(child.previous_sibling)
                        if prev_text and prev_text[-1].isspace():
                            prev_space = ''
                    
                    if child.next_sibling and isinstance(child.next_sibling, NavigableString):
                        next_text = str(child.next_sibling)
                        if next_text and next_text[0].isspace():
                            next_space = ''
                    
                    item_fragments.append({'type': 'strong', 'content': prev_space + child.get_text() + next_space})
                elif child.name in ['em', 'i']:
                    # 기울임체도 동일하게 처리
                    prev_space = ''
                    next_space = ''
                    
                    if child.previous_sibling and isinstance(child.previous_sibling, NavigableString):
                        prev_text = str(child.previous_sibling)
                        if prev_text and prev_text[-1].isspace():
                            prev_space = ''
                    
                    if child.next_sibling and isinstance(child.next_sibling, NavigableString):
                        next_text = str(child.next_sibling)
                        if next_text and next_text[0].isspace():
                            next_space = ''
                    
                    item_fragments.append({'type': 'em', 'content': prev_space + child.get_text() + next_space})
                elif child.name == 'a':
                    # 링크도 동일하게 처리
                    prev_space = ''
                    next_space = ''
                    
                    if child.previous_sibling and isinstance(child.previous_sibling, NavigableString):
                        prev_text = str(child.previous_sibling)
                        if prev_text and prev_text[-1].isspace():
                            prev_space = ''
                    
                    if child.next_sibling and isinstance(child.next_sibling, NavigableString):
                        next_text = str(child.next_sibling)
                        if next_text and next_text[0].isspace():
                            next_space = ''
                    
                    item_fragments.append({
                        'type': 'a', 
                        'content': prev_space + child.get_text() + next_space, 
                        'href': child.get('href', '')
                    })
                elif child.name not in ['ul', 'ol']:
                    text = child.get_text()  # 공백 보존
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
        """중첩 리스트 항목 추출"""
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
        
        thead = table_tag.find('thead')
        if thead:
            for tr in thead.find_all('tr'):
                row = []
                for th in tr.find_all(['th']):
                    row.append({'content': th.get_text(), 'is_header': True})
                if row:
                    rows.append(row)
        
        tbody = table_tag.find('tbody') or table_tag
        for tr in tbody.find_all('tr'):
            row = []
            for td in tr.find_all(['td']):
                row.append({'content': td.get_text(), 'is_header': False})
            if row:
                rows.append(row)
        
        return rows
    
    def _convert_elements_to_hwpml(self, elements):
        """마크다운 요소를 HWPML로 변환"""
        hwpml = ""
        
        for element in elements:
            element_type = element['type']
            template_style = self.template_styles.get(element_type, self.template_styles.get('p'))
            
            if template_style is None:
                hwpml += self._create_default_hwpml(element)
                continue
            
            if element_type in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                hwpml += self._insert_text_into_template(template_style['structure'], element['content'])
            elif element_type == 'p':
                if element.get('has_formatting', False):
                    hwpml += self._convert_formatted_paragraph(element, template_style)
                else:
                    hwpml += self._insert_text_into_template(template_style['structure'], element['content'])
            elif element_type == 'ul':
                hwpml += self._convert_list_to_hwpml(element, template_style)
            elif element_type == 'table':
                hwpml += self._create_default_table_hwpml(element)
        
        return hwpml
    
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
            
            if fragment_type == 'text':
                hwpml += f'<TEXT CharShape="{normal_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'strong':
                # 굵게: 복제된 CharShape 사용
                hwpml += f'<TEXT CharShape="{self.special_formats["strong"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'em':
                # 기울임: 복제된 CharShape 사용
                hwpml += f'<TEXT CharShape="{self.special_formats["em"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'a':
                field_id = str(self.field_id_counter + 1)
                inst_id = str(self.inst_id_counter + 1)
                self.field_id_counter += 1
                self.inst_id_counter += 1
                
                href = fragment.get('href', '').replace('/', '\\/')
                command = f"{href};1;0;0;"
                
                hwpml += f'<TEXT CharShape="{self.special_formats["underline"]}">'
                hwpml += f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'
                hwpml += f'<TEXT CharShape="{self.special_formats["underline"]}"><CHAR>{content}</CHAR></TEXT>'
                hwpml += f'<TEXT CharShape="{self.special_formats["underline"]}">'
                hwpml += f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'
        
        hwpml += '</P>'
        
        return hwpml
    
    def _insert_text_into_template(self, template, text, preserve_prefix=True):
        """
        텍스트를 템플릿의 CHAR 태그 내에 삽입하고, 필요한 경우 셀 너비를 조정하여 줄바꿈을 방지합니다.
        CHAR 태그가 없는 경우에는 TEXT 태그 내의 CHAR 태그를 대상으로 처리합니다.
        """
        import re

        # 최대 테이블 너비 설정
        MAX_TABLE_WIDTH = 42250

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
                    multiplier = min(max(ratio, 1.2), 5.0)  # 최대 3배로 제한
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
            # --- CHAR 태그를 찾지 못한 경우: TEXT 태그 내의 CHAR 태그를 대상으로 처리 ---
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
            prefix = f"{self.bullet_symbol} "

        indent = "  " * level
        hwpml += f'<P {p_attributes}>'

        # 글머리 기호에는 템플릿의 char_shape 사용 (리스트 스타일)
        hwpml += f'<TEXT CharShape="{char_shape}"><CHAR>{indent}{prefix}</CHAR></TEXT>'

        # 텍스트 내용에는 일반 단락 스타일 사용
        p_style = self.template_styles.get('p', {})
        text_char_shape = p_style.get('char_shape', "0")  # 일반 단락 스타일 또는 기본값 "0"

        for fragment in fragments:
            fragment_type = fragment['type']
            content = fragment['content']

            if fragment_type == 'text':
                hwpml += f'<TEXT CharShape="{text_char_shape}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'strong':
                hwpml += f'<TEXT CharShape="{self.special_formats["strong"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'em':
                hwpml += f'<TEXT CharShape="{self.special_formats["em"]}"><CHAR>{content}</CHAR></TEXT>'
            elif fragment_type == 'a':
                # 하이퍼링크 처리 코드...
                field_id = str(self.field_id_counter + 1)
                inst_id = str(self.inst_id_counter + 1)
                self.field_id_counter += 1
                self.inst_id_counter += 1

                href = fragment.get('href', '').replace('/', '\\/')
                command = f"{href};1;0;0;"

                hwpml += f'<TEXT CharShape="{self.special_formats["underline"]}">'
                hwpml += f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'
                hwpml += f'<TEXT CharShape="{self.special_formats["underline"]}"><CHAR>{content}</CHAR></TEXT>'
                hwpml += f'<TEXT CharShape="{self.special_formats["underline"]}">'
                hwpml += f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
                hwpml += '</TEXT>'

        hwpml += '</P>'

        # 중첩 리스트 처리 - 기존 코드와 동일
        if 'nested_items' in item and item['nested_items']:
            nested_counter = {}
            for nested_item in item['nested_items']:
                hwpml += self._process_list_item(nested_item, template, char_shape, top_level_counter, is_top_level=False, counter=nested_counter)

        return hwpml

    def add_table_borderfills(self):
        """테이블용 BORDERFILL 요소를 추가하는 함수"""
        soup = BeautifulSoup(self.template_content, 'xml')

        # BORDERFILLLIST 찾기
        borderfill_list = soup.find('BORDERFILLLIST')
        if not borderfill_list:
            print("BORDERFILLLIST를 찾을 수 없습니다.")
            return False

        # 기존 ID 중 가장 큰 값 찾기
        existing_ids = [int(bf.get('Id', '0')) for bf in borderfill_list.find_all('BORDERFILL')]
        next_id = max(existing_ids) + 1 if existing_ids else 1

        # 테이블용 테두리 스타일 정의 - 유형별 순서 정정
        table_borderfills = [
            # 헤더용 테두리 (상하좌우 모두 실선) - ID: next_id
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false">
            <LEFTBORDER Type="Solid" Width="0.12mm"/>
            <RIGHTBORDER Type="Solid" Width="0.12mm"/>
            <TOPBORDER Type="Solid" Width="0.12mm"/>
            <BOTTOMBORDER Type="Solid" Width="0.12mm"/>
            <DIAGONAL Type="Solid" Width="0.1mm"/>
            </BORDERFILL>""",

            # 마지막 행용 테두리 (상단 점선, 하단 실선) - ID: next_id + 1
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false">
            <LEFTBORDER Type="Solid" Width="0.12mm"/>
            <RIGHTBORDER Type="Solid" Width="0.12mm"/>
            <TOPBORDER Type="Dot" Width="0.3mm"/>
            <BOTTOMBORDER Type="Solid" Width="0.12mm"/>
            <DIAGONAL Type="Solid" Width="0.1mm"/>
            </BORDERFILL>""",

            # 중간 행용 테두리 (상단 실선, 하단 점선) - ID: next_id + 2
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false">
            <LEFTBORDER Type="Solid" Width="0.12mm"/>
            <RIGHTBORDER Type="Solid" Width="0.12mm"/>
            <TOPBORDER Type="Dot" Width="0.3mm"/>
            <BOTTOMBORDER Type="Dot" Width="0.3mm"/>
            <DIAGONAL Type="Solid" Width="0.1mm"/>
            </BORDERFILL>"""
        ]

        # 테이블 테두리 ID 저장 - 명확한 의미 부여
        self.table_border_fills = {
            'header': str(next_id),      # 헤더용 (상하좌우 모두 실선)
            'footer': str(next_id + 1),  # 마지막 행용 (상단 점선, 하단 실선)
            'body': str(next_id + 2)     # 중간 행용 (상단 실선, 하단 점선)
        }

        # BORDERFILL 요소 추가
        for i, bf_template in enumerate(table_borderfills):
            new_id = next_id + i
            bf_soup = BeautifulSoup(bf_template.format(new_id), 'xml')
            borderfill_list.append(bf_soup.find('BORDERFILL'))

        # Count 속성 업데이트
        borderfill_list['Count'] = str(len(borderfill_list.find_all('BORDERFILL')))

        # 템플릿 내용 업데이트
        self.template_content = str(soup)
        return True
    
    def _create_default_table_hwpml(self, table_element):
        """기본 HWPML 표 생성"""
        rows = table_element['rows']
        row_count = len(rows)
        col_count = max(len(row) for row in rows) if rows else 0

        total_table_width = 42250
        cell_width = total_table_width // col_count if col_count > 0 else 21125

        inst_id = self.inst_id_counter
        self.inst_id_counter += 1

        hwpml = f"""<P ParaShape="0" Style="0"><TEXT CharShape="0"> <TABLE BorderFill="{self.table_border_fills['header']}" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="true" RowCount="{row_count}"> <SHAPEOBJECT InstId="{inst_id}" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1"> <SIZE Height="3846" HeightRelTo="Absolute" Protect="false" Width="{total_table_width}" WidthRelTo="Absolute"/> <POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="true" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Column" TreatAsChar="false" VertAlign="Top" VertOffset="0" VertRelTo="Para"/> <OUTSIDEMARGIN Bottom="283" Left="283" Right="283" Top="283"/> </SHAPEOBJECT> <INSIDEMARGIN Bottom="141" Left="510" Right="510" Top="141"/>"""

        for row_idx, row in enumerate(rows):
            hwpml += f"\n<ROW>"

            # 행 위치에 따라 다른 테두리 스타일 적용
            if row_idx == 0:  # 첫번째 행 (헤더)
                border_fill_id = self.table_border_fills['header']
            elif row_idx == row_count - 1:  # 마지막 행
                border_fill_id = self.table_border_fills['footer']
            else:  # 중간 행
                border_fill_id = self.table_border_fills['body']

            for cell_idx, cell in enumerate(row):
                hwpml += f""" <CELL BorderFill="{border_fill_id}" ColAddr="{cell_idx}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="{str(cell.get('is_header', False)).lower()}" Height="282" Protect="false" RowAddr="{row_idx}" RowSpan="1" Width="{cell_width}"> <CELLMARGIN Bottom="141" Left="510" Right="510" Top="141"/> <PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center"> <P ParaShape="0" Style="0"> <TEXT CharShape="0"><CHAR>{cell['content']}</CHAR></TEXT> </P> </PARALIST> </CELL>"""

            hwpml += f"\n</ROW>"

        hwpml += "\n</TABLE><CHAR/></TEXT></P>"

        return hwpml
    
    def _create_default_hwpml(self, element):
        """기본 HWPML 요소 생성"""
        element_type = element['type']
        content = element.get('content', '')
        
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("마크다운 → HWP 변환기")
        self.setGeometry(100, 100, 600, 400)
        
        self.converter = HWPMLConverter()
        self.template_path = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 현재 스크립트의 위치를 기준으로 상대 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # convertedDocs 디렉토리 경로 설정
        output_dir = os.path.join(current_dir, "convertedDocs")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 기본 출력 파일 경로 설정
        self.output_path = os.path.join(output_dir, "converted.hml")
        
        self.layout = QVBoxLayout(self.central_widget)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("여기에 마크다운 텍스트를 붙여넣거나 클립보드에서 불러오세요")
        self.layout.addWidget(self.text_edit)
        
        self.button_layout = QHBoxLayout()
        
        self.template_button = QPushButton("템플릿 선택")
        self.clipboard_button = QPushButton("클립보드에서 불러오기")
        self.save_button = QPushButton("출력 경로 선택")
        self.convert_button = QPushButton("변환")
        
        self.button_layout.addWidget(self.template_button)
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.convert_button)
        
        self.layout.addLayout(self.button_layout)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")
        
        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.save_button.clicked.connect(self.select_output_path)
        self.convert_button.clicked.connect(self.convert)
    
    def select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "템플릿 파일 선택", "", "HWP 파일 (*.hml)")
        if file_path:
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            self.status_bar.showMessage(f"템플릿 로드 완료: {file_path}" if success else "템플릿 로드 오류")
    
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
            title = "제목 없음"
            author = "작성자 없음"
            date = "날짜 없음"
            
            t = re.search(r"(?<=title: ).*", md_text)
            a = re.search(r"(?<=author: ).*", md_text)
            d = re.search(r"(?<=date: ).*", md_text)
            
            if t:
                title = t.group(0).strip()
            if a:
                author = a.group(0).strip()
            if d:
                date = d.group(0).strip()
            
            md_text = re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)
            
            hwpml_content = self.converter.convert_md_to_hwpml(md_text, title, author, date)
            
            with io.open(self.output_path, "w", encoding="utf-8") as f:
                f.write(hwpml_content)
            
            self.status_bar.showMessage(f"변환 완료: {self.output_path}")
            
            # 변환 완료 후 파일 자동 실행
            try:
                os.startfile(self.output_path)
            except Exception as e:
                self.status_bar.showMessage(f"파일을 자동으로 열지 못했습니다: {str(e)}")
        except Exception as e:
            self.status_bar.showMessage(f"변환 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())