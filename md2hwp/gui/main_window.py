# md2hwp/gui/main_window.py

import os
import io
import datetime
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QPushButton, QFileDialog,
                              QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QApplication,
                              QLabel)
from PySide6.QtCore import Qt, QEvent
from .status_handler import StatusHandler
from ..config import OUTPUT_DIR_NAME, DEFAULT_ENCODING
from ..utils.file_utils import ensure_directory, generate_output_filename, save_text_file, open_file

class MainWindow(QMainWindow):
    """GUI 메인 창 클래스"""

    def __init__(self, converter):
        super().__init__()

        self.setWindowTitle("마크다운 → HWP 변환기")
        self.setGeometry(100, 100, 600, 400)

        self.converter = converter
        self.template_path = ""
        self.output_path = None
        self.user_selected_output_path = False

        self.overlay_widget = None

        self.setup_ui()

    def setup_ui(self):
        """UI 구성 요소 설정"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setAcceptDrops(True)

        # 출력 디렉토리 설정
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(os.path.dirname(current_dir), OUTPUT_DIR_NAME)
        ensure_directory(self.output_dir)

        # 레이아웃 구성
        self.layout = QVBoxLayout(self.central_widget)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("여기에 마크다운 텍스트를 붙여넣거나 .md 파일을 드롭하세요")
        self.text_edit.setAcceptDrops(True)
        self.layout.addWidget(self.text_edit)

        # 버튼 레이아웃 구성
        self.button_layout = QHBoxLayout()

        self.template_button = QPushButton("템플릿 선택")
        self.clipboard_button = QPushButton("클립보드에서 불러오기")
        self.save_button = QPushButton("출력 경로 선택")
        self.convert_button = QPushButton("변환")

        self.button_layout.addWidget(self.template_button)
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.convert_button)

        self.layout.addLayout(self.button_layout)

        # 상태바 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_handler = StatusHandler(self.status_bar)
        self.status_handler.reset()

        # 버튼 이벤트 연결
        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.save_button.clicked.connect(self.select_output_path)
        self.convert_button.clicked.connect(self.convert)

        # 드래그 앤 드롭 설정
        self.setAcceptDrops(True)

        # 오버레이 위젯 설정
        self.overlay_widget = QLabel("여기에 파일을 드롭하세요\n(.md 또는 .hml)", self)
        self.overlay_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_widget.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: 3px dashed white;
            }
        """)
        self.overlay_widget.hide()
        self.overlay_widget.raise_()

    def resizeEvent(self, event):
        """창 크기가 변경될 때 오버레이 위젯 크기 조절"""
        super().resizeEvent(event)
        if self.overlay_widget:
            status_bar_height = self.status_bar.height() if self.status_bar else 0
            overlay_height = self.height() - status_bar_height
            self.overlay_widget.setGeometry(0, 0, self.width(), overlay_height)

    # 드래그 앤 드롭 관련 이벤트 핸들러
    def dragEnterEvent(self, event):
        """드래그된 항목이 창 영역에 들어왔을 때"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            valid_file_found = False
            for url in urls:
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    _, extension = os.path.splitext(file_path)
                    if extension.lower() in ['.md', '.hml']:
                        valid_file_found = True
                        break

            if valid_file_found:
                event.acceptProposedAction()
                self.overlay_widget.show()
                self.overlay_widget.raise_()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """드래그 중 창 영역을 벗어났을 때 오버레이 숨김"""
        self.overlay_widget.hide()
        event.accept()

    def dropEvent(self, event):
        """드롭 이벤트 처리"""
        self.overlay_widget.hide()

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()

            if os.path.isfile(file_path):
                _, extension = os.path.splitext(file_path)
                extension = extension.lower()

                if extension == ".md":
                    try:
                        with io.open(file_path, "r", encoding=DEFAULT_ENCODING) as f:
                            md_content = f.read()
                        self.text_edit.setPlainText(md_content)
                        self.status_handler.set_success(f"마크다운 파일 로드 완료: {os.path.basename(file_path)}")
                        event.acceptProposedAction()
                    except Exception as e:
                        self.status_handler.set_error(f"마크다운 파일 읽기 오류: {e}")
                        event.ignore()

                elif extension == ".hml":
                    self.template_path = file_path
                    success = self.converter.load_template(file_path)
                    if success:
                        self.status_handler.set_success(f"템플릿 로드 완료: {os.path.basename(file_path)}")
                        event.acceptProposedAction()
                    else:
                        self.status_handler.set_error("템플릿 로드 오류")
                        event.ignore()
                else:
                    self.status_handler.set_error(f"지원하지 않는 파일 형식입니다: {extension}")
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    # 파일 및 변환 관련 메서드
    def select_template(self):
        """템플릿 파일 선택 대화상자 표시"""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        if not os.path.exists(template_dir):
             template_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(self, "템플릿 파일 선택", template_dir, "HWP 템플릿 파일 (*.hml)")
        if file_path:
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            if success:
                self.status_handler.set_success(f"템플릿 로드 완료: {os.path.basename(file_path)}")
            else:
                self.status_handler.set_error("템플릿 로드 오류")

    def load_from_clipboard(self):
        """클립보드에서 마크다운 텍스트 불러오기"""
        clipboard = QApplication.clipboard()
        md_text = clipboard.text()
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_handler.set_message("클립보드에서 텍스트 로드 완료")
        else:
            self.status_handler.set_error("클립보드에 텍스트 없음")

    def select_output_path(self):
        """출력 파일 경로 선택"""
        default_dir = os.path.dirname(self.output_path) if self.output_path else self.output_dir
        default_filename = os.path.basename(self.output_path) if self.output_path else "converted.hml"
        default_path = os.path.join(default_dir, default_filename)

        file_path, _ = QFileDialog.getSaveFileName(self, "HWP 파일 저장", default_path, "HWP 파일 (*.hml)")
        if file_path:
            if not file_path.lower().endswith('.hml'):
                file_path += '.hml'
            self.output_path = file_path
            self.user_selected_output_path = True
            self.status_handler.set_message(f"출력 경로 설정: {file_path}")

    def convert(self):
        """마크다운을 HWPML로 변환하여 저장"""
        if not self.template_path:
            self.status_handler.set_error("먼저 템플릿을 선택하세요")
            return

        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_handler.set_error("변환할 텍스트가 없습니다")
            return

        # 출력 경로 결정
        if self.user_selected_output_path and self.output_path:
            current_output_path = self.output_path
            current_output_dir = os.path.dirname(current_output_path)
        else:
            current_output_dir = self.output_dir
            current_output_path = generate_output_filename(current_output_dir)

        ensure_directory(current_output_dir)

        self.status_handler.set_message("변환 중...")
        QApplication.processEvents()

        try:
            hwpml_content = self.converter.convert_md_to_hwpml(md_text)
            save_text_file(current_output_path, hwpml_content, encoding=DEFAULT_ENCODING)
            self.status_handler.set_success(f"변환 완료: {current_output_path}")

            # 파일 자동 실행 시도
            if open_file(current_output_path):
                pass
            else:
                try:
                    os.startfile(current_output_dir)
                    self.status_handler.set_message(f"파일 열기 실패. 저장 폴더를 열었습니다: {current_output_dir}")
                except Exception as folder_err:
                    self.status_handler.set_error(f"파일/폴더 자동 열기 실패: {folder_err}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_handler.set_error(f"변환 중 오류 발생: {str(e)}")