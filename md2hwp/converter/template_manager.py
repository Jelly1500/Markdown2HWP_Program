"""
HWPML 템플릿 관리 모듈
"""
import re
from bs4 import BeautifulSoup, NavigableString
from ..config import STYLE_MAPPING_ORDER, DEFAULT_BULLET_SYMBOL, PARAGRAPH_FORMAT_SETTINGS
from .special_char import SpecialCharHandler
import os

class TemplateManager:
    """HWPML 템플릿 관리 클래스"""
    
    def __init__(self):
        self.template_content = None
        self.template_styles = {}
        self.special_formats = {}
        self.list_special_formats = {}
        self.list_special_formats_levels = {}
        # 깊이별 리스트 스타일 저장 (0: 1단, 1: 2단, 2: 3단)
        self.list_level_styles = {}
        self.bullet_symbol_levels = {}
        # 테이블 테두리 영역별 BorderFill ID 매핑
        # 1번째 행: 왼쪽, 가운데, 오른쪽
        # 2번째 행: 왼쪽, 가운데, 오른쪽  
        # 마지막 행: 왼쪽, 가운데, 오른쪽
        # 중간 행: 왼쪽, 가운데, 오른쪽
        self.table_border_fills = {
            'first_row_left': "3",      # 1번째 행 가장 왼쪽
            'first_row_center': "4",    # 1번째 행 가운데
            'first_row_right': "5",     # 1번째 행 가장 오른쪽
            'second_row_left': "6",     # 2번째 행 가장 왼쪽
            'second_row_center': "7",   # 2번째 행 가운데
            'second_row_right': "8",    # 2번째 행 가장 오른쪽
            'last_row_left': "9",       # 마지막 행 가장 왼쪽
            'last_row_center': "10",    # 마지막 행 가운데
            'last_row_right': "11",     # 마지막 행 가장 오른쪽
            'middle_row_left': "12",    # 중간 행 가장 왼쪽
            'middle_row_center': "13",  # 중간 행 가운데
            'middle_row_right': "14"    # 중간 행 가장 오른쪽
        }
        self.style_mapping_order = STYLE_MAPPING_ORDER
        self.bullet_symbol = DEFAULT_BULLET_SYMBOL  # 기본 글머리표
        self.margin_para_shapes = {}
        self.special_char_handler = SpecialCharHandler()
        
        # 편집 용지(SECDEF) 및 단 설정(COLDEF) 보관
        self.sec_def_content = None

        # 문단 형식 설정
        self.paragraph_format_settings = PARAGRAPH_FORMAT_SETTINGS
        self.current_paragraph_format = self.paragraph_format_settings['default_format']
        
        # 기본 템플릿 경로 설정 수정 (빌드된 exe 환경 고려)
        import sys
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller 등으로 빌드된 경우 (.exe)
            base_path = os.path.dirname(sys.executable)
        else:
            # 일반 파이썬 환경에서 실행된 경우 (소스코드)
            # 현재 실행 파일이 담겨 있는 폴더의 상위 폴더를 가리키도록 수정
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.default_template_dir = os.path.join(base_path, "new_template")
        self.default_template_file = os.path.join(self.default_template_dir, "템플릿문서.hml")
        
        # 디버깅을 위한 경로 출력
        print(f"Template Manager 초기화:")
        print(f"Base Path: {base_path}")
        print(f"Default Template Dir: {self.default_template_dir}")
        print(f"Default Template File: {self.default_template_file}")
        print(f"Default Template File Exists: {os.path.exists(self.default_template_file)}")
        
        # 템플릿 디렉토리가 없으면 생성
        if not os.path.exists(self.default_template_dir):
            try:
                os.makedirs(self.default_template_dir, exist_ok=True)
                print(f"템플릿 디렉토리 생성: {self.default_template_dir}")
            except Exception as e:
                print(f"템플릿 디렉토리 생성 실패: {e}")

        self._reset_dynamic_template_caches()
    
    def _reset_dynamic_template_caches(self):
        """Reset caches that depend on the currently loaded template."""
        self.template_styles = {key: None for key in self.style_mapping_order}
        self.special_formats = {}
        self.list_special_formats = {}
        self.list_special_formats_levels = {}
        self.list_level_styles = {}
        self.bullet_symbol_levels = {}
        self.margin_para_shapes = {}
        self.sec_def_content = None
        self.bullet_symbol = DEFAULT_BULLET_SYMBOL

    def load_template(self, template_path):
        """
        템플릿 로드 (BeautifulSoup 기반으로 수정)
        - SECDEF와 실제 내용(표 등)이 한 P 태그에 섞인 경우를 처리하도록 개선
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'xml')

            # BODY 태그 내에서 SECDEF를 포함한 P 태그 검색
            body_tag = soup.find('BODY')
            if not body_tag:
                print("템플릿 로드 오류: BODY 태그를 찾을 수 없습니다.")
                return False

            self._reset_dynamic_template_caches()

            p_tag_with_secdef = next((p for p in body_tag.find_all('P') if p.find('SECDEF')), None)
            
            if p_tag_with_secdef:
                # 1. SECDEF와 COLDEF 태그를 원본 P 태그에서 '추출' (제거하고 반환받음)
                secdef_tag = p_tag_with_secdef.find('SECDEF').extract()
                coldef_tag = p_tag_with_secdef.find('COLDEF')
                if coldef_tag:
                    coldef_tag = coldef_tag.extract()

                # 2. 추출한 태그들을 보관용 새 P 태그에 담기
                clean_p_for_storage = soup.new_tag('P', **p_tag_with_secdef.attrs)
                original_text_tag = p_tag_with_secdef.find('TEXT')
                text_attrs = original_text_tag.attrs if original_text_tag else {}
                new_text_tag = soup.new_tag('TEXT', **text_attrs)
                
                new_text_tag.append(secdef_tag)
                if coldef_tag:
                    new_text_tag.append(coldef_tag)
                new_text_tag.append(soup.new_tag('CHAR', string=' '))
                clean_p_for_storage.append(new_text_tag)
                
                self.sec_def_content = str(clean_p_for_storage)
                print("편집 용지(SECDEF)를 포함한 문단 설정을 성공적으로 분리/정리하여 저장했습니다.")

                # 3. 원본 P 태그에 더 이상 유의미한 내용이 없으면 완전히 제거
                if not p_tag_with_secdef.get_text(strip=True) and not p_tag_with_secdef.find(['TABLE', 'PICTURE']):
                    p_tag_with_secdef.decompose()
                    print("내용이 없는 SECDEF 문단을 완전히 제거했습니다.")
            
            # 이제 soup 객체는 SECDEF/COLDEF가 깔끔하게 분리된 상태
            # 템플릿 내의 모든 <TAB/> 태그를 공백 4개로 치환
            self._replace_tab_tags_in_soup(soup)
            
            self._extract_template_styles(soup)
            self._extract_and_clone_charshapes(soup)
            self.add_table_borderfills(soup)
            self.template_content = str(soup)
            
            return True
        except Exception as e:
            print(f"템플릿 로드 오류: {e}")
            return False
    
    def _replace_tab_tags_in_soup(self, soup):
        """BeautifulSoup 객체 내의 모든 <TAB/> 태그를 공백 4개로 치환"""
        # 모든 CHAR 태그를 찾아서 내용을 확인하고 <TAB/> 태그를 치환
        for char_tag in soup.find_all('CHAR'):
            if char_tag.string and '<TAB/>' in char_tag.string:
                char_tag.string = char_tag.string.replace('<TAB/>', '    ')
        
        # TEXT 태그 내의 텍스트 노드에서도 <TAB/> 태그를 치환
        for text_tag in soup.find_all('TEXT'):
            for content in text_tag.contents:
                if hasattr(content, 'string') and content.string and '<TAB/>' in content.string:
                    content.string = content.string.replace('<TAB/>', '    ')
    
    def _extract_template_styles(self, soup):
        """템플릿에서 순서대로 서식 스타일 추출"""
        body_section = soup.find('BODY')
        if not body_section:
            raise ValueError("템플릿에 BODY 섹션이 없습니다")
        
        section = body_section.find('SECTION')
        if not section:
            raise ValueError("템플릿에 SECTION 요소가 없습니다")
        
        # 모든 균형 잡힌 P 태그 구조 순서대로 추출
        balanced_p_tags = self._extract_balanced_p_tags(str(section))
        
        # 서식 스타일 매핑 초기화
        self.template_styles = {key: None for key in self.style_mapping_order}
        
        # Populate list styles using sample paragraphs inside the section
        self._populate_list_sample_styles(section)
        
        # 순서대로 마크다운 요소에 매핑
        for idx, tag_structure in enumerate(balanced_p_tags):
            if idx < len(self.style_mapping_order):
                style_key = self.style_mapping_order[idx]

                if self.template_styles.get(style_key):
                    continue

                # 특수 문자 자동 번호가 있는지 확인
                has_special_char_numbering = False
                char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
                matches = char_pattern.finditer(tag_structure)
                for match in matches:
                    content = match.group(1)
                    for char in content:
                        if self.special_char_handler.identify_special_char(char):
                            has_special_char_numbering = True
                            break
                    if has_special_char_numbering:
                        break

                # 구조에서 <TAB/> 태그를 공백 4개로 치환
                cleaned_tag_structure = tag_structure.replace('<TAB/>', '    ')
                
                self.template_styles[style_key] = {
                    'structure': cleaned_tag_structure,
                    'para_shape': self._extract_para_shape(tag_structure),
                    'char_shape': self._extract_char_shape(tag_structure),
                    'has_table': '<TABLE' in tag_structure,
                    'has_field': '<FIELDBEGIN' in tag_structure,
                    'has_special_char_numbering': has_special_char_numbering
                }
                
                # 순서 없는 리스트에서 글머리표 추출 (깊이별: ul1, ul2, ul3)
                if style_key.startswith('ul'):
                    text_matches = re.findall(r'<TEXT CharShape="(\d+)">', tag_structure)
                    bullet_char_shape = self._extract_char_shape(tag_structure)
                    text_char_shape = self._extract_char_shape(tag_structure)
                    if len(text_matches) >= 2:
                        bullet_char_shape = text_matches[0]
                        text_char_shape = text_matches[1]
                    self.template_styles[style_key]['bullet_char_shape'] = bullet_char_shape
                    self.template_styles[style_key]['text_char_shape'] = text_char_shape

                    # 레벨 인덱스 계산 (ul1->0, ul2->1, ul3->2)
                    try:
                        level_index = int(style_key.replace('ul', '')) - 1
                    except Exception:
                        level_index = 0

                    self.list_level_styles[level_index] = {
                        'structure': cleaned_tag_structure,
                        'para_shape': self.template_styles[style_key]['para_shape'],
                        'bullet_char_shape': bullet_char_shape,
                        'text_char_shape': text_char_shape
                    }

                    bullet = self._extract_bullet_symbol(tag_structure)
                    if bullet:
                        self.bullet_symbol_levels[level_index] = bullet
                    else:
                        # 기본값 사용
                        self.bullet_symbol_levels.setdefault(level_index, DEFAULT_BULLET_SYMBOL)
    
    def _extract_bullet_symbol(self, structure):
        """순서 없는 리스트 구조에서 글머리표 특수기호 추출"""
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>', re.DOTALL)
        match = char_pattern.search(structure)

        if not match:
            return None

        content = match.group(1)
        # <TAB/> 태그를 공백 4개로 치환한 후 다른 inline 태그 제거
        content = content.replace('<TAB/>', '    ')
        content = re.sub(r'<[^>]+>', '', content)
        content = content.strip()

        if not content:
            return None

        match_symbol = re.match(r'[^\w\s]+', content)
        if match_symbol:
            return match_symbol.group(0)

        return None

    def _populate_list_sample_styles(self, section):
        """Populate list level styles by sampling bullet paragraphs in the template section."""
        if not section:
            return

        bullet_candidates = []

        for p in section.find_all('P'):
            text = p.get_text()
            if not text:
                continue
            stripped = text.strip()
            if not stripped:
                continue
            if not stripped[0].isalnum():
                bullet_candidates.append(p)

        self._apply_list_candidates(bullet_candidates)

    def _apply_list_candidates(self, candidates):
        max_levels = 3
        level = 0
        for p in candidates:
            if level >= max_levels:
                break
            if p.find('SECDEF') or p.find('COLDEF'):
                continue

            structure = str(p).replace('<TAB/>', '    ')
            bullet_char_shape, text_char_shape, bullet_symbol, prefix_text = self._extract_list_char_shapes(p)
            if text_char_shape is None:
                continue
            para_shape = p.get('ParaShape', '0')

            if bullet_symbol:
                self.bullet_symbol_levels[level] = bullet_symbol

            style_key = f'ul{level + 1}'
            entry = {
                'structure': structure,
                'para_shape': para_shape,
                'bullet_char_shape': bullet_char_shape or self._extract_char_shape(structure),
                'text_char_shape': text_char_shape or self._extract_char_shape(structure),
                'prefix_text': prefix_text or ''
            }
            self.list_level_styles[level] = entry

            char_shape = self._extract_char_shape(structure)
            self.template_styles[style_key] = {
                'structure': structure,
                'para_shape': para_shape,
                'char_shape': char_shape,
                'bullet_char_shape': entry['bullet_char_shape'],
                'text_char_shape': entry['text_char_shape'],
                'has_table': '<TABLE' in structure,
                'has_field': '<FIELDBEGIN' in structure,
                'has_special_char_numbering': False,
                'prefix_text': prefix_text or ''
            }

            level += 1

    def _extract_list_char_shapes(self, p_tag):
        """Extract char shapes for bullet and text fragments from a sample paragraph."""
        bullet_char_shape = None
        text_char_shape = None
        bullet_symbol = None
        prefix_parts = []
        bullet_found = False

        for text_tag in p_tag.find_all('TEXT'):
            char_shape = text_tag.get('CharShape')
            for char_node in text_tag.find_all('CHAR'):
                content = char_node.text or ''
                if not bullet_found:
                    prefix_parts.append(content)

                stripped = content.strip()
                if not stripped:
                    continue

                first_char = stripped[0]
                if not bullet_found and not first_char.isalnum():
                    bullet_symbol = first_char
                    bullet_char_shape = char_shape
                    bullet_found = True
                else:
                    if text_char_shape is None:
                        text_char_shape = char_shape
                    if prefix_parts and first_char in prefix_parts[-1]:
                        prefix_parts[-1] = prefix_parts[-1][:prefix_parts[-1].find(first_char)]
                    bullet_found = True
                    break
            if bullet_found and text_char_shape is not None:
                break

        prefix_text = ''.join(prefix_parts)
        prefix_text = prefix_text.rstrip('\r').rstrip('\n')
        return bullet_char_shape, text_char_shape, bullet_symbol, prefix_text


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
                # <TAB/> 태그를 공백 4개로 치환
                element = element.replace('<TAB/>', '    ')
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
    
    def _extract_and_clone_charshapes(self, soup):
        """템플릿에서 CharShape을 추출하고 특별 서식이 적용된 복제본 생성 (단락/리스트 분리)"""
        docinfo = soup.find('MAPPINGTABLE')
        if not docinfo:
            raise ValueError("템플릿에 DOCINFO 섹션이 없습니다")

        charshapepool = docinfo.find('CHARSHAPELIST')
        if not charshapepool:
            raise ValueError("템플릿에 CHARSHAPEPOOL 섹션이 없습니다")

        all_charshapes = charshapepool.find_all('CHARSHAPE')
        if not all_charshapes:
            raise ValueError("템플릿에 CHARSHAPE 정의가 없습니다")

        last_id = max(int(cs.get('Id', '0')) for cs in all_charshapes)

        # --- 1. 일반 단락('p') 기반 특수 서식 생성 ---
        base_charshape_id_p = self.template_styles.get('p', {}).get('char_shape')
        base_charshape_p = next((cs for cs in all_charshapes if cs.get('Id') == base_charshape_id_p), None)

        if base_charshape_p is None:
            print(f"경고: 'p' 스타일에 대한 ID {base_charshape_id_p}의 CHARSHAPE을 찾을 수 없습니다. 첫 번째 CHARSHAPE을 사용합니다.")
            base_charshape_p = all_charshapes[0] if all_charshapes else None
        
        if base_charshape_p:
            p_formats = {
                'strong': str(last_id + 1), 'em': str(last_id + 2), 'underline': str(last_id + 3),
                'strong_em': str(last_id + 4), 'strong_underline': str(last_id + 5), 'em_underline': str(last_id + 6),
                'strong_em_underline': str(last_id + 7)
            }
            self.special_formats = p_formats
            
            # Clone and append for 'p'
            strong_p = self._clone_charshape(base_charshape_p, p_formats['strong']); strong_p.append(soup.new_tag("BOLD")); charshapepool.append(strong_p)
            em_p = self._clone_charshape(base_charshape_p, p_formats['em']); em_p.append(soup.new_tag("ITALIC")); charshapepool.append(em_p)
            underline_p = self._clone_charshape(base_charshape_p, p_formats['underline']); underline_p.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(underline_p)
            strong_em_p = self._clone_charshape(base_charshape_p, p_formats['strong_em']); strong_em_p.append(soup.new_tag("BOLD")); strong_em_p.append(soup.new_tag("ITALIC")); charshapepool.append(strong_em_p)
            strong_underline_p = self._clone_charshape(base_charshape_p, p_formats['strong_underline']); strong_underline_p.append(soup.new_tag("BOLD")); strong_underline_p.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(strong_underline_p)
            em_underline_p = self._clone_charshape(base_charshape_p, p_formats['em_underline']); em_underline_p.append(soup.new_tag("ITALIC")); em_underline_p.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(em_underline_p)
            strong_em_underline_p = self._clone_charshape(base_charshape_p, p_formats['strong_em_underline']); strong_em_underline_p.append(soup.new_tag("BOLD")); strong_em_underline_p.append(soup.new_tag("ITALIC")); strong_em_underline_p.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(strong_em_underline_p)
            last_id += 7

        # --- 2. 리스트(ul1/ul2/ul3) 기반 특수 서식 생성 ---
        if self.list_level_styles:
            # 깊이별로 각각 생성
            for level_index in sorted(self.list_level_styles.keys()):
                base_id = self.list_level_styles[level_index].get('text_char_shape')
                base_cs = next((cs for cs in all_charshapes if cs.get('Id') == base_id), None)
                if base_cs is None:
                    print(f"경고: 'ul{level_index+1}' 스타일의 텍스트 CharShape {base_id}를 찾을 수 없습니다. 'p' 스타일 기반을 사용합니다.")
                    base_cs = base_charshape_p
                if not base_cs:
                    continue
                ul_formats = {
                    'strong': str(last_id + 1), 'em': str(last_id + 2), 'underline': str(last_id + 3),
                    'strong_em': str(last_id + 4), 'strong_underline': str(last_id + 5), 'em_underline': str(last_id + 6),
                    'strong_em_underline': str(last_id + 7)
                }
                # 저장: 깊이별 특수 서식
                self.list_special_formats_levels[level_index] = ul_formats
                if level_index == 0:
                    # 하위 호환: 기존 속성에도 저장
                    self.list_special_formats = ul_formats
                # Clone and append for this level base
                strong_ul = self._clone_charshape(base_cs, ul_formats['strong']); strong_ul.append(soup.new_tag("BOLD")); charshapepool.append(strong_ul)
                em_ul = self._clone_charshape(base_cs, ul_formats['em']); em_ul.append(soup.new_tag("ITALIC")); charshapepool.append(em_ul)
                underline_ul = self._clone_charshape(base_cs, ul_formats['underline']); underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(underline_ul)
                strong_em_ul = self._clone_charshape(base_cs, ul_formats['strong_em']); strong_em_ul.append(soup.new_tag("BOLD")); strong_em_ul.append(soup.new_tag("ITALIC")); charshapepool.append(strong_em_ul)
                strong_underline_ul = self._clone_charshape(base_cs, ul_formats['strong_underline']); strong_underline_ul.append(soup.new_tag("BOLD")); strong_underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(strong_underline_ul)
                em_underline_ul = self._clone_charshape(base_cs, ul_formats['em_underline']); em_underline_ul.append(soup.new_tag("ITALIC")); em_underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(em_underline_ul)
                strong_em_underline_ul = self._clone_charshape(base_cs, ul_formats['strong_em_underline']); strong_em_underline_ul.append(soup.new_tag("BOLD")); strong_em_underline_ul.append(soup.new_tag("ITALIC")); strong_em_underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(strong_em_underline_ul)
                last_id += 7
        else:
            # 기존 방식(단일 ul) 하위 호환
            base_charshape_id_ul = self.template_styles.get('ul', {}).get('text_char_shape')
            base_charshape_ul = next((cs for cs in all_charshapes if cs.get('Id') == base_charshape_id_ul), None)
            if base_charshape_ul is None:
                print(f"경고: 'ul' 스타일에 대한 ID {base_charshape_id_ul}의 CHARSHAPE을 찾을 수 없습니다. 'p' 스타일 기반을 사용합니다.")
                base_charshape_ul = base_charshape_p
            if base_charshape_ul:
                ul_formats = {
                    'strong': str(last_id + 1), 'em': str(last_id + 2), 'underline': str(last_id + 3),
                    'strong_em': str(last_id + 4), 'strong_underline': str(last_id + 5), 'em_underline': str(last_id + 6),
                    'strong_em_underline': str(last_id + 7)
                }
                self.list_special_formats = ul_formats
                self.list_special_formats_levels[0] = ul_formats
                strong_ul = self._clone_charshape(base_charshape_ul, ul_formats['strong']); strong_ul.append(soup.new_tag("BOLD")); charshapepool.append(strong_ul)
                em_ul = self._clone_charshape(base_charshape_ul, ul_formats['em']); em_ul.append(soup.new_tag("ITALIC")); charshapepool.append(em_ul)
                underline_ul = self._clone_charshape(base_charshape_ul, ul_formats['underline']); underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(underline_ul)
                strong_em_ul = self._clone_charshape(base_charshape_ul, ul_formats['strong_em']); strong_em_ul.append(soup.new_tag("BOLD")); strong_em_ul.append(soup.new_tag("ITALIC")); charshapepool.append(strong_em_ul)
                strong_underline_ul = self._clone_charshape(base_charshape_ul, ul_formats['strong_underline']); strong_underline_ul.append(soup.new_tag("BOLD")); strong_underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(strong_underline_ul)
                em_underline_ul = self._clone_charshape(base_charshape_ul, ul_formats['em_underline']); em_underline_ul.append(soup.new_tag("ITALIC")); em_underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(em_underline_ul)
                strong_em_underline_ul = self._clone_charshape(base_charshape_ul, ul_formats['strong_em_underline']); strong_em_underline_ul.append(soup.new_tag("BOLD")); strong_em_underline_ul.append(soup.new_tag("ITALIC")); strong_em_underline_ul.append(soup.new_tag("UNDERLINE", Color="16711680", Shape="Solid", Type="Bottom")); charshapepool.append(strong_em_underline_ul)
                last_id += 7

        self.template_content = str(soup)


    def _clone_charshape(self, base_charshape, new_id):
        """CharShape 객체를 복제하고 새 ID를 할당합니다."""
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
                new_charshape.append(child)
            else:
                # 기존 서식 태그는 복사하지 않음 (새로 추가할 예정)
                if child.name not in ['BOLD', 'ITALIC', 'UNDERLINE']:
                    new_child = soup.new_tag(child.name)
                    for attr, value in child.attrs.items():
                        new_child[attr] = value
                    for grandchild in child.children:
                        if isinstance(grandchild, NavigableString):
                            new_child.append(grandchild)
                        else:
                            new_grandchild = soup.new_tag(grandchild.name)
                            for attr, value in grandchild.attrs.items():
                                new_grandchild[attr] = value
                            new_child.append(new_grandchild)
                    new_charshape.append(new_child)
        
        return new_charshape
    
    def add_table_borderfills(self, soup):
        """테이블용 BORDERFILL 요소를 추가하는 함수"""
        # BORDERFILLLIST 찾기
        borderfill_list = soup.find('BORDERFILLLIST')
        if not borderfill_list:
            print("BORDERFILLLIST를 찾을 수 없습니다. MAPPINGTABLE 내에서 검색을 시도합니다.")
            mapping_table = soup.find('MAPPINGTABLE')
            if mapping_table:
                borderfill_list = mapping_table.find('BORDERFILLLIST')
            
            if not borderfill_list:
                print("경고: BORDERFILLLIST를 찾을 수 없습니다. 기본 테두리 ID를 사용합니다.")
                # 기본 테두리 ID 유지
                self.table_border_fills = {'header': "3", 'footer': "4", 'body': "6"}
                return False

        # 기존 ID 중 가장 큰 값 찾기
        existing_ids = [int(bf.get('Id', '0')) for bf in borderfill_list.find_all('BORDERFILL')]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        

        # 테이블용 테두리 스타일 정의 - 12개 영역별 정의
        table_borderfills = [
            # 1번째 행 가장 왼쪽 (ID: next_id)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.4mm"/>
<BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 1번째 행 가운데 (ID: next_id + 1)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.4mm"/>
<BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 1번째 행 가장 오른쪽 (ID: next_id + 2)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="None" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.4mm"/>
<BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 2번째 행 가장 왼쪽 (ID: next_id + 3)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="DoubleSlim" Width="0.5mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>
""",

            # 2번째 행 가운데 (ID: next_id + 4)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="DoubleSlim" Width="0.5mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 2번째 행 가장 오른쪽 (ID: next_id + 5)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="None" Width="0.12mm"/>
