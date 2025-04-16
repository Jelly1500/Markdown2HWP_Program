"""
특수 문자 처리 및 자동 증가 담당 모듈
"""
import re
from md2hwp.config import SPECIAL_CHAR_MAPS

class SpecialCharHandler:
    """특수 문자 처리 및 자동 증가 담당 클래스"""
    
    def __init__(self):
        self.special_char_counters = {}
        
        self.special_char_maps = SPECIAL_CHAR_MAPS
        
        self.heading_levels = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    def identify_special_char(self, char):
        """특수 문자가 어떤 유형인지 식별하고 정보 반환"""
        code_point = ord(char)
        
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
        """특수 문자와 아라비아 숫자를 식별하고 증가된 값의 문자 반환. 첫 발견 시 원본 문자 반환."""
        special_char_info = self.identify_special_char(char)
        if not special_char_info:
            return char  

        char_type = special_char_info['type']
        char_value = special_char_info['value'] 
        char_info = special_char_info['info']
        base_value = char_info['base_value']
        max_value = char_info['max_count']
        start_code_point, _ = char_info['range']

        if template_type not in self.special_char_counters:
            self.special_char_counters[template_type] = {}
        type_counters = self.special_char_counters[template_type]

        if char_type not in type_counters:
            type_counters[char_type] = char_value
            return char
        else:
            current_counter_value = type_counters[char_type]

            if isinstance(current_counter_value, str):
                current_ordinal = ord(current_counter_value) - base_value
                next_ordinal = current_ordinal + 1
                if next_ordinal >= max_value:
                    next_ordinal = 0
                
                next_char_code = base_value + next_ordinal
                type_counters[char_type] = chr(next_char_code)
                next_code_point = start_code_point + next_ordinal 
                
            else:
                next_counter_value = current_counter_value + 1
                if next_counter_value > max_value: 
                    next_counter_value = base_value 
                
                type_counters[char_type] = next_counter_value 
                offset = next_counter_value - base_value
                next_code_point = start_code_point + offset 

            return chr(next_code_point)
    
    def process_special_chars_in_template(self, template, style_key):
        """템플릿 내의 특수 문자를 처리하여 자동 증가시킴 (하위 헤딩 카운터 초기화 추가)"""
        
        if style_key in self.heading_levels:
            current_level_index = self.heading_levels.index(style_key)
            for level in self.heading_levels[current_level_index + 1:]:
                if level in self.special_char_counters:
                    self.special_char_counters[level] = {}
        
        char_pattern = re.compile(r'<CHAR>(.*?)</CHAR>')
        matches = list(char_pattern.finditer(template))
        
        if not matches:
            return template
        
        new_template = template
        offset = 0 
        
        for match in matches:
            start, end = match.span()
            start += offset
            end += offset
            original_content = match.group(1)
            
            if match == max(matches, key=lambda m: len(m.group(1))):
                continue
            
            new_content = original_content
            for i, char in enumerate(original_content):
                special_char_info = self.identify_special_char(char)
                if special_char_info:
                    next_char = self.increment_special_char(char, style_key) 
                    new_content = new_content[:i] + next_char + new_content[i+1:]
            
            if new_content != original_content:
                replacement = f'<CHAR>{new_content}</CHAR>'
                new_template = new_template[:start] + replacement + new_template[end:]
                offset += len(replacement) - (end - start)
        
        return new_template
    
    def reset_counters(self):
        """특수 문자 카운터 초기화"""
        self.special_char_counters = {}