"""
애플리케이션 스타일시트 정의 모듈
"""

# iOS 스타일 기본 QSS
IOS_LIKE_QSS = """
/* 전역 설정: 기본 폰트 및 배경색 */
QWidget {
    font-family: ".AppleSystemUIFont", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 10pt;
    color: #1d1d1f; /* 기본 텍스트 검은색 계열 */
}

QMainWindow {
    background-color: #ffffff; /* 메인 창 배경 흰색으로 변경 */
}

/* 텍스트 편집 영역 (코드 블록 느낌) */
QTextEdit#MarkdownInput {
    background-color: #f0f2f5; /* 연한 회색 배경 (코드 블록 느낌) */
    border: 1px solid #e0e0e0; /* 약간 더 연한 테두리 */
    border-radius: 6px; /* 둥근 모서리 약간 줄임 */
    padding: 12px;
    font-size: 10.5pt; /* 폰트 크기 미세 조정 */
    color: #1d1d1f; /* 어두운 배경에 맞춰 텍스트 색상 확인 */
    /* 코드 블록 느낌을 위해 고정폭 글꼴 사용 (선택 사항) */
    /* font-family: "Consolas", "Monaco", monospace; */
}
QTextEdit#MarkdownInput:focus {
    border: 1px solid #007aff; /* 포커스 시 파란색 테두리 유지 */
    background-color: #f8f9fa; /* 포커스 시 배경 살짝 밝게 (선택 사항) */
}
QTextEdit#MarkdownInput:disabled {
    background-color: #f8f8f8; /* 비활성화 시 배경 */
    color: #a0a0a0;
}

/* 버튼 공통 스타일 */
QPushButton {
    border: none;
    padding: 9px 16px; /* 패딩 미세 조정 */
    border-radius: 6px; /* 둥근 모서리 */
    font-size: 10pt;
    font-weight: 500;
    min-height: 34px;
    min-width: 90px;
    outline: none;
}
QPushButton:disabled {
    background-color: #e0e0e0;
    color: #a0a0a0;
}

/* 보조 버튼 (템플릿, 로드, 저장) */
QPushButton { /* 기본값 */
    background-color: #f0f2f5; /* 텍스트 영역 배경과 유사한 회색 */
    color: #1d1d1f; /* 텍스트 색상 검은색 계열로 변경 */
}
QPushButton:hover {
    background-color: #e2e5e8;
}
QPushButton:pressed {
    background-color: #d8dde0;
}

/* 주요 액션 버튼 (변환) - 모던 스타일 */
QPushButton#ConvertButton {
    background-color: #f0f2f5; /* 다른 버튼과 같은 배경색 */
    color: #1d1d1f; /* 다른 버튼과 같은 텍스트 색상 */
    font-weight: 500; /* 약간 더 굵게 */
    font-size: 10pt; /* 다른 버튼과 동일한 크기 */
    padding: 9px 16px; /* 다른 버튼과 동일한 패딩 */
    min-height: 34px;
    border-radius: 6px; /* 다른 버튼과 동일한 모서리 */
}
QPushButton#ConvertButton:hover {
    background-color: #e2e5e8; /* 다른 버튼과 동일한 호버 색상 */
}
QPushButton#ConvertButton:pressed {
    background-color: #d8dde0; /* 다른 버튼과 동일한 프레스 색상 */
}
QPushButton#ConvertButton:disabled {
    background-color: #e0e0e0;
    color: #a0a0a0;
    border-bottom: 2px solid #a0a0a0;
}

/* 상태 표시 라벨 (템플릿, 출력 경로) */
QLabel#FilePathLabel {
    font-size: 9pt;
    color: #6e6e73;
    padding-top: 3px;
}

/* 상태 표시줄 */
QStatusBar {
    background-color: #ffffff; /* 메인 배경과 동일 (흰색) */
    border-top: 1px solid #e5e5e5; /* 상단 구분선 */
    color: #6e6e73;
    font-size: 9pt;
    padding-left: 10px;
}
QStatusBar::item {
    border: none;
}

/* 구분선 */
QFrame#Divider {
    border: none;
    border-top: 1px solid #f0f0f0; /* 배경이 흰색이므로 더 연하게 */
    margin-top: 15px;
    margin-bottom: 15px;
}

/* 드래그 오버레이 라벨 - 옅은 회색으로 변경 */
QLabel#OverlayLabel {
    background-color: rgba(220, 220, 220, 0.85); /* 반투명 연한 회색 */
    color: #333333; /* 어두운 텍스트 색상 */
    font-size: 20px;
    font-weight: 500;
    border: 2px dashed #a0a0a0; /* 회색 점선 테두리 */
    border-radius: 8px;
    qproperty-alignment: 'AlignCenter';
}

/* 헤딩 변경 버튼 스타일 */
QPushButton[objectName^="HeadingButton"],
QPushButton[objectName^="SubHeadingButton"] {
    min-width: 28px; /* 최소 너비 조정 */
    max-width: 40px; /* 최대 너비 조정 */
    padding: 3px;    /* 패딩 조정 */
    font-size: 9pt;
    background-color: rgba(240, 242, 245, 0.8); /* 약간 투명하게 */
    color: #1d1d1f;
    border-radius: 4px; /* 모서리 둥글게 */
}
QPushButton[objectName^="HeadingButton"]:checked {
    background-color: rgba(208, 208, 213, 0.9); /* 눌린 상태 배경색 */
    border: 1px solid #a0a0a5;
}
QPushButton[objectName^="SubHeadingButton"]:hover {
    background-color: rgba(226, 229, 232, 0.8);
}
QPushButton[objectName^="SubHeadingButton"]:pressed {
    background-color: rgba(216, 221, 224, 0.8);
}

/* 헤딩 버튼 컨테이너 */
QWidget#HeadingButtonContainer {
    background-color: transparent;
}
QWidget#SubHeadingButtonContainer {
    background-color: transparent;
}
"""

# 다크 모드 스타일 (향후 확장용)
DARK_MODE_QSS = """
/* 다크 모드 스타일 - 향후 구현 */
QWidget {
    font-family: ".AppleSystemUIFont", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 10pt;
    color: #f5f5f7;
    background-color: #1d1d1f;
}

QMainWindow {
    background-color: #1d1d1f;
}
""" 