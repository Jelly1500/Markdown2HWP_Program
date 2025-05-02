"""
애플리케이션 설정 및 상수 관리 모듈
"""

# 애플리케이션 설정
APP_NAME = "마크다운 → HWP 변환기"
APP_VERSION = "1.0.0"

# 파일 관련 설정
DEFAULT_ENCODING = "utf-8"
OUTPUT_DIR_NAME = "convertedDocs"

# 테이블 관련 상수
MAX_TABLE_WIDTH = 42250
DEFAULT_CELL_WIDTH = 21125

# 특수 문자 매핑
SPECIAL_CHAR_MAPS = {
    'circled_numbers': {  # 원형 숫자 ① ② ③
        'range': (0x2460, 0x2473),  # U+2460 ~ U+2473
        'base_value': 1,  # ①(U+2460) = 1
        'max_count': 20
    },
    'parenthesized_numbers': {  # 괄호 숫자 ⑴ ⑵ ⑶
        'range': (0x2474, 0x2487),  # U+2474 ~ U+2487
        'base_value': 1,  # ⑴(U+2474) = 1
        'max_count': 20
    },
    'period_numbers': {  # 마침표 숫자 ⒈ ⒉ ⒊
        'range': (0x2488, 0x249B),  # U+2488 ~ U+249B
        'base_value': 1,  # ⒈(U+2488) = 1
        'max_count': 20
    },
    'circled_uppercase': {  # 원형 알파벳(대문자) Ⓐ Ⓑ Ⓒ
        'range': (0x24B6, 0x24CF),  # U+24B6 ~ U+24CF
        'base_value': ord('A'),  # Ⓐ(U+24B6) = A
        'max_count': 26
    },
    'circled_lowercase': {  # 원형 알파벳(소문자) ⓐ ⓑ ⓒ
        'range': (0x24D0, 0x24E9),  # U+24D0 ~ U+24E9
        'base_value': ord('a'),  # ⓐ(U+24D0) = a
        'max_count': 26
    },
    'roman_uppercase': {  # 로마 숫자(대문자) Ⅰ Ⅱ Ⅲ
        'range': (0x2160, 0x216B),  # U+2160 ~ U+216B
        'base_value': 1,  # Ⅰ(U+2160) = 1
        'max_count': 12
    },
    'roman_lowercase': {  # 로마 숫자(소문자) ⅰ ⅱ ⅲ
        'range': (0x2170, 0x217B),  # U+2170 ~ U+217B
        'base_value': 1,  # ⅰ(U+2170) = 1
        'max_count': 12
    },
    'arabic_numbers': {  # 아라비아 숫자 0 1 2 ... 9
        'range': (ord('0'), ord('9')),  # U+0030 ~ U+0039
        'base_value': 0,  # '0'(U+0030) = 0
        'max_count': 9  # 0부터 9까지 (최대값)
    }
}

# 스타일 매핑 순서
STYLE_MAPPING_ORDER = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul'
]

# 기본 글머리표
DEFAULT_BULLET_SYMBOL = "•"

LICENSE_SERVER_URL = "https://validate-license-xrrzxuc2hq-uc.a.run.app"
LICENSE_FILE_PATH = "license.dat" 
LICENSE_CHECK_INTERVAL_DAYS = 7 

