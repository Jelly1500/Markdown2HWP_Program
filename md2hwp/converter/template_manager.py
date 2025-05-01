"""
HWPML 템플릿 관리 모듈
"""
import re
from bs4 import BeautifulSoup, NavigableString
from ..config import STYLE_MAPPING_ORDER, DEFAULT_BULLET_SYMBOL
import os

class TemplateManager:
    """HWPML 템플릿 관리 클래스"""
    
    def __init__(self):
        self.template_content = None
        self.template_styles = {}
        self.special_formats = {}
        self.table_border_fills = {'header': "3", 'footer': "4", 'body': "6"}  # 기본값
        self.style_mapping_order = STYLE_MAPPING_ORDER
        self.bullet_symbol = DEFAULT_BULLET_SYMBOL  # 기본 글머리표
        self.margin_para_shapes = {}
        
        # 기본 템플릿 경로 설정 수정
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.default_template_dir = os.path.join(base_path, "md2hwp", "new_template")
        self.default_template_file = os.path.join(self.default_template_dir, "템플릿문서.hml")
        
        # 디버깅을 위한 경로 출력
        print(f"Template Manager 초기화:")
        print(f"Base Path: {base_path}")
        print(f"Default Template Dir: {self.default_template_dir}")
        print(f"Default Template File: {self.default_template_file}")
        print(f"Default Template File Exists: {os.path.exists(self.default_template_file)}")
    
    def load_template(self, template_path):
        """HWPML 템플릿 파일 로드 및 서식 구조 추출"""
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                self.template_content = file.read()
                
            # 템플릿에서 서식 구조 추출
            self._extract_template_styles()
            
            # CharShape 추출 및 특별 서식 복제
            self.special_formats = self._extract_and_clone_charshapes()
            
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

            # 중간 행용 테두리 (상단 점선, 하단 점선) - ID: next_id + 2
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
            
            # 기본 템플릿 파일이 존재하는지 확인
            if not os.path.exists(self.default_template_file):
                error_msg = f"기본 템플릿 파일을 찾을 수 없습니다.\n경로: {self.default_template_file}"
                print(error_msg)  # 디버깅을 위한 출력
                return False, error_msg
            
            # 기본 템플릿 파일을 새 템플릿 파일로 복사
            import shutil
            try:
                shutil.copy2(self.default_template_file, new_template_path)
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

    def create_template_from_source(self, source_path, template_name):
        """원본 문서 설정이 적용된 새 템플릿 생성"""
        try:
            # 템플릿 이름에 .hml 확장자 추가
            if not template_name.endswith('.hml'):
                template_name += '.hml'
            
            # 새 템플릿 파일 경로
            new_template_path = os.path.join(self.default_template_dir, template_name)
            
            # 기본 템플릿 파일이 존재하는지 확인
            if not os.path.exists(self.default_template_file):
                return False, "기본 템플릿 파일을 찾을 수 없습니다."
            
            # 원본 파일에서 HEAD 태그 전체 추출
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            # HEAD 태그 전체 추출
            head_pattern = r'<HEAD.*?</HEAD>'
            head_match = re.search(head_pattern, source_content, re.DOTALL)
            
            if not head_match:
                return False, "원본 파일에서 HEAD 태그를 찾을 수 없습니다."
            
            # HEAD 태그 전체 내용 추출
            head_content = head_match.group(0)
            print(f"추출된 HEAD 태그: {head_content[:200]}...")
            
            # 원본 파일에서 PAGEDEF 태그 추출
            pagedef_pattern = r'<PAGEDEF.*?</PAGEDEF>'
            pagedef_match = re.search(pagedef_pattern, source_content, re.DOTALL)
            
            if not pagedef_match:
                return False, "원본 파일에서 PAGEDEF 태그를 찾을 수 없습니다."
            
            # PAGEDEF 태그 내용 추출
            pagedef_content = pagedef_match.group(0)
            print(f"추출된 PAGEDEF 태그: {pagedef_content}")
            
            # 기본 템플릿 파일 로드
            with open(self.default_template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 기본 템플릿의 HEAD 태그를 원본의 HEAD 태그로 교체
            template_head_pattern = r'<HEAD.*?</HEAD>'
            template_content = re.sub(template_head_pattern, head_content, template_content, flags=re.DOTALL)
            
            # 기본 템플릿의 PAGEDEF 태그를 원본의 PAGEDEF 태그로 교체
            template_pagedef_pattern = r'<PAGEDEF.*?</PAGEDEF>'
            template_content = re.sub(template_pagedef_pattern, pagedef_content, template_content, flags=re.DOTALL)
            
            # 수정된 템플릿을 새 파일로 저장
            with open(new_template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            return True, f"새 템플릿 '{template_name}' 생성 완료"
            
        except Exception as e:
            return False, f"템플릿 생성 중 오류 발생: {str(e)}" 