<TOPBORDER Type="DoubleSlim" Width="0.5mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 마지막 행 가장 왼쪽 (ID: next_id + 6)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.4mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 마지막 행 가운데 (ID: next_id + 7)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.4mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 마지막 행 가장 오른쪽 (ID: next_id + 8)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="None" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.4mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 중간 행 가장 왼쪽 (ID: next_id + 9)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 중간 행 가운데 (ID: next_id + 10)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>""",

            # 중간 행 가장 오른쪽 (ID: next_id + 11)
            """<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="None" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>"""
        ]

        # 테이블 테두리 ID 저장 - 세분화된 영역별 매핑
        self.table_border_fills = {
            'first_row_left': str(next_id),      # 1번째 행 가장 왼쪽
            'first_row_center': str(next_id + 1), # 1번째 행 가운데
            'first_row_right': str(next_id + 2),  # 1번째 행 가장 오른쪽
            'second_row_left': str(next_id + 3),  # 2번째 행 가장 왼쪽
            'second_row_center': str(next_id + 4), # 2번째 행 가운데
            'second_row_right': str(next_id + 5),  # 2번째 행 가장 오른쪽
            'last_row_left': str(next_id + 6),     # 마지막 행 가장 왼쪽
            'last_row_center': str(next_id + 7),   # 마지막 행 가운데
            'last_row_right': str(next_id + 8),    # 마지막 행 가장 오른쪽
            'middle_row_left': str(next_id + 9),   # 중간 행 가장 왼쪽
            'middle_row_center': str(next_id + 10), # 중간 행 가운데
            'middle_row_right': str(next_id + 11)   # 중간 행 가장 오른쪽
        }

        # BORDERFILL 요소 추가
        for i, bf_template in enumerate(table_borderfills):
            new_id = next_id + i
            bf_soup = BeautifulSoup(bf_template.format(new_id), 'xml')
            borderfill_list.append(bf_soup.find('BORDERFILL'))

        # Count 속성 업데이트
        borderfill_list['Count'] = str(len(borderfill_list.find_all('BORDERFILL')))

        # 템플릿 내용 업데이트
        return True 

    
    def _create_parashape_with_spacing(self, soup, para_id, line_spacing):
        """문단 간격이 조정된 ParaShape 생성"""
        # 기본 ParaShape 복제
        base_parashape = soup.find('PARASHAPE')
        if not base_parashape:
            print("기본 ParaShape을 찾을 수 없습니다.")
            return None
        
        new_parashape = soup.new_tag("PARASHAPE")
        
        # 모든 속성 복사
        for attr, value in base_parashape.attrs.items():
            new_parashape[attr] = value
        
        # ID 업데이트
        new_parashape['Id'] = str(para_id)
        
        # 기존 속성 복사
        for child in base_parashape.children:
            if isinstance(child, NavigableString):
                new_parashape.append(child.copy())
            else:
                new_child = soup.new_tag(child.name)
                for attr, value in child.attrs.items():
                    new_child[attr] = value
                new_parashape.append(new_child)
        
        # 문단 간격 설정
        new_parashape['LineSpacing'] = str(line_spacing)
        new_parashape['LineSpacingType'] = "Percent"  # 비율 단위 사용
        
        return new_parashape 

    def set_paragraph_format(self, format_type):
        """문단 형식 설정 (normal, template_default)"""
        if format_type in ['normal', 'template_default']:
            self.current_paragraph_format = format_type
            print(f"문단 형식이 '{format_type}'으로 설정되었습니다.")
        else:
            print(f"지원하지 않는 문단 형식입니다: {format_type}")
    
    def get_paragraph_format_settings(self):
        """현재 문단 형식 설정 반환"""
        if self.current_paragraph_format == 'template_default':
            return None  # 템플릿 기본값 사용
        else:
            return self.paragraph_format_settings[f"{self.current_paragraph_format}_format"]
    
    def adjust_parashape_format(self, parashape_soup, format_settings=None):
        """ParaShape의 문단 형식을 조정"""
        if format_settings is None:
            format_settings = self.get_paragraph_format_settings()
        
        if format_settings is None:
            return parashape_soup  # 템플릿 기본값 사용
        
        # PARAMARGIN 태그 찾기
        paramargin = parashape_soup.find('PARAMARGIN')
        if paramargin:
            # Indent 설정
            if 'indent' in format_settings:
                paramargin['Indent'] = str(format_settings['indent'])
            
            # LineSpacing 설정
            if 'line_spacing' in format_settings:
                paramargin['LineSpacing'] = str(format_settings['line_spacing'])
            
            # LineSpacingType 설정
            if 'line_spacing_type' in format_settings:
                paramargin['LineSpacingType'] = format_settings['line_spacing_type']
        
        return parashape_soup

    def create_default_template(self, template_name):
        """기본 문서 설정이 적용된 새 템플릿 생성"""
        try:
            # 템플릿 이름에 .hml 확장자 추가
            if not template_name.endswith('.hml'):
                template_name += '.hml'
            
            # 새 템플릿 파일 경로
            new_template_path = os.path.join(self.default_template_dir, template_name)
            
            # 템플릿 저장 경로 로그 출력
            print(f"템플릿 생성 시작:")
            print(f"  - 템플릿 이름: {template_name}")
            print(f"  - 저장 경로: {new_template_path}")
            print(f"  - 템플릿 디렉토리 존재: {os.path.exists(self.default_template_dir)}")
            
            # 기본 템플릿 파일이 존재하는지 확인
            if not os.path.exists(self.default_template_file):
                error_msg = f"기본 템플릿 파일을 찾을 수 없습니다.\n경로: {self.default_template_file}"
                print(error_msg)  # 디버깅을 위한 출력
                return False, error_msg
            
            # 기본 템플릿 파일을 새 템플릿 파일로 복사
            import shutil
            try:
                shutil.copy2(self.default_template_file, new_template_path)
                print(f"템플릿 파일 복사 성공: {new_template_path}")
                print(f"새 템플릿 생성 성공: {new_template_path}")  # 디버깅을 위한 출력
                return True, f"새 템플릿 '{template_name}' 생성 완료"
            except Exception as copy_error:
                error_msg = f"파일 복사 중 오류 발생: {str(copy_error)}"
                print(error_msg)  # 디버깅을 위한 출력
                return False, error_msg
            
        except Exception as e:
            error_msg = f"템플릿 생성 중 오류 발생: {str(e)}"
            print(error_msg)  # 디버깅을 위한 출력
            return False, error_msg
    
    def create_template_from_source_advanced(self, source_path, template_name, p_tag_mappings):
        """
        [수정된 로직] 원본 문서(source_path)를 기반으로 BeautifulSoup DOM을 직접 조작하여 안전하게 템플릿을 생성합니다.
        정규식과 문자열 재파싱을 최소화하여 구조적 안정성을 확보합니다.
        """
        try:
            # 템플릿 이름 및 경로 설정
            if not template_name.endswith('.hml'):
                template_name += '.hml'
            new_template_path = os.path.join(self.default_template_dir, template_name)
            
            print(f"고급 템플릿 생성 시작 (DOM 기반):")
            print(f"  - 템플릿 이름: {template_name}")
            print(f"  - 저장 경로: {new_template_path}")
            print(f"  - 원본 파일: {source_path}")
            
            # 1. 원본 HML 파일을 읽고 전체를 BeautifulSoup 객체로 파싱
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            soup = BeautifulSoup(source_content, 'xml')

            # 2. HEAD 수정: BorderFill 태그 추가 (기존 DOM 객체 직접 수정)
            head_tag = soup.find('HEAD')
            if not head_tag:
                return False, "원본 파일에서 HEAD 태그를 찾을 수 없습니다."
            self._add_borderfills_to_head(head_tag)

            # 3. 원본 DOM에서 SECDEF 포함 P 태그를 찾아 보관 (나중에 사용하기 위함)
            secdef_para_tag = None
            for p_tag in soup.find_all('P'):
                if p_tag.find('SECDEF'):
                    # CHAR 태그 안의 내용을 공백으로 정리
                    for char_tag in p_tag.find_all('CHAR'):
                        char_tag.string = ' '
                    secdef_para_tag = p_tag.extract() # 원본 DOM에서 분리하여 보관
                    break
            
            # 4. BODY 섹션 준비 (기존 내용 모두 삭제)
            section_tag = soup.find('SECTION')
            if not section_tag:
                return False, "원본 파일에서 SECTION 태그를 찾을 수 없습니다."
            section_tag.clear()

            # 5. 사용자가 선택한 문단에 SECDEF가 있는지 확인
            has_secdef_in_selection = any('<SECDEF' in p_str for p_str in p_tag_mappings.values())

            # 6. 필요 시, 보관해 둔 SECDEF P 태그를 SECTION의 맨 앞에 삽입
            if not has_secdef_in_selection:
                if secdef_para_tag:
                    print("템플릿에 SECDEF 태그가 누락되어 원본 문서에서 가져옵니다.")
                    section_tag.insert(0, secdef_para_tag)
                    print("편집 용지(SECDEF/COLDEF) 설정을 템플릿 맨 앞에 추가했습니다.")
                else:
                    print("경고: 원본 문서에서도 용지 설정(SECDEF/COLDEF)을 찾지 못했습니다.")

            # 7. 사용자가 매핑한 P 태그들을 SECTION에 순서대로 추가
            placeholder_p_tag = '<P ParaShape="0" Style="0"><TEXT CharShape="0"><CHAR>###</CHAR></TEXT></P>'
            p_tag_strings = [placeholder_p_tag] * len(self.style_mapping_order)
            for line_num_str, p_tag_str in p_tag_mappings.items():
                try:
                    index = int(line_num_str) - 1
                    if 0 <= index < len(p_tag_strings):
                        # <TAB/> 태그를 공백 4개로 치환
                        p_tag_str = p_tag_str.replace('<TAB/>', '    ')
                        p_tag_strings[index] = p_tag_str
                except (ValueError, TypeError):
                    continue
            
            for p_tag_str in p_tag_strings:
                p_soup = BeautifulSoup(p_tag_str, 'xml')
                p_tag_to_append = p_soup.find('P')
                if p_tag_to_append:
                    section_tag.append(p_tag_to_append)

            # 8. 최종 수정된 soup 객체를 파일에 저장
            with open(new_template_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"템플릿 파일 저장 성공: {new_template_path}")
            return True, f"새 템플릿 '{template_name}' 생성 완료"
            
        except Exception as e:
            error_msg = f"템플릿 생성 중 오류 발생: {str(e)}"
            print(error_msg)
            return False, error_msg

    def _add_borderfills_to_head(self, head_tag):
        """head_tag 객체에 테이블용 BORDERFILL 요소들을 직접 추가합니다."""
        try:
            borderfill_list = head_tag.find('BORDERFILLLIST')
            if not borderfill_list:
                print("경고: BORDERFILLLIST를 찾을 수 없습니다.")
                return

            existing_ids = [int(bf.get('Id', '0')) for bf in borderfill_list.find_all('BORDERFILL')]
            next_id = max(existing_ids) + 1 if existing_ids else 1

            new_borderfills_xml = [
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.4mm"/><BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 1}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.4mm"/><BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 2}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.4mm"/><BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 3}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.4mm"/><BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 4}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="DoubleSlim" Width="0.5mm"/><BOTTOMBORDER Type="Solid" Width="0.12mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 5}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.12mm"/><BOTTOMBORDER Type="Solid" Width="0.12mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 6}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="None" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.4mm"/><BOTTOMBORDER Type="DoubleSlim" Width="0.5mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 7}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="None" Width="0.12mm"/><TOPBORDER Type="DoubleSlim" Width="0.5mm"/><BOTTOMBORDER Type="Solid" Width="0.12mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 8}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="None" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.12mm"/><BOTTOMBORDER Type="Solid" Width="0.12mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 9}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="None" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.12mm"/><BOTTOMBORDER Type="Solid" Width="0.4mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 10}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="Solid" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.12mm"/><BOTTOMBORDER Type="Solid" Width="0.4mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>',
                f'<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="{next_id + 11}" Shadow="false" Slash="0" ThreeD="false"><LEFTBORDER Type="Solid" Width="0.12mm"/><RIGHTBORDER Type="None" Width="0.12mm"/><TOPBORDER Type="Solid" Width="0.12mm"/><BOTTOMBORDER Type="Solid" Width="0.4mm"/><DIAGONAL Type="Solid" Width="0.1mm"/></BORDERFILL>'
            ]
            
            for bf_xml in new_borderfills_xml:
                bf_soup = BeautifulSoup(bf_xml, 'xml')
                if bf_soup.BORDERFILL:
                    borderfill_list.append(bf_soup.BORDERFILL)

            borderfill_list['Count'] = str(len(borderfill_list.find_all('BORDERFILL')))

            self.table_border_fills = {
                'first_row_left': str(next_id),
                'first_row_center': str(next_id + 1),
                'first_row_right': str(next_id + 2),
                'second_row_left': str(next_id + 3),
                'second_row_center': str(next_id + 4),
                'second_row_right': str(next_id + 5),
                'last_row_left': str(next_id + 6),
                'last_row_center': str(next_id + 7),
                'last_row_right': str(next_id + 8),
                'middle_row_left': str(next_id + 9),
                'middle_row_center': str(next_id + 10),
                'middle_row_right': str(next_id + 11)
            }
            
            print(f"BorderFill 태그 {len(new_borderfills_xml)}개 추가 완료 (ID: {next_id} ~ {next_id + len(new_borderfills_xml) - 1})")
            print(f"테이블 테두리 BorderFill ID 매핑 업데이트 완료")
            
        except Exception as e:
            print(f"BorderFill 추가 중 오류 발생: {e}")
