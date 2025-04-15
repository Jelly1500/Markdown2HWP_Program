"""
마크다운 텍스트를 구조화된 요소로 파싱하는 모듈
"""
import re
import mistune
from bs4 import BeautifulSoup, NavigableString

class MarkdownParser:
    """마크다운 텍스트를 구조화된 요소로 파싱하는 클래스"""
    
    def __init__(self):
        self.parser = mistune
    
    def parse(self, md_text):
        """마크다운을 HTML로 변환 후 구조화된 요소로 파싱"""
        html = self.parser.html(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        return self._extract_markdown_elements(soup)
    
    def extract_metadata(self, md_text):
        """마크다운에서 메타데이터 추출 (제목, 작성자, 날짜)"""
        metadata = {
            'title': "제목 없음",
            'author': "작성자 없음",
            'date': "날짜 없음"
        }
        
        title_match = re.search(r"(?<=title: ).*", md_text)
        author_match = re.search(r"(?<=author: ).*", md_text)
        date_match = re.search(r"(?<=date: ).*", md_text)
        
        if title_match:
            metadata['title'] = title_match.group(0).strip()
        if author_match:
            metadata['author'] = author_match.group(0).strip()
        if date_match:
            metadata['date'] = date_match.group(0).strip()
            
        return metadata
    
    def remove_metadata_section(self, md_text):
        """마크다운에서 YAML 메타데이터 섹션 제거"""
        return re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)
    
    def _split_heading_number(self, text):
        """
        제목에서 문단 번호와 실제 제목 텍스트를 분리.
        예: '1.1 예제' → ('1.1', '예제')
        """
        match = re.match(r'^\s*(\d+(?:[.-]\d+)*)(?:[).]?)\s*(.+)$', text)
        if match:
            return match.group(1), match.group(2).strip()
        else:
            return None, text.strip()

    def _extract_markdown_elements(self, soup):
        """HTML soup에서 마크다운 요소 추출"""
        elements = []
        
        for tag in soup.find_all(True, recursive=False):
            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading_num, heading_text = self._split_heading_number(tag.get_text())
                elements.append({
                    'type': tag.name,
                    'content': heading_text,
                    'number': heading_num  # ex) "1.2.3" 등
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