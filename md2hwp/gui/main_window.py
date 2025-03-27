# md2hwp/gui/main_window.py

import os
import io
import sys
import datetime
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QPushButton, QFileDialog,
                              QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QApplication,
                              QLabel, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent, QGuiApplication, QFont

from .status_handler import StatusHandler
from ..config import APP_NAME, OUTPUT_DIR_NAME, DEFAULT_ENCODING
from ..utils.file_utils import ensure_directory, generate_output_filename, save_text_file, open_file

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
        self.template_path = ""
        self.output_path = None
        self.user_selected_output_path = False
        self.is_converting = False

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v1.0")
        self.setGeometry(100, 100, 750, 600)
        self.setMinimumSize(600, 500)

        icon_folder = QIcon.fromTheme("folder-open", QIcon(":/qt-project.org/styles/commonstyle/images/diropen.png"))
        icon_clipboard = QIcon.fromTheme("edit-paste", QIcon(":/qt-project.org/styles/commonstyle/images/paste.png"))
        icon_save = QIcon.fromTheme("document-save-as", QIcon(":/qt-project.org/styles/commonstyle/images/save.png"))
        # 변환 아이콘 - 다른 버튼과 동일한 스타일의 아이콘 사용
        icon_convert = QIcon.fromTheme("document-send", QIcon(":/qt-project.org/styles/commonstyle/images/up.png"))
        
        # 아이콘이 없거나 테마가 불일치할 경우 대비
        if icon_convert.isNull():
            # 아이콘 없이 텍스트만 사용
            icon_convert = QIcon()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("MarkdownInput")
        self.text_edit.setPlaceholderText("여기에 마크다운을 붙여넣거나 .md 파일을 드롭하세요...")
        self.text_edit.setAcceptDrops(False)

        self.template_button = QPushButton(" 템플릿 선택")
        self.template_button.setIcon(icon_folder)
        self.clipboard_button = QPushButton(" 클립보드")
        self.clipboard_button.setIcon(icon_clipboard)
        self.save_button = QPushButton(" 저장 경로")
        self.save_button.setIcon(icon_save)
        # 변환 버튼 텍스트 수정
        self.convert_button = QPushButton(" 변환하기")
        self.convert_button.setIcon(icon_convert) # 아이콘 적용
        self.convert_button.setObjectName("ConvertButton")

        self.template_label = QLabel("템플릿: 선택되지 않음")
        self.template_label.setObjectName("FilePathLabel")
        self.output_label = QLabel("출력 경로: (기본 경로 사용)")
        self.output_label.setObjectName("FilePathLabel")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        file_status_layout = QHBoxLayout()
        file_status_layout.addWidget(self.template_label)
        file_status_layout.addStretch(1)
        file_status_layout.addWidget(self.output_label)
        main_layout.addLayout(file_status_layout)

        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        divider1.setObjectName("Divider")
        main_layout.addWidget(divider1)

        top_button_layout = QHBoxLayout()
        top_button_layout.setSpacing(10)
        top_button_layout.addWidget(self.template_button)
        top_button_layout.addWidget(self.clipboard_button)
        top_button_layout.addWidget(self.save_button)
        top_button_layout.addStretch(1)
        top_button_layout.addWidget(self.convert_button)
        main_layout.addLayout(top_button_layout)

        main_layout.addWidget(self.text_edit, 1)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        divider2.setObjectName("Divider")
        main_layout.addWidget(divider2)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_handler = StatusHandler(self.status_bar)
        self.status_handler.reset()

        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.save_button.clicked.connect(self.select_output_path)
        self.convert_button.clicked.connect(self.convert)

        self.setAcceptDrops(True)
        self.setup_overlay()

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = os.path.join(project_root, OUTPUT_DIR_NAME)
        ensure_directory(self.output_dir)

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
        if self.is_converting: return
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        file_path, _ = QFileDialog.getOpenFileName(self, "템플릿 파일 선택", template_dir if os.path.exists(template_dir) else "", "HWP 템플릿 파일 (*.hml)")
        if file_path:
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            if success:
                self.template_label.setText(f"템플릿: {os.path.basename(file_path)}")
                self.status_handler.set_success(f"템플릿 로드: {os.path.basename(file_path)}")
            else:
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

    def select_output_path(self):
        if self.is_converting: return
        default_dir = os.path.dirname(self.output_path) if self.user_selected_output_path and self.output_path else self.output_dir
        default_filename = os.path.basename(self.output_path) if self.user_selected_output_path and self.output_path else f"converted_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.hml"
        default_path = os.path.join(default_dir, default_filename)
        file_path, _ = QFileDialog.getSaveFileName(self, "HWPML 파일로 저장", default_path, "HWPML 파일 (*.hml)")
        if file_path:
            if not file_path.lower().endswith('.hml'): file_path += '.hml'
            self.output_path = file_path
            self.user_selected_output_path = True
            self.output_label.setText(f"출력 경로: {file_path}")
            self.status_handler.set_message(f"출력 경로 설정: {os.path.basename(file_path)}", 3000)

    def convert(self):
        if self.is_converting: return
        if not self.template_path or "선택되지 않음" in self.template_label.text():
            self.status_handler.set_warning("먼저 템플릿을 선택하세요.")
            return
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_handler.set_warning("변환할 텍스트가 없습니다.")
            return

        if self.user_selected_output_path and self.output_path:
            current_output_path = self.output_path
            current_output_dir = os.path.dirname(current_output_path)
        else:
            current_output_dir = self.output_dir
            current_output_path = generate_output_filename(current_output_dir)
            self.output_label.setText(f"출력 경로: {current_output_path}")
        ensure_directory(current_output_dir)

        self.is_converting = True
        self.set_ui_enabled(False)
        self.status_handler.set_message("변환 중...", timeout=0)
        QApplication.processEvents()

        try:
            hwpml_content = self.converter.convert_md_to_hwpml(md_text)
            save_text_file(current_output_path, hwpml_content, encoding=DEFAULT_ENCODING)
            self.status_handler.set_success(f"변환 완료: {os.path.basename(current_output_path)}")
            QTimer.singleShot(100, lambda: self.try_open_result(current_output_path, current_output_dir))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_handler.set_error(f"변환 중 오류 발생: {str(e)}")
        finally:
            self.is_converting = False
            QTimer.singleShot(200, lambda: self.set_ui_enabled(True))

    def set_ui_enabled(self, enabled: bool):
        self.template_button.setEnabled(enabled)
        self.clipboard_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.convert_button.setEnabled(enabled)
        self.text_edit.setEnabled(enabled)

    def try_open_result(self, file_path, folder_path):
        if not open_file(file_path):
            try:
                if sys.platform == "win32": os.startfile(folder_path)
                elif sys.platform == "darwin": import subprocess; subprocess.run(['open', folder_path])
                else: import subprocess; subprocess.run(['xdg-open', folder_path])
                self.status_handler.set_warning("파일 열기 실패. 저장 폴더를 열었습니다.", 5000)
            except Exception as folder_err:
                 self.status_handler.set_warning(f"파일/폴더 자동 열기 실패: {folder_err}", 5000)