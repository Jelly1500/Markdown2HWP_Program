"""
HWPML 템플릿 관리 모듈
"""
import re
from bs4 import BeautifulSoup, NavigableString
from ..config import STYLE_MAPPING_ORDER, DEFAULT_BULLET_SYMBOL
from .special_char import SpecialCharHandler
import os

class TemplateManager:
    """HWPML 템플릿 관리 클래스"""
    
    def __init__(self):
        self.template_content = None
        self.template_styles = {}
        self.special_formats = {}
        self.list_special_formats = {}
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
    
    def load_template(self, template_path):
        """HWPML 템플릿 파일 로드 및 서식 구조 추출"""
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                self.template_content = file.read()
            
            # 템플릿에서 서식 구조 추출
            self._extract_template_styles()
            
            # CharShape 추출 및 특별 서식 복제
            self._extract_and_clone_charshapes()
            
            # 테이블 테두리 스타일 추가
            border_result = self.add_table_borderfills()
            if not border_result:
                print("테이블 테두리 스타일 추가에 실패했습니다. 기본값을 사용합니다.")
            
            
            
            return True
        except Exception as e:
            print(f"템플릿 로드 오류: {e}")
            return False
    
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
        
        # 서식 스타일 매핑 초기화
        self.template_styles = {key: None for key in self.style_mapping_order}
        
        # 순서대로 마크다운 요소에 매핑
        for idx, tag_structure in enumerate(balanced_p_tags):
            if idx < len(self.style_mapping_order):
                style_key = self.style_mapping_order[idx]

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

                self.template_styles[style_key] = {
                    'structure': tag_structure,
                    'para_shape': self._extract_para_shape(tag_structure),
                    'char_shape': self._extract_char_shape(tag_structure),
                    'has_table': '<TABLE' in tag_structure,
                    'has_field': '<FIELDBEGIN' in tag_structure,
                    'has_special_char_numbering': has_special_char_numbering
                }
                
                # 순서 없는 리스트에서 글머리표 추출
                if style_key == 'ul':
                    text_matches = re.findall(r'<TEXT CharShape="(\d+)">', tag_structure)
                    if len(text_matches) >= 2:
                        self.template_styles[style_key]['bullet_char_shape'] = text_matches[0]
                        self.template_styles[style_key]['text_char_shape'] = text_matches[1]
                    else:
                        self.template_styles[style_key]['bullet_char_shape'] = self._extract_char_shape(tag_structure)
                        self.template_styles[style_key]['text_char_shape'] = self._extract_char_shape(tag_structure)
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
    
    def _extract_and_clone_charshapes(self):
        """템플릿에서 CharShape을 추출하고 특별 서식이 적용된 복제본 생성 (단락/리스트 분리)"""
        soup = BeautifulSoup(self.template_content, 'xml')

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

        # --- 2. 리스트('ul') 기반 특수 서식 생성 ---
        base_charshape_id_ul = self.template_styles.get('ul', {}).get('text_char_shape')
        base_charshape_ul = next((cs for cs in all_charshapes if cs.get('Id') == base_charshape_id_ul), None)

        if base_charshape_ul is None:
            print(f"경고: 'ul' 스타일에 대한 ID {base_charshape_id_ul}의 CHARSHAPE을 찾을 수 없습니다. 'p' 스타일 기반을 사용합니다.")
            base_charshape_ul = base_charshape_p # Fallback to paragraph style

        if base_charshape_ul:
            ul_formats = {
                'strong': str(last_id + 1), 'em': str(last_id + 2), 'underline': str(last_id + 3),
                'strong_em': str(last_id + 4), 'strong_underline': str(last_id + 5), 'em_underline': str(last_id + 6),
                'strong_em_underline': str(last_id + 7)
            }
            self.list_special_formats = ul_formats
            
            # Clone and append for 'ul'
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
    
    def add_table_borderfills(self):
        """테이블용 BORDERFILL 요소를 추가하는 함수"""
        soup = BeautifulSoup(self.template_content, 'xml')

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
        self.template_content = str(soup)
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
        원본 문서 설정과 입력된 P 태그 매핑이 적용된 새 템플릿을 생성합니다.
        (요구사항에 맞춰 수정된 함수)
        """
        try:
            # 템플릿 이름에 .hml 확장자 추가
            if not template_name.endswith('.hml'):
                template_name += '.hml'
            
            # 새 템플릿 파일 경로
            new_template_path = os.path.join(self.default_template_dir, template_name)
            
            # 템플릿 저장 경로 로그 출력
            print(f"고급 템플릿 생성 시작:")
            print(f"  - 템플릿 이름: {template_name}")
            print(f"  - 저장 경로: {new_template_path}")
            print(f"  - 템플릿 디렉토리 존재: {os.path.exists(self.default_template_dir)}")
            print(f"  - 원본 파일: {source_path}")
            print(f"  - P태그 매핑 개수: {len(p_tag_mappings)}")
            
            # 기본 템플릿 파일이 존재하는지 확인
            if not os.path.exists(self.default_template_file):
                error_msg = f"기본 템플릿 파일을 찾을 수 없습니다.\n경로: {self.default_template_file}"
                print(error_msg)
                return False, error_msg
            
            # --- 기존 로직 (HEAD 및 PAGEDEF 태그 처리) - 그대로 유지 ---
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            head_pattern = r'<HEAD.*?</HEAD>'
            head_match = re.search(head_pattern, source_content, re.DOTALL)
            if not head_match:
                return False, "원본 파일에서 HEAD 태그를 찾을 수 없습니다."
            head_content = head_match.group(0)

            # --- BorderFill 태그들을 head_content에 추가하는 로직 ---
            head_content = self._add_borderfills_to_head(head_content)

            pagedef_pattern = r'<PAGEDEF.*?</PAGEDEF>'
            pagedef_match = re.search(pagedef_pattern, source_content, re.DOTALL)
            if not pagedef_match:
                return False, "원본 파일에서 PAGEDEF 태그를 찾을 수 없습니다."
            pagedef_content = pagedef_match.group(0)

            with open(self.default_template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template_content = re.sub(r'<HEAD.*?</HEAD>', head_content, template_content, flags=re.DOTALL)
            template_content = re.sub(r'<PAGEDEF.*?</PAGEDEF>', pagedef_content, template_content, flags=re.DOTALL)

            # --- ★★★ 신규 로직 (BODY 내용 생성 및 교체) ★★★ ---

            # 1. 8개의 플레이스홀더 P 태그를 생성합니다.
            placeholder_p_tag = '<P ParaShape="0" Style="0"><TEXT CharShape="0"><CHAR>###</CHAR></TEXT></P>'
            p_tag_list = [placeholder_p_tag] * 8
            
            # 2. 입력받은 p_tag_mappings에 따라 플레이스홀더를 실제 P 태그로 교체합니다.
            for line_num_str, new_p_tag in p_tag_mappings.items():
                try:
                    # 1 기반 인덱스를 0 기반으로 변환
                    index = int(line_num_str) - 1
                    if 0 <= index < len(p_tag_list):
                        p_tag_list[index] = new_p_tag
                        print(f"  - P태그 매핑: {line_num_str} -> 인덱스 {index}")
                    else:
                        print(f"경고: 유효하지 않은 줄 번호 '{line_num_str}'는 무시됩니다.")
                except (ValueError, TypeError):
                    print(f"경고: 잘못된 키 값 '{line_num_str}'는 무시됩니다.")

            # 3. 수정된 P 태그 리스트를 하나의 문자열로 결합합니다.
            final_p_tags_string = "\n".join(p_tag_list)

            # 4. 템플릿에서 기존 BODY 블록을 찾아 새로 생성한 내용으로 교체합니다.
            #    이때, BODY와 SECTION의 여는 태그는 원본 템플릿의 것을 유지하여 속성을 보존합니다.
            body_open_match = re.search(r'(<BODY.*?>)', template_content, re.DOTALL)
            section_open_match = re.search(r'(<SECTION.*?>)', template_content, re.DOTALL)
            
            body_open_tag = body_open_match.group(1) if body_open_match else "<BODY>"
            section_open_tag = section_open_match.group(1) if section_open_match else '<SECTION ID="0">'
            
            # 새로운 BODY 블록 구성
            new_body_block = f"{body_open_tag}\n{section_open_tag}\n{final_p_tags_string}\n</SECTION>\n</BODY>"
            
            # 기존 BODY 블록 전체를 새로운 블록으로 교체
            template_content = re.sub(r'<BODY.*?</BODY>', new_body_block, template_content, flags=re.DOTALL)

            # -------------------- 신규 로직 끝 --------------------

            # 수정된 템플릿을 새 파일로 저장
            with open(new_template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"템플릿 파일 저장 성공: {new_template_path}")
            return True, f"새 템플릿 '{template_name}' 생성 완료"
            
        except Exception as e:
            error_msg = f"템플릿 생성 중 오류 발생: {str(e)}"
            print(error_msg)
            return False, error_msg

    def _add_borderfills_to_head(self, head_content):
        """head_content에 새로운 BorderFill 태그들을 추가합니다. (BeautifulSoup 사용)"""
        try:
            soup = BeautifulSoup(head_content, 'xml')
            borderfill_list = soup.find('BORDERFILLLIST')

            if not borderfill_list:
                print("경고: BORDERFILLLIST를 찾을 수 없습니다.")
                return head_content

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
                borderfill_list.append(bf_soup.find('BORDERFILL'))

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
            
            # BeautifulSoup 객체를 문자열로 변환하여 반환하되, <?xml> 선언이 붙지 않도록 HEAD 태그 내용만 추출
            head_tag = soup.find('HEAD')
            if head_tag:
                return str(head_tag)
            return head_content

        except Exception as e:
            print(f"BorderFill 추가 중 오류 발생: {e}")
            return head_content