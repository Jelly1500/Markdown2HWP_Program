"""
마크다운 텍스트를 구조화된 요소로 파싱하는 모듈
"""
import re
import logging
from typing import List, Dict, Any, Optional
import mistune
import emoji
from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)


class MarkdownParser:
    """마크다운 텍스트를 구조화된 요소로 파싱하는 클래스"""

    def __init__(self, debug: bool = False):
        """
        Args:
            debug: True일 경우 변환된 HTML을 파일로 저장
        """
        # 테이블, 취소선 등의 플러그인 활성화
        self.parser = mistune.create_markdown(
            plugins=['table', 'strikethrough', 'url', 'task_lists']
        )
        self.debug = debug

    def _remove_emojis(self, text: str) -> str:
        """emoji 라이브러리를 사용하여 주어진 텍스트에서 이모티콘을 제거합니다."""
        return emoji.replace_emoji(text, replace='')

    def _process_reference_links(self, md_text: str) -> str:
        """Reference Link 형식([텍스트][번호])을 인라인 링크로 변환"""
        reference_pattern = r'^\[(\d+)\]:\s*(.+)$'
        references = {}
        
        lines = md_text.split('\n')
        processed_lines = []
        
        # 1단계: Reference Link 정의 수집
        for line in lines:
            match = re.match(reference_pattern, line.strip())
            if match:
                ref_id = match.group(1)
                url = match.group(2).strip()
                references[ref_id] = url
            else:
                processed_lines.append(line)
        
        # 2단계: Reference Link 사용을 인라인 링크로 변환
        def replace_reference_link(match):
            text = match.group(1)
            ref_id = match.group(2)
            if ref_id in references:
                return f'[{text}]({references[ref_id]})'
            logger.warning(f"Reference [{ref_id}] not found for text: {text}")
            return match.group(0)
        
        reference_link_pattern = r'\[([^\]]+)\]\[(\d+)\]'
        result_lines = [
            re.sub(reference_link_pattern, replace_reference_link, line)
            for line in processed_lines
        ]
        
        return '\n'.join(result_lines)

    def parse(self, md_text: str) -> List[Dict[str, Any]]:
        """
        마크다운을 HTML로 변환 후 구조화된 요소로 파싱
        
        Args:
            md_text: 파싱할 마크다운 텍스트
            
        Returns:
            구조화된 요소 리스트
            
        Raises:
            ValueError: 유효하지 않은 마크다운 입력
        """
        if not md_text or not md_text.strip():
            return []
        
        try:
            # 1. 파싱 전 이모티콘 제거
            md_text_no_emojis = self._remove_emojis(md_text)
            
            # 2. Reference Link 처리
            processed_md_text = self._process_reference_links(md_text_no_emojis)
            
            # 3. HTML로 변환
            html = self.parser(processed_md_text)

            # 4. 디버깅 모드일 때만 HTML 파일 저장
            if self.debug:
                try:
                    with open("converted.html", "w", encoding="utf-8") as f:
                        f.write(html)
                except IOError as e:
                    logger.error(f"Failed to write debug HTML file: {e}")

            # 5. HTML 파싱 및 요소 추출
            soup = BeautifulSoup(html, 'html.parser')
            return self._extract_markdown_elements(soup)
            
        except Exception as e:
            logger.error(f"Failed to parse markdown: {e}")
            raise ValueError(f"마크다운 파싱 실패: {e}")

    def extract_metadata(self, md_text: str) -> Dict[str, str]:
        """마크다운에서 메타데이터 추출 (제목, 작성자, 날짜)"""
        metadata = {
            'title': "제목 없음",
            'author': "작성자 없음",
            'date': "날짜 없음"
        }
        
        patterns = {
            'title': r"(?<=title: ).*",
            'author': r"(?<=author: ).*",
            'date': r"(?<=date: ).*"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, md_text)
            if match:
                metadata[key] = match.group(0).strip()
            
        return metadata
    
    def remove_metadata_section(self, md_text: str) -> str:
        """마크다운에서 YAML 메타데이터 섹션 제거"""
        return re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)
    
    def _extract_markdown_elements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """HTML soup에서 마크다운 요소 추출"""
        elements = []
        
        for tag in soup.find_all(True, recursive=False):
            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                elements.append({
                    'type': tag.name,
                    'content': tag.get_text()
                })
            elif tag.name == 'blockquote':
                elements.append({
                    'type': 'blockquote',
                    'content': tag.get_text(),
                    'has_formatting': True,
                    'fragments': self._extract_blockquote_fragments(tag)
                })
            elif tag.name == 'p':
                has_formatting = bool(tag.find(['strong', 'b', 'em', 'i', 'a', 'br', 'code', 'del']))
                element = {
                    'type': 'p',
                    'content': tag.get_text(),
                    'has_formatting': has_formatting
                }
                if has_formatting:
                    element['fragments'] = self._extract_paragraph_fragments(tag)
                elements.append(element)
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
            elif tag.name == 'pre':
                elements.append({
                    'type': 'code',
                    'content': tag.get_text(separator='\n', strip=False)
                })
        
        return elements
    
    def _should_preserve_space(self, sibling, position: str) -> bool:
        """
        인접 요소와의 공백 보존 여부 확인
        
        Args:
            sibling: 인접 형제 요소
            position: 'before' 또는 'after'
        """
        if not sibling or not isinstance(sibling, NavigableString):
            return False
        
        text = str(sibling)
        if not text:
            return False
        
        if position == 'before':
            return text[-1].isspace()
        elif position == 'after':
            return text[0].isspace()
        
        return False
    
    def _extract_inline_element(self, child: Tag, include_href: bool = False) -> Dict[str, Any]:
        """
        인라인 요소(strong, em, a 등)를 추출하고 공백을 보존
        
        Args:
            child: 추출할 태그
            include_href: 링크의 경우 href 포함 여부
        """
        element_type = child.name if child.name != 'b' else 'strong'
        if child.name == 'i':
            element_type = 'em'
        
        # 공백 처리는 더 이상 필요하지 않음 (이미 텍스트에 포함)
        content = child.get_text()
        
        result = {'type': element_type, 'content': content}
        if include_href and child.name == 'a':
            result['href'] = child.get('href', '')
        
        return result
    
    def _extract_paragraph_fragments(self, p_tag: Tag) -> List[Dict[str, Any]]:
        """단락 내 텍스트와 강조 요소를 조각으로 추출하면서 공백 보존"""
        fragments = []

        for child in p_tag.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text:
                    fragments.append({'type': 'text', 'content': text})
            elif child.name in ['strong', 'b', 'em', 'i']:
                fragments.append(self._extract_inline_element(child))
            elif child.name == 'a':
                fragments.append(self._extract_inline_element(child, include_href=True))
            elif child.name == 'code':
                fragments.append({'type': 'code', 'content': child.get_text()})
            elif child.name == 'del':
                fragments.append({'type': 'del', 'content': child.get_text()})
            elif child.name == 'br':
                fragments.append({'type': 'br'})

        return fragments
    
    def _extract_blockquote_fragments(self, blockquote_tag: Tag) -> List[Dict[str, Any]]:
        """인용문 태그에서 단락들을 추출하고 각 단락에서 프래그먼트를 추출"""
        fragments = []
        p_tags = blockquote_tag.find_all('p', recursive=False)
        
        if not p_tags:
            return self._extract_paragraph_fragments(blockquote_tag)
            
        for i, p_tag in enumerate(p_tags):
            fragments.extend(self._extract_paragraph_fragments(p_tag))
            if i < len(p_tags) - 1:
                fragments.append({'type': 'br'})
        
        return fragments
    
    def _extract_list_items(self, list_tag: Tag, level: int = 0) -> List[Dict[str, Any]]:
        """
        리스트 항목 추출 (재귀적으로 중첩 리스트 처리)
        
        Args:
            list_tag: ul 또는 ol 태그
            level: 중첩 레벨 (0부터 시작)
        """
        items = []
        is_ordered = list_tag.name == 'ol'
        
        # ol 태그의 start 속성 추출
        start_value = 1
        if is_ordered:
            try:
                start_value = int(list_tag.get('start', 1))
            except (ValueError, TypeError):
                start_value = 1
        
        current_value = start_value
        
        for li in list_tag.find_all('li', recursive=False):
            item_fragments = []
            nested_lists = []
            
            for child in li.children:
                if isinstance(child, NavigableString):
                    text = str(child) if level == 0 else str(child).strip()
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
                elif child.name in ['strong', 'b', 'em', 'i']:
                    item_fragments.append(self._extract_inline_element(child))
                elif child.name == 'a':
                    item_fragments.append(self._extract_inline_element(child, include_href=True))
                elif child.name == 'code':
                    item_fragments.append({'type': 'code', 'content': child.get_text()})
                elif child.name == 'del':
                    item_fragments.append({'type': 'del', 'content': child.get_text()})
                elif child.name == 'br':
                    item_fragments.append({'type': 'br'})
                elif child.name in ['ul', 'ol']:
                    nested_lists.append(child)
                else:
                    text = child.get_text() if level == 0 else child.get_text().strip()
                    if text:
                        item_fragments.append({'type': 'text', 'content': text})
            
            # 빈 li 태그에 중첩 리스트만 있는 경우
            if not item_fragments and nested_lists:
                for nested_list in nested_lists:
                    nested_items = self._extract_list_items(nested_list, level)
                    items.extend(nested_items)
            else:
                item_info = {
                    'fragments': item_fragments,
                    'is_ordered': is_ordered,
                    'level': level,
                    'start_value': current_value if is_ordered else None
                }
                
                if nested_lists:
                    item_info['nested_items'] = []
                    for nested_list in nested_lists:
                        nested_items = self._extract_list_items(nested_list, level + 1)
                        item_info['nested_items'].extend(nested_items)
                
                items.append(item_info)
                if is_ordered:
                    current_value += 1
        
        return items
    
    def _extract_table_rows(self, table_tag: Tag) -> List[List[Dict[str, Any]]]:
        """표 행과 셀 데이터 추출"""
        rows = []
        
        # 헤더 처리
        thead = table_tag.find('thead')
        if thead:
            for tr in thead.find_all('tr'):
                row = [
                    {'content': th.get_text(), 'is_header': True}
                    for th in tr.find_all('th')
                ]
                if row:
                    rows.append(row)
        
        # 본문 처리
        tbody = table_tag.find('tbody') or table_tag
        for tr in tbody.find_all('tr'):
            row = [
                {'content': td.get_text(), 'is_header': False}
                for td in tr.find_all('td')
            ]
            if row:
                rows.append(row)
        
        return rows