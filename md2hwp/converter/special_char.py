"""
특수 문자 처리 및 자동 증가 담당 모듈
"""
import re
from md2hwp.config import SPECIAL_CHAR_MAPS

class SpecialCharHandler:
    """특수 문자 처리 및 자동 증가 담당 클래스"""
    
    def __init__(self):
        # 특수 문자 증가를 위한 카운터 저장
        self.special_char_counters = {}

        # 헤딩 계층 구조별 숫자 카운터 (예: h1 -> 1, h2 -> 1.1 ...)
        self.heading_counters = {
            'h1': 0, 'h2': 0, 'h3': 0,
            'h4': 0, 'h5': 0, 'h6': 0
        }
        
        # 특수 문자 유니코드 매핑
        self.special_char_maps = SPECIAL_CHAR_MAPS
        
        # 헤딩 레벨별 계층 구조를 위한 데이터
        self.heading_levels = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    def identify_special_char(self, char):
        """특수 문자가 어떤 유형인지 식별하고 정보 반환"""
        code_point = ord(char)

        # ASCII 숫자 처리 ('1' ~ '9')
        if '1' <= char <= '9':
            return {
                'type': 'ascii_digit',
                'value': int(char),
                'code_point': code_point,
                'info': {
                    'range': (ord('1'), ord('9')),
                    'base_value': 1,
                    'max_count': 9
                }
            }

        # 기존 특수 문자 매핑 처리
        for char_type, info in self.special_char_maps.items():
            start, end = info['range']
            if start <= code_point <= end:
                if char_type in ['circled_uppercase', 'circled_lowercase']:
                    value = chr(code_point - start + info['base_value'])
                else:
                    value = code_point - start + info['base_value']
                return {
                    'type': char_type,
                    'value': value,
                    'code_point': code_point,
                    'info': info
                }
        
        return None
    
    
    def increment_special_char(self, char, template_type):
        """특수 문자를 식별하고 증가된 값의 문자 반환 (카운터 초기화 로직 제거)"""
        special_char_info = self.identify_special_char(char)
        if not special_char_info:
            return char  # 특수 문자가 아니면 그대로 반환
        
        char_type = special_char_info['type']
        
        # 해당 템플릿 타입에 대한 카운터 가져오기
        if template_type not in self.special_char_counters:
            self.special_char_counters[template_type] = {}
        
        type_counters = self.special_char_counters[template_type]
        
        # 해당 특수 문자 타입의 카운터 가져오기 또는 초기화
        if char_type not in type_counters:
            # 최초 발견 시 현재 값으로 설정 (1부터 시작)
            type_counters[char_type] = 1
        else:
            # 이미 카운터가 있으면 증가
            type_counters[char_type] += 1
        
        # 최대값 확인
        max_count = special_char_info['info']['max_count']
        if type_counters[char_type] > max_count:
            type_counters[char_type] = 1  # 최대값 초과 시 1로 리셋
        
        # 증가된 값에 해당하는 유니코드 문자 반환
        start, _ = special_char_info['info']['range']
        next_value = type_counters[char_type]
        
        # 알파벳/숫자 공통 처리
        offset = next_value - 1  # 1부터 시작하므로 1을 빼줌
        next_code_point = start + offset
        
        return chr(next_code_point)
    
    def process_special_chars_in_template(self, template, template_type, text):
        """템플릿 내의 특수 문자를 처리하여 자동 증가시킴 (하위 헤딩 카운터 초기화 추가)"""
        
        # 헤딩 계층 구조 처리: 현재 템플릿 타입이 헤딩이면 하위 레벨 카운터 초기화
        if template_type in self.heading_levels:
            current_level_index = self.heading_levels.index(template_type)
            type_counters = self.special_char_counters.get(template_type, {})

            for lower_level in self.heading_levels[current_level_index + 1:]:
                if lower_level in type_counters:
                    type_counters[lower_level] = 0  # 또는 del type_counters[lower_level]

        
        # 모든 <CHAR>...</CHAR> 태그 찾기
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
        matches = list(char_pattern.finditer(template))
        
        if not matches:
            return template
        
        # 각 매치에 대해 특수 문자 증가 적용
        new_template = template
        offset = 0  # 문자열 길이 변화에 따른 오프셋
        
        for match in matches:
            start, end = match.span()
            start += offset
            end += offset
            original_content = match.group(1)
            
            # 텍스트가 삽입될 위치인 가장 긴 CHAR 태그 건너뛰기
            if match == max(matches, key=lambda m: len(m.group(1))):
                continue
            
            # 특수 문자 찾기 및 처리
            new_content = original_content
            for i, char in enumerate(original_content):
                special_char_info = self.identify_special_char(char)
                if special_char_info:
                    next_char = self.increment_special_char(char, template_type)
                    new_content = new_content[:i] + next_char + new_content[i+1:]
            
            # 내용에 변경이 있으면 교체
            if new_content != original_content:
                replacement = f'<CHAR>{new_content}</CHAR>'
                new_template = new_template[:start] + replacement + new_template[end:]
                offset += len(replacement) - (end - start)
        
        return new_template
    
    def reset_counters(self):
        """특수 문자 카운터 초기화"""
        # 초기화 전에 기존 카운터 값 출력
        print("Before resetting counters:")
        for template_type, counters in self.special_char_counters.items():
            print(f"Template Type: {template_type}")
            for char_type, count in counters.items():
                print(f"  {char_type}: {count}")
        
        # 카운터 초기화
        self.special_char_counters = {}
        
        # 초기화 후 새로 들어오는 카운터 값 출력
        print("\nAfter resetting counters:")
        for template_type, counters in self.special_char_counters.items():
            print(f"Template Type: {template_type}")
            for char_type, count in counters.items():
                print(f"  {char_type}: {count}")