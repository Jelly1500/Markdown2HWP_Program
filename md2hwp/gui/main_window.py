# md2hwp/gui/main_window.py

import os
import io
import sys
import datetime
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QPushButton, QFileDialog,
                              QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QApplication,
                              QLabel, QSizePolicy, QFrame,QMenu)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent, QGuiApplication, QFont

from .status_handler import StatusHandler
from ..config import APP_NAME, OUTPUT_DIR_NAME, DEFAULT_ENCODING
from ..utils.file_utils import ensure_directory, generate_output_filename, save_text_file, open_file,open_file_explorer

# --- 수정된 QSS ---
UPDATED_IOS_LIKE_QSS = """
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
"""


class MainWindow(QMainWindow):
    """GUI 메인 창 클래스 (수정된 스타일 적용)"""

    def __init__(self, converter):
        super().__init__()

        self.converter = converter
        self.template_path = ""  # 선택된 템플릿 파일 경로
        self.output_path = None   # 마지막으로 변환된 HML 파일 경로
        self.is_converting = False

        # --- 기본 폴더 경로 설정 로직 ---
        try:
            current_file_path = os.path.abspath(__file__)
            gui_dir = os.path.dirname(current_file_path)
            app_dir = os.path.dirname(gui_dir)
            project_root = os.path.dirname(app_dir)

            self.default_output_dir = os.path.join(project_root, "convertedDocs")
            self.default_template_dir = os.path.join(project_root, "new_template")

            ensure_directory(self.default_output_dir)
            ensure_directory(self.default_template_dir)
        except Exception as e:
            print(f"경고: 기본 폴더 경로 설정 중 오류 발생 - {e}")
            self.default_output_dir = ensure_directory(os.path.abspath("convertedDocs"))
            self.default_template_dir = ensure_directory(os.path.abspath("new_template"))

        # UI 설정 및 스타일 적용
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v1.0")
        self.setGeometry(100, 100, 750, 600)
        self.setMinimumSize(600, 500)

        # --- 아이콘 로드 ---
        icon_folder = QIcon.fromTheme("folder-open", QIcon(":/qt-project.org/styles/commonstyle/images/diropen.png"))
        icon_clipboard = QIcon.fromTheme("edit-paste", QIcon(":/qt-project.org/styles/commonstyle/images/paste.png"))
        icon_convert = QIcon.fromTheme("document-send", QIcon(":/qt-project.org/styles/commonstyle/images/up.png"))
        icon_explore = QIcon.fromTheme("folder", QIcon(":/qt-project.org/styles/commonstyle/images/diropen.png"))

        # 아이콘 로드 실패 대비
        if icon_convert.isNull(): icon_convert = QIcon()
        if icon_explore.isNull(): icon_explore = QIcon()

        # --- 위젯 생성 ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("MarkdownInput")
        self.text_edit.setPlaceholderText("여기에 마크다운을 붙여넣거나 .md 파일을 드롭하세요...")
        self.text_edit.setAcceptDrops(False) # 드래그는 창 전체에서 처리

        self.template_button = QPushButton(" 템플릿 선택")
        self.template_button.setIcon(icon_folder)
        self.clipboard_button = QPushButton(" 클립보드")
        self.clipboard_button.setIcon(icon_clipboard)

        # 파일 위치 보기 버튼 및 메뉴
        self.file_explore_button = QPushButton(" 파일 위치")
        self.file_explore_button.setIcon(icon_explore)
        self.file_explore_menu = QMenu()
        self.show_output_action = self.file_explore_menu.addAction("변환 파일 위치")
        self.show_template_action = self.file_explore_menu.addAction("템플릿 파일 위치")
        self.file_explore_button.setMenu(self.file_explore_menu)

        self.convert_button = QPushButton(" 변환하기")
        self.convert_button.setIcon(icon_convert)
        self.convert_button.setObjectName("ConvertButton")

        # --- 라벨 생성 (output_label 텍스트 수정) ---
        self.template_label = QLabel("템플릿: 선택되지 않음")
        self.template_label.setObjectName("FilePathLabel")
        # 초기 라벨에 기본 출력 폴더 이름 표시
        self.output_label = QLabel(f"출력 폴더: {os.path.basename(self.default_output_dir)}")
        self.output_label.setObjectName("FilePathLabel")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # --- 레이아웃 설정 ---
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 파일 상태 라벨 레이아웃
        file_status_layout = QHBoxLayout()
        file_status_layout.addWidget(self.template_label)
        file_status_layout.addStretch(1)
        file_status_layout.addWidget(self.output_label)
        main_layout.addLayout(file_status_layout)

        # 구분선 1
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        divider1.setObjectName("Divider")
        main_layout.addWidget(divider1)

        # 상단 버튼 레이아웃 (파일 위치 버튼 추가)
        top_button_layout = QHBoxLayout()
        top_button_layout.setSpacing(10)
        top_button_layout.addWidget(self.template_button)
        top_button_layout.addWidget(self.clipboard_button)
        top_button_layout.addWidget(self.file_explore_button) # '저장 경로' 대신 '파일 위치' 버튼
        top_button_layout.addStretch(1)
        top_button_layout.addWidget(self.convert_button)
        main_layout.addLayout(top_button_layout)

        # 텍스트 편집 영역
        main_layout.addWidget(self.text_edit, 1) # stretch factor 1

        # 구분선 2
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        divider2.setObjectName("Divider")
        main_layout.addWidget(divider2)

        # 상태 표시줄 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_handler = StatusHandler(self.status_bar)
        # 생성자에서 경로 오류가 발생했을 수 있으므로, 여기서 초기 메시지 설정 가능
        self.status_handler.reset() # 기본 메시지 "준비" 설정

        # --- 시그널 연결 ---
        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.convert_button.clicked.connect(self.convert)
        # 메뉴 액션 시그널 연결
        self.show_output_action.triggered.connect(self.show_output_location)
        self.show_template_action.triggered.connect(self.show_template_location)

        # 드래그 앤 드롭 활성화 및 오버레이 설정
        self.setAcceptDrops(True)
        self.setup_overlay()


    def apply_styles(self):
        """스타일시트 적용"""
        self.setStyleSheet(UPDATED_IOS_LIKE_QSS) # 수정된 QSS 변수 사용

    def setup_overlay(self):
        """드래그 앤 드롭 피드백을 위한 오버레이 설정"""
        self.overlay_widget = QLabel(self)
        self.overlay_widget.setObjectName("OverlayLabel")
        self.overlay_widget.setText("템플릿(.hml) 또는 마크다운(.md) 파일 드롭")
        self.overlay_widget.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        status_bar_height = self.status_bar.height() if self.status_bar else 0
        self.overlay_widget.setGeometry(0, 0, self.width(), self.height() - status_bar_height)

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    _, extension = os.path.splitext(file_path)
                    if extension.lower() in ['.md', '.hml']:
                        event.acceptProposedAction()
                        self.overlay_widget.show()
                        self.overlay_widget.raise_()
                        return
            event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.overlay_widget.hide()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.overlay_widget.hide()
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.handle_dropped_file(file_path)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def handle_dropped_file(self, file_path):
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        if extension == ".md":
            try:
                with io.open(file_path, "r", encoding=DEFAULT_ENCODING) as f:
                    md_content = f.read()
                self.text_edit.setPlainText(md_content)
                self.status_handler.set_success(f"마크다운 파일 로드: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_handler.set_error(f"마크다운 파일 읽기 오류: {e}")
        elif extension == ".hml":
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            if success:
                self.template_label.setText(f"템플릿: {os.path.basename(file_path)}")
                self.status_handler.set_success(f"템플릿 로드: {os.path.basename(file_path)}")
            else:
                self.template_label.setText("템플릿: 선택되지 않음")
                self.status_handler.set_error("템플릿 로드 오류")
        else:
            self.status_handler.set_warning(f"지원하지 않는 파일 형식: {extension}")

    def select_template(self):
        """템플릿 선택 다이얼로그를 기본 템플릿 폴더에서 시작"""
        if self.is_converting: return

        # 파일 다이얼로그 시작 위치를 self.default_template_dir (new_template 폴더)로 지정
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "템플릿 파일 선택",
            self.default_template_dir, # 시작 디렉토리 변경
            "HWP 템플릿 파일 (*.hml)"
        )

        if file_path:
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            if success:
                # 성공 시 라벨 업데이트 및 상태 메시지 표시
                self.template_label.setText(f"템플릿: {os.path.basename(file_path)}")
                self.status_handler.set_success(f"템플릿 로드: {os.path.basename(file_path)}")
            else:
                # 실패 시 경로 및 라벨 초기화, 오류 메시지 표시
                self.template_path = "" # 실패 시 경로 초기화
                self.template_label.setText("템플릿: 선택되지 않음")
                self.status_handler.set_error("템플릿 로드 오류")
                
    def load_from_clipboard(self):
        if self.is_converting: return
        clipboard = QGuiApplication.clipboard()
        md_text = clipboard.text()
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_handler.set_message("클립보드에서 붙여넣기 완료", 3000)
        else:
            self.status_handler.set_warning("클립보드에 텍스트가 없습니다.")

    # --- 추가된 메서드 ---
    def show_output_location(self):
        """변환된 파일 위치 또는 기본 출력 폴더(convertedDocs)를 파일 탐색기에서 보여줌"""
        path_to_open = self.default_output_dir # 기본적으로 convertedDocs 폴더 경로

        # 마지막으로 변환된 파일 경로가 있고, 해당 파일이 실제로 존재하면
        if self.output_path and os.path.exists(self.output_path):
            # 해당 파일 경로를 사용 (탐색기에서 해당 파일이 선택됨)
            path_to_open = self.output_path
        # 그렇지 않으면(변환된 파일이 없거나, 경로가 있지만 파일이 삭제된 경우 등)
        # 기본 폴더 경로(self.default_output_dir)를 그대로 사용

        try:
            # 파일 탐색기 열기 시도 (파일 또는 폴더 경로 모두 처리 가능)
            open_file_explorer(path_to_open, handle_type='output')
        except FileNotFoundError:
             # open_file_explorer 내부에서도 체크하지만, 만약을 위해 여기서도 처리
             self.status_handler.set_error(f"경로를 찾을 수 없습니다: {os.path.basename(path_to_open)}")
        except Exception as e:
            # 기타 예외 처리 (권한 문제 등)
            self.status_handler.set_error(f"파일 탐색기 열기 실패: {str(e)}")

    # 5. show_template_location 메서드 (수정됨)
    def show_template_location(self):
        """선택된 템플릿 위치 또는 기본 템플릿 폴더(new_template)를 파일 탐색기에서 보여줌"""
        path_to_open = self.default_template_dir # 기본적으로 new_template 폴더 경로

        # 선택된 템플릿 경로가 있고, 해당 파일이 실제로 존재하면
        if self.template_path and os.path.exists(self.template_path):
            # 해당 파일 경로를 사용 (탐색기에서 해당 파일이 선택됨)
            path_to_open = self.template_path
        # 그렇지 않으면(선택된 템플릿이 없거나, 경로가 있지만 파일이 삭제된 경우 등)
        # 기본 폴더 경로(self.default_template_dir)를 그대로 사용

        try:
            # 파일 탐색기 열기 시도 (파일 또는 폴더 경로 모두 처리 가능)
            open_file_explorer(path_to_open, handle_type='template')
        except FileNotFoundError:
             self.status_handler.set_error(f"경로를 찾을 수 없습니다: {os.path.basename(path_to_open)}")
        except Exception as e:
            self.status_handler.set_error(f"파일 탐색기 열기 실패: {str(e)}")

    
    def convert(self):
        """마크다운을 HWPML로 변환하여 기본 출력 폴더에 저장"""
        if self.is_converting: return

        # 템플릿 선택 여부 확인
        if not self.template_path or "선택되지 않음" in self.template_label.text():
            self.status_handler.set_warning("먼저 템플릿을 선택하세요.")
            return
        # 변환할 텍스트 확인
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_handler.set_warning("변환할 텍스트가 없습니다.")
            return

        # --- 출력 경로 설정 (항상 기본 폴더 사용) ---
        current_output_dir = self.default_output_dir # convertedDocs 폴더 사용
        # 타임스탬프 기반 파일명 생성
        current_output_path = generate_output_filename(current_output_dir)
        # 마지막 출력 경로 업데이트
        self.output_path = current_output_path
        # 출력 라벨에 변환된 '파일' 이름 표시
        self.output_label.setText(f"출력 파일: {os.path.basename(current_output_path)}")
        # 폴더 생성은 생성자에서 이미 처리됨
        # ensure_directory(current_output_dir)
        # --- ---

        # UI 비활성화 및 상태 메시지 설정
        self.is_converting = True
        self.set_ui_enabled(False)
        self.status_handler.set_message("변환 중...", timeout=0) # timeout 0은 자동 숨김 없음
        QApplication.processEvents() # UI 업데이트 강제 적용

        try:
            # 변환 실행
            hwpml_content = self.converter.convert_md_to_hwpml(md_text)
            # 결과 파일 저장
            save_text_file(current_output_path, hwpml_content, encoding=DEFAULT_ENCODING)
            # 성공 메시지 표시
            self.status_handler.set_success(f"변환 완료: {os.path.basename(current_output_path)}")
            # 변환된 파일 자동 열기 시도 (약간의 지연 후)
            QTimer.singleShot(100, lambda: self.try_open_result(current_output_path, current_output_dir))
        except Exception as e:
            # 오류 발생 시 처리
            import traceback
            traceback.print_exc() # 콘솔에 상세 오류 출력
            self.status_handler.set_error(f"변환 중 오류 발생: {str(e)}")
        finally:
            # 변환 완료 또는 실패 후 UI 활성화 (약간의 지연 후)
            self.is_converting = False
            QTimer.singleShot(500, lambda: self.set_ui_enabled(True))

    def set_ui_enabled(self, enabled: bool):
        self.template_button.setEnabled(enabled)
        self.clipboard_button.setEnabled(enabled)
        self.file_explore_button.setEnabled(enabled)
        self.convert_button.setEnabled(enabled)
        self.text_edit.setEnabled(enabled)

    def try_open_result(self, file_path, folder_path):
        # 파일 열기 실패 시 폴더 열기 (기존 코드 유지)
        if not open_file(file_path):
            try:
                # open_file_explorer 를 사용하여 폴더 열기 시도
                open_file_explorer(folder_path) # 파일 경로나 폴더 경로 모두 처리 가능
                self.status_handler.set_warning("파일 자동 열기 실패. 저장 폴더를 열었습니다.", 5000)
            except Exception as folder_err:
                 self.status_handler.set_warning(f"파일/폴더 자동 열기 실패: {folder_err}", 5000)

