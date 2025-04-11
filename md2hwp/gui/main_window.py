# md2hwp/gui/main_window.py
import os
import io
import sys
import datetime
import re
# QtWidgets에서 필요한 클래스들을 가져옵니다.
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QPushButton, QFileDialog, # <- QTextEdit 여기로 이동
                              QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QApplication,
                              QLabel, QSizePolicy, QFrame, QMenu, QMessageBox,
                              QGroupBox, QToolButton, QInputDialog)
from PySide6.QtCore import Qt, QEvent, QTimer, QRegularExpression, QPropertyAnimation, QEasingCurve, QSize
# QtGui에서 필요한 클래스들을 가져옵니다.
from PySide6.QtGui import (QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent,
                           QGuiApplication, QFont, QTextCursor,      # <- QTextEdit 제거
                           QTextCharFormat, QTextDocument)
from .status_handler import StatusHandler
from ..config import APP_NAME, OUTPUT_DIR_NAME, DEFAULT_ENCODING
from ..utils.file_utils import ensure_directory, generate_output_filename, save_text_file, open_file, open_file_explorer
# 스타일시트 가져오기
from .styles import IOS_LIKE_QSS


def get_base_path():
    """ 실행 환경에 따라 기본 경로를 반환 (빌드된 .exe 또는 소스코드) """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller 등으로 빌드된 경우 (.exe)
        # sys.executable은 .exe 파일의 *절대 경로*입니다.
        return os.path.dirname(sys.executable)
    else:
        # 일반 파이썬 환경에서 실행된 경우 (소스코드)
        # 현재 파일(main_window.py) 기준 상위-상위 폴더를 기준으로 설정
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_PATH = get_base_path()
class MainWindow(QMainWindow):
    """GUI 메인 창 클래스 (헤딩 및 포맷 변경 기능 추가)"""

    def __init__(self, converter):
        super().__init__()

        self.converter = converter
        self.template_path = ""
        self.output_path = None
        self.is_converting = False

        # --- 기본 폴더 및 템플릿 경로 설정 ---
        try:
            self.default_output_dir = os.path.join(BASE_PATH, "convertedDocs")
            self.default_template_dir = os.path.join(BASE_PATH, "new_template") # 폴더 이름 수정 (template -> new_template)
            self.default_template_file = os.path.join(self.default_template_dir, "템플릿문서.hml")

            ensure_directory(self.default_output_dir)
        except Exception as e:
            print(f"경고: 기본 폴더 경로 설정 중 오류 발생 - {e}")
            self.default_output_dir = ensure_directory(os.path.abspath("convertedDocs"))
            self.default_template_dir = ensure_directory(os.path.abspath("new_template"))
            self.default_template_file = os.path.join(self.default_template_dir, "템플릿문서.hml")

        # --- 상태 변수 추가 ---
        self.selected_heading_level = 0 # 현재 선택된 대상 헤딩 레벨 (0은 선택 없음)
        self.selected_format_type = None # 현재 선택된 포맷 타입 ('bold', 'italic', 'list')
        self.active_delete_button = None # 현재 활성화된 포맷 삭제 버튼

        # UI 설정 및 스타일 적용
        self.setup_ui()
        self.apply_styles()

        # --- 프로그램 시작 시 기본 템플릿 로드 ---
        self.load_default_template()

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v1.0")
        self.setGeometry(100, 100, 900, 650) # 너비 확장, 높이 약간 늘림
        self.setMinimumSize(750, 550) # 최소 너비도 증가

        # --- 아이콘 로드 (기존 코드 유지) ---
        icon_folder = QIcon.fromTheme("folder-open", QIcon(":/qt-project.org/styles/commonstyle/images/diropen.png"))
        icon_clipboard = QIcon.fromTheme("edit-paste", QIcon(":/qt-project.org/styles/commonstyle/images/paste.png"))
        icon_convert = QIcon.fromTheme("document-send", QIcon(":/qt-project.org/styles/commonstyle/images/up.png"))
        icon_explore = QIcon.fromTheme("folder", QIcon(":/qt-project.org/styles/commonstyle/images/diropen.png"))
        if icon_convert.isNull(): icon_convert = QIcon()
        if icon_explore.isNull(): icon_explore = QIcon()

        # --- 위젯 생성 (기존 + 추가) ---
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
        self.file_explore_button = QPushButton(" 파일 위치")
        self.file_explore_button.setIcon(icon_explore)
        self.file_explore_menu = QMenu()
        self.show_output_action = self.file_explore_menu.addAction("변환 파일 위치")
        self.show_template_action = self.file_explore_menu.addAction("템플릿 파일 위치")
        self.file_explore_button.setMenu(self.file_explore_menu)
        self.convert_button = QPushButton(" 변환하기")
        self.convert_button.setIcon(icon_convert)
        self.convert_button.setObjectName("ConvertButton")

        self.template_label = QLabel("템플릿: 선택되지 않음")
        self.template_label.setObjectName("FilePathLabel")
        self.output_label = QLabel(f"출력 폴더: {os.path.basename(self.default_output_dir)}")
        self.output_label.setObjectName("FilePathLabel")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # 새 템플릿 생성 메뉴 추가
        self.new_template_menu = QMenu("새 템플릿 생성")
        self.new_template_menu.addAction("기본 문서 설정이 적용된 템플릿 생성", self.create_default_template)
        self.new_template_menu.addAction("원본 문서 설정이 적용된 템플릿 생성", self.create_template_from_source)

        # 새 템플릿 생성 버튼 추가
        self.new_template_button = QToolButton()
        self.new_template_button.setText("새 템플릿 생성")
        self.new_template_button.setIcon(icon_folder)
        self.new_template_button.setMenu(self.new_template_menu)
        self.new_template_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.new_template_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.new_template_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # --- 레이아웃 설정 ---
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
        top_button_layout.addWidget(self.new_template_button)  # 새 템플릿 생성 버튼 추가
        top_button_layout.addWidget(self.template_button)
        top_button_layout.addWidget(self.clipboard_button)
        top_button_layout.addWidget(self.file_explore_button)
        top_button_layout.addStretch(1)
        top_button_layout.addWidget(self.convert_button)
        main_layout.addLayout(top_button_layout)

        # --- 헤딩 변경 버튼 영역 추가 (텍스트 편집기 내부로 이동) ---
        # 헤딩 버튼 컨테이너 생성
        self.heading_button_container = QWidget()
        self.heading_button_container.setObjectName("HeadingButtonContainer")
        heading_button_layout = QHBoxLayout(self.heading_button_container)
        heading_button_layout.setContentsMargins(5, 5, 5, 5)
        heading_button_layout.setSpacing(5)

        self.heading_buttons = {}
        for i in range(1, 7):
            btn = QPushButton(f"H{i}")
            btn.setFixedSize(32, 25) # 크기 축소
            btn.setObjectName(f"HeadingButton{i}")
            btn.setCheckable(True)
            btn.clicked.connect(self.on_heading_button_clicked)
            heading_button_layout.addWidget(btn)
            self.heading_buttons[i] = btn

        # --- 포맷 변경 버튼 영역 추가 ---
        self.format_button_container = QWidget()
        self.format_button_container.setObjectName("FormatButtonContainer")
        format_button_layout = QHBoxLayout(self.format_button_container)
        format_button_layout.setContentsMargins(5, 5, 5, 5)
        format_button_layout.setSpacing(5)

        self.format_buttons = {}
        self.format_delete_buttons = {}
        format_types = {'bold': 'B', 'italic': 'I', 'list': 'L'} # 타입과 버튼 텍스트

        for fmt_type, btn_text in format_types.items():
            btn = QPushButton(btn_text)
            btn.setFixedSize(32, 25)
            btn.setObjectName(f"FormatButton{fmt_type.capitalize()}")
            btn.setCheckable(True)
            btn.clicked.connect(self.on_format_button_clicked)
            format_button_layout.addWidget(btn)
            self.format_buttons[fmt_type] = btn

            # 해당 포맷 삭제 버튼 생성
            del_btn = QPushButton("X")
            del_btn.setFixedSize(32, 25)
            del_btn.setObjectName(f"DeleteFormatButton{fmt_type.capitalize()}")
            del_btn.setToolTip(f"모든 {fmt_type} 서식 삭제")
            del_btn.clicked.connect(self.on_delete_format_button_clicked)
            self.format_delete_buttons[fmt_type] = del_btn

        # 하위 포맷 삭제 버튼 그룹 (초기에는 숨김)
        self.sub_format_widget = QWidget()
        self.sub_format_widget.setObjectName("SubFormatButtonContainer")
        self.sub_format_layout = QHBoxLayout(self.sub_format_widget)
        self.sub_format_layout.setContentsMargins(0, 0, 0, 0) # 여백 최소화
        self.sub_format_layout.setSpacing(5)
        # 생성된 삭제 버튼들을 하위 레이아웃에 추가 (초기에는 모두 숨김)
        for fmt_type in format_types:
            self.sub_format_layout.addWidget(self.format_delete_buttons[fmt_type])
            self.format_delete_buttons[fmt_type].hide()

        self.sub_format_widget.hide()
        self.sub_format_widget.setFixedHeight(0) # 애니메이션 위해 초기 높이 0


        # 하위 변경 옵션 버튼 그룹 (초기에는 숨김) - 헤딩용
        self.sub_heading_widget = QWidget()
        self.sub_heading_widget.setObjectName("SubHeadingButtonContainer") # 이름 유지
        self.sub_heading_layout = QHBoxLayout(self.sub_heading_widget)
        self.sub_heading_layout.setContentsMargins(5, 5, 5, 5)
        self.sub_heading_layout.setSpacing(5)

        self.sub_heading_buttons = {}
        for i in range(1, 7):
            btn = QPushButton(f"→{i}") # 화살표 추가
            btn.setFixedSize(32, 25) # 크기 축소
            btn.setObjectName(f"SubHeadingButton{i}")
            btn.clicked.connect(self.on_sub_heading_button_clicked)
            self.sub_heading_layout.addWidget(btn)
            self.sub_heading_buttons[i] = btn

        # 헤딩 삭제 버튼 추가
        self.delete_heading_button = QPushButton("X")
        self.delete_heading_button.setFixedSize(32, 25)
        self.delete_heading_button.setObjectName("DeleteHeadingButton")
        self.delete_heading_button.setToolTip("선택된 레벨의 모든 헤딩 마커 삭제") # 툴팁 수정
        self.delete_heading_button.clicked.connect(self.on_delete_heading_button_clicked)
        self.sub_heading_layout.addWidget(self.delete_heading_button)

        self.sub_heading_widget.hide() # 초기 숨김
        self.sub_heading_widget.setFixedHeight(0) # 애니메이션을 위한 초기 높이

        # 텍스트 편집 영역 (메인 레이아웃에 추가)
        main_layout.addWidget(self.text_edit, 1) # stretch factor 1

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        divider2.setObjectName("Divider")
        main_layout.addWidget(divider2)

        # 상태 표시줄 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_handler = StatusHandler(self.status_bar)
        self.status_handler.reset()

        # --- 시그널 연결 ---
        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.convert_button.clicked.connect(self.convert)
        self.show_output_action.triggered.connect(self.show_output_location)
        self.show_template_action.triggered.connect(self.show_template_location)

        # 드래그 앤 드롭 활성화 및 오버레이 설정
        self.setAcceptDrops(True)
        self.setup_overlay()

        # 텍스트 편집기에 헤딩 버튼 추가
        self.setup_heading_buttons_in_editor()

    def apply_styles(self):
        """스타일시트 적용"""
        self.setStyleSheet(IOS_LIKE_QSS)

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
            self.set_template(file_path) # 템플릿 설정 함수 호출
        else:
            self.status_handler.set_warning(f"지원하지 않는 파일 형식: {extension}")

    # --- 기본 템플릿 로드 메서드 (수정) ---
    def load_default_template(self):
        """프로그램 시작 시 기본 템플릿을 로드합니다."""
        if os.path.exists(self.default_template_file):
            if self.set_template(self.default_template_file): # 템플릿 설정 함수 사용
                 self.status_handler.set_message(f"기본 템플릿 '{os.path.basename(self.default_template_file)}' 로드 완료", 3000)
            else:
                 self.status_handler.set_error("기본 템플릿 로드 중 오류 발생. 수동으로 선택해주세요.")
        else:
            self.template_path = ""
            self.template_label.setText("템플릿: 선택되지 않음")
            self.status_handler.set_warning("기본 템플릿 파일을 찾을 수 없습니다. '템플릿 선택' 버튼을 이용하세요.")

    # --- 템플릿 설정 함수 추가 ---
    def set_template(self, file_path):
        """주어진 경로의 템플릿을 로드하고 UI를 업데이트합니다."""
        success = self.converter.load_template(file_path)
        if success:
            self.template_path = file_path
            self.template_label.setText(f"템플릿: {os.path.basename(file_path)}")
            # 템플릿 변경 시 헤딩 변경 상태 초기화
            self.reset_heading_change_state()
            return True
        else:
            self.template_path = "" # 실패 시 경로 초기화
            self.template_label.setText("템플릿: 선택되지 않음")
            self.status_handler.set_error(f"템플릿 로드 오류: {os.path.basename(file_path)}")
            # 템플릿 로드 실패 시 헤딩 변경 상태 초기화
            self.reset_heading_change_state()
            return False

    def select_template(self):
        """템플릿 선택 다이얼로그"""
        if self.is_converting: return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "템플릿 파일 선택", self.default_template_dir, "HWP 템플릿 파일 (*.hml)"
        )
        if file_path:
            if self.set_template(file_path): # 템플릿 설정 함수 사용
                self.status_handler.set_success(f"템플릿 로드: {os.path.basename(file_path)}")
            # set_template 함수 내에서 실패 처리를 하므로 여기서는 추가 처리 필요 없음

    def load_from_clipboard(self):
        if self.is_converting: return
        clipboard = QGuiApplication.clipboard()
        md_text = clipboard.text()
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_handler.set_message("클립보드에서 붙여넣기 완료", 3000)
        else:
            self.status_handler.set_warning("클립보드에 텍스트가 없습니다.")

    def show_output_location(self):
        """변환된 파일 위치 또는 기본 출력 폴더 열기"""
        path_to_open = self.default_output_dir
        if self.output_path and os.path.exists(self.output_path):
            path_to_open = self.output_path
        try:
            open_file_explorer(path_to_open, handle_type='output')
        except FileNotFoundError:
             self.status_handler.set_error(f"경로를 찾을 수 없습니다: {os.path.basename(path_to_open)}")
        except Exception as e:
            self.status_handler.set_error(f"파일 탐색기 열기 실패: {str(e)}")

    def show_template_location(self):
        """선택된 템플릿 위치 또는 기본 템플릿 폴더 열기"""
        path_to_open = self.default_template_dir
        if self.template_path and os.path.exists(self.template_path):
            path_to_open = self.template_path
        try:
            open_file_explorer(path_to_open, handle_type='template')
        except FileNotFoundError:
             self.status_handler.set_error(f"경로를 찾을 수 없습니다: {os.path.basename(path_to_open)}")
        except Exception as e:
            self.status_handler.set_error(f"파일 탐색기 열기 실패: {str(e)}")

    def convert(self):
        """마크다운을 HWPML로 변환"""
        if self.is_converting: return
        if not self.template_path:
            self.status_handler.set_warning("템플릿이 로드되지 않았습니다. 템플릿을 선택하세요.")
            return
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_handler.set_warning("변환할 텍스트가 없습니다.")
            return

        current_output_dir = self.default_output_dir
        current_output_path = generate_output_filename(current_output_dir)
        self.output_path = current_output_path
        self.output_label.setText(f"출력 파일: {os.path.basename(current_output_path)}")

        self.is_converting = True
        self.set_ui_enabled(False)
        self.status_handler.set_message("변환 중...", timeout=0)
        QApplication.processEvents()

        try:
            hwpml_content = self.converter.convert_md_to_hwpml(md_text)
            save_text_file(current_output_path, hwpml_content, encoding=DEFAULT_ENCODING)
            
            # HML을 HWP로 변환
            from md2hwp.utils.hwp_to_hml import convert_hml_to_hwp
            hwp_path = os.path.splitext(current_output_path)[0] + ".hwp"
            
            # HML을 HWP로 변환
            convert_hml_to_hwp(current_output_path)
            
            # HML 파일 삭제
            if os.path.exists(current_output_path):
                os.remove(current_output_path)
            
            # 출력 경로를 HWP 파일로 업데이트
            self.output_path = hwp_path
            self.status_handler.set_success(f"변환 완료: {os.path.basename(hwp_path)}")
            QTimer.singleShot(100, lambda: self.try_open_result(hwp_path, current_output_dir))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_handler.set_error(f"변환 중 오류 발생: {str(e)}")
        finally:
            self.is_converting = False
            QTimer.singleShot(500, lambda: self.set_ui_enabled(True))

    def set_ui_enabled(self, enabled: bool):
        self.template_button.setEnabled(enabled)
        self.clipboard_button.setEnabled(enabled)
        self.file_explore_button.setEnabled(enabled)
        self.convert_button.setEnabled(enabled)
        self.text_edit.setEnabled(enabled)
        # 헤딩 변경 버튼들도 활성화/비활성화
        for btn in self.heading_buttons.values():
            btn.setEnabled(enabled)
        # 포맷 변경 버튼들도 활성화/비활성화
        for btn in self.format_buttons.values():
            btn.setEnabled(enabled)
        # 하위 버튼들은 상태에 따라 관리되므로 여기서 직접 제어하지 않음
        if not enabled:
            self.reset_heading_change_state() # 비활성화 시 상태 초기화
            self.reset_format_change_state() # 포맷 상태도 초기화


    def try_open_result(self, file_path, folder_path):
        if not open_file(file_path):
            try:
                open_file_explorer(folder_path)
                self.status_handler.set_warning("파일 자동 열기 실패. 저장 폴더를 열었습니다.", 5000)
            except Exception as folder_err:
                 self.status_handler.set_warning(f"파일/폴더 자동 열기 실패: {folder_err}", 5000)


    # --- 헤딩 및 포맷 변경 관련 메서드 ---

    def highlight_content(self, level=0, format_type=None):
        """지정된 레벨의 헤딩 또는 특정 포맷을 하이라이트합니다."""
        self.clear_highlights()
        if level == 0 and format_type is None:
            return

        cursor = QTextCursor(self.text_edit.document())
        selections = []

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 180)) # 연한 노란색 배경

        doc = self.text_edit.document()
        regex = None

        if level > 0:
            # 헤딩 하이라이트
            pattern = r'^' + '#' * level + r' '
            regex = QRegularExpression(pattern)
            cursor = doc.find(regex, cursor)
            while not cursor.isNull():
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                # 헤딩 마커 부분만 선택 ('## ' 부분)
                selection.cursor.clearSelection()
                # 패턴 시작 위치부터 끝 위치까지 선택
                start_pos = cursor.anchor() # find 결과의 시작 위치
                end_pos = cursor.position() # find 결과의 끝 위치
                selection.cursor.setPosition(start_pos)
                selection.cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
                selection.format = highlight_format
                selections.append(selection)
                cursor = doc.find(regex, cursor) # 다음 찾기

        elif format_type:
            # 포맷 하이라이트
            if format_type == 'bold':
                # **text** 또는 __text__ (non-greedy)
                pattern = r'(\*\*|__)(.+?)\1'
            elif format_type == 'italic':
                # *text* 또는 _text_ (non-greedy, 단 ** 또는 __ 내부의 *나 _는 제외 필요 - 복잡도 증가)
                pattern = r'(?<![\*_])(\*|_)(?![\*_])(.+?)\1(?!\1)' # **bold** 안의 *italic* 제외 시도
            elif format_type == 'list':
                # *, -, +, 1. 등으로 시작하는 줄
                pattern = r'^[ \t]*([\*\-\+]|\d+\.)[ \t]+'
            else:
                return # 지원하지 않는 타입

            regex = QRegularExpression(pattern)
            if format_type == 'list':
                 regex.setPatternOptions(QRegularExpression.PatternOption.MultilineOption)

            cursor = doc.find(regex, cursor)
            while not cursor.isNull():
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.cursor.clearSelection()
                start_pos = cursor.anchor()
                end_pos = cursor.position()
                selection.cursor.setPosition(start_pos)
                selection.cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
                selection.format = highlight_format
                selections.append(selection)
                cursor = doc.find(regex, cursor) # 다음 찾기

        self.text_edit.setExtraSelections(selections)

    def clear_highlights(self):
        """모든 추가 선택(하이라이트)을 제거합니다."""
        self.text_edit.setExtraSelections([])

    def reset_heading_change_state(self):
        """헤딩 변경 관련 상태를 초기화합니다."""
        # 헤딩 관련 상태만 초기화, 하이라이트는 공통 clear_highlights 사용
        if self.selected_heading_level > 0:
            self.clear_highlights()
            self.animate_sub_heading_widget(False)
            if self.selected_heading_level in self.heading_buttons:
                 if self.heading_buttons[self.selected_heading_level].isChecked():
                     self.heading_buttons[self.selected_heading_level].setChecked(False)
            self.selected_heading_level = 0
            self.delete_heading_button.setVisible(False)

    def reset_format_change_state(self):
        """포맷 변경 관련 상태를 초기화합니다."""
        # 포맷 관련 상태만 초기화, 하이라이트는 공통 clear_highlights 사용
        if self.selected_format_type:
            self.clear_highlights()
            if self.selected_format_type in self.format_buttons:
                 if self.format_buttons[self.selected_format_type].isChecked():
                     self.format_buttons[self.selected_format_type].setChecked(False)
            self.selected_format_type = None
            self.active_delete_button = None
            self.animate_sub_format_widget(False) # 하위 포맷 버튼 컨테이너 숨김


    def animate_widget_height(self, widget, show=True, target_height=35, duration=200):
        """지정된 위젯의 높이를 애니메이션으로 조절합니다. (Simplified)"""
        start_value = widget.height()
        end_value = target_height if show else 0

        # 애니메이션 전 설정
        if show:
            widget.show() # 먼저 보이게 설정
            # widget.raise_() # 위로 올리기 -> resize 이벤트에서 최종적으로 처리

        # 애니메이션 생성 및 설정
        animation = QPropertyAnimation(widget, b"maximumHeight")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 애니메이션 완료 시 처리
        if not show:
            # finished 시그널은 QPropertyAnimation이 완료된 후 자동으로 호출됨
            # 연결된 슬롯에서 hide()를 호출하도록 함
            # 기존 연결이 있다면 제거 후 새로 연결 (중복 방지)
            try:
                 animation.finished.disconnect()
            except RuntimeError:
                 pass # 연결이 없으면 무시
            animation.finished.connect(widget.hide)
        else:
             # 보이는 애니메이션 완료 후 최소 높이 설정
             try:
                 animation.finished.disconnect()
             except RuntimeError:
                 pass
             animation.finished.connect(lambda: widget.setMinimumHeight(target_height))


        # 기존 애니메이션 중지 (간단하게)
        if hasattr(widget, '_height_animation') and widget._height_animation:
            # Check if the C++ object is still valid before stopping
            try:
                if widget._height_animation.state() == QPropertyAnimation.State.Running:
                    widget._height_animation.stop()
            except RuntimeError:
                pass # Object might be deleted
        widget._height_animation = animation
        # Use DeleteWhenStopped to let Qt manage the animation object lifecycle
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


    def animate_sub_heading_widget(self, show=True):
        """하위 헤딩 버튼 컨테이너를 애니메이션으로 표시/숨김"""
        self.animate_widget_height(self.sub_heading_widget, show)

    def animate_sub_format_widget(self, show=True):
        """하위 포맷 삭제 버튼 컨테이너를 애니메이션으로 표시/숨김"""
        self.animate_widget_height(self.sub_format_widget, show)


    def on_heading_button_clicked(self):
        """H1-H6 버튼 클릭 시 호출됩니다."""
        clicked_button = self.sender()
        target_level = 0
        for level, btn in self.heading_buttons.items():
            if btn == clicked_button:
                target_level = level
                # 다른 버튼들은 체크 해제
                for other_level, other_btn in self.heading_buttons.items():
                    if other_level != target_level:
                        if other_btn.isChecked(): # 불필요한 호출 방지
                            other_btn.setChecked(False)
                break

        # 버튼이 체크 해제된 경우 (다시 클릭)
        if not clicked_button.isChecked():
            self.reset_heading_change_state() # 헤딩 상태만 리셋
            return

        # 이전에 다른 버튼이 선택된 상태였다면 초기화
        if self.selected_heading_level != 0 and self.selected_heading_level != target_level:
            pass # 그냥 진행하여 새 레벨로 덮어씀

        # 다른 활성 상태 초기화 (포맷 버튼 및 하위 위젯)
        self.reset_format_change_state()

        # 현재 상태 업데이트 및 하이라이트
        self.selected_heading_level = target_level
        self.highlight_content(level=target_level) # 통합된 하이라이트 함수 사용

        # 하위 버튼 및 삭제 버튼 표시 (자기 자신 제외)
        num_visible_buttons = 0
        button_width = 32
        spacing = 5
        for level, btn in self.sub_heading_buttons.items():
            is_visible = (level != target_level)
            btn.setVisible(is_visible)
            if is_visible:
                num_visible_buttons += 1
        self.delete_heading_button.setVisible(True) # 삭제 버튼 항상 표시
        num_visible_buttons += 1

        # 필요한 너비 계산 및 설정
        sub_widget_width = (num_visible_buttons * button_width) + ((num_visible_buttons - 1) * spacing if num_visible_buttons > 0 else 0)
        self.sub_heading_widget.setFixedWidth(sub_widget_width)

        # 위치 재조정 및 애니메이션 시작
        self.on_text_edit_resize(None) # 현재 위치로 이동
        self.animate_sub_heading_widget(True) # 애니메이션으로 표시


    def on_sub_heading_button_clicked(self):
        """하위 변경 옵션 버튼 (→ Hx) 클릭 시 호출됩니다."""
        if self.selected_heading_level == 0:
            return # 대상 헤딩이 선택되지 않았으면 무시

        clicked_button = self.sender()
        change_to_level = 0
        for level, btn in self.sub_heading_buttons.items():
            if btn == clicked_button:
                change_to_level = level
                break

        if change_to_level == 0 or change_to_level == self.selected_heading_level:
            return # 유효하지 않은 변경 레벨이면 무시

        # 사용자 확인 (선택 사항)
        reply = QMessageBox.question(self, '헤딩 변경 확인',
                                     f"문서 전체의 H{self.selected_heading_level}을(를) H{change_to_level}(으)로 변경하시겠습니까?\n(이 작업은 되돌릴 수 없습니다.)",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            self.reset_heading_change_state() # 취소 시 상태 초기화
            return

        # --- 일괄 변경 로직 실행 ---
        from_pattern = r'^' + '#' * self.selected_heading_level + r' '
        to_prefix = '#' * change_to_level + ' '

        current_text = self.text_edit.toPlainText()
        # re.MULTILINE 플래그 필수
        new_text = re.sub(from_pattern, to_prefix, current_text, flags=re.MULTILINE)

        if new_text != current_text:
            self.text_edit.setPlainText(new_text) # 변경된 텍스트로 업데이트
            self.status_handler.set_success(f"H{self.selected_heading_level} → H{change_to_level} 변경 완료", 3000)
        else:
            self.status_handler.set_message(f"변경할 H{self.selected_heading_level} 헤딩이 없습니다.", 3000)


        # 상태 초기화
        self.reset_heading_change_state()

    def on_delete_heading_button_clicked(self):
        """헤딩 삭제 버튼 (X) 클릭 시 호출됩니다."""
        if self.selected_heading_level == 0:
            return # 대상 헤딩이 선택되지 않았으면 무시

        # 사용자 확인
        reply = QMessageBox.question(self, '헤딩 삭제 확인',
                                     f"문서 전체의 H{self.selected_heading_level} 헤딩 마커('# ')를 모두 삭제하시겠습니까?\n(이 작업은 되돌릴 수 없습니다.)", # 문구 수정
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            self.reset_heading_change_state() # 취소 시 상태 초기화
            return

        # --- 헤딩 삭제 로직 실행 ---
        # 삭제할 패턴: 라인 시작 ^, # 개수, 공백 하나
        # re.MULTILINE 플래그 사용
        from_pattern = r'^' + '#' * self.selected_heading_level + r' '

        current_text = self.text_edit.toPlainText()
        # re.sub으로 해당 패턴을 빈 문자열로 대체 (헤딩 마커만 삭제)
        new_text = re.sub(from_pattern, '', current_text, flags=re.MULTILINE)

        if new_text != current_text:
            self.text_edit.setPlainText(new_text) # 변경된 텍스트로 업데이트
            self.status_handler.set_success(f"H{self.selected_heading_level} 헤딩 마커 삭제 완료", 3000)
        else:
            self.status_handler.set_message(f"삭제할 H{self.selected_heading_level} 헤딩 마커가 없습니다.", 3000)

        # 상태 초기화
        self.reset_heading_change_state()

    # --- 포맷 버튼 관련 메서드 ---
    def on_format_button_clicked(self):
        """포맷 버튼 (B, I, L) 클릭 시 호출됩니다."""
        clicked_button = self.sender()
        target_format = None
        for fmt_type, btn in self.format_buttons.items():
            if btn == clicked_button:
                target_format = fmt_type
                # 다른 포맷 버튼 및 해당 삭제 버튼 상태 초기화
                for other_fmt, other_btn in self.format_buttons.items():
                    if other_fmt != target_format and other_btn.isChecked():
                        other_btn.setChecked(False)
                        # self.format_delete_buttons[other_fmt].hide() # 하위 위젯 전체 숨김으로 대체
                break

        # 버튼이 체크 해제된 경우 (다시 클릭)
        if not clicked_button.isChecked():
            self.reset_format_change_state() # 포맷 상태만 리셋
            return

        # 다른 활성 상태 초기화 (헤딩)
        self.reset_heading_change_state()

        # 현재 상태 업데이트 및 하이라이트
        self.selected_format_type = target_format
        self.highlight_content(format_type=target_format) # 통합 하이라이트 함수 사용

        # 해당 포맷 삭제 버튼만 표시하고 나머지는 숨김
        button_width = 32 # 삭제 버튼 너비
        for fmt, btn in self.format_delete_buttons.items():
            if fmt == target_format:
                btn.show()
                self.active_delete_button = btn # 활성 삭제 버튼 저장
            else:
                btn.hide()

        # 하위 포맷 삭제 버튼 컨테이너 너비 설정 (버튼 1개)
        self.sub_format_widget.setFixedWidth(button_width)

        # 위치 재조정 및 애니메이션 시작
        self.on_text_edit_resize(None) # 현재 위치로 이동
        self.animate_sub_format_widget(True) # 애니메이션으로 표시


    def on_delete_format_button_clicked(self):
        """포맷 삭제 버튼 (X) 클릭 시 호출됩니다."""
        clicked_button = self.sender()
        # active_delete_button과 일치하는지, 그리고 selected_format_type이 있는지 확인
        if clicked_button != self.active_delete_button or not self.selected_format_type:
             print("Warning: Inactive delete button clicked or no format selected.")
             return

        target_format = self.selected_format_type # 저장된 타입 사용

        # 사용자 확인
        reply = QMessageBox.question(self, f'{target_format.capitalize()} 서식 삭제 확인',
                                     f"문서 전체의 모든 '{target_format}' 서식을 삭제하시겠습니까?\n(이 작업은 되돌릴 수 없습니다.)",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            self.reset_format_change_state() # 취소 시 상태 초기화
            return

        # --- 서식 삭제 로직 실행 ---
        current_text = self.text_edit.toPlainText()
        new_text = current_text
        pattern = None
        replacement = r'\2' # 그룹 2 (내용)만 남김

        try:
            if target_format == 'bold':
                # **text** 또는 __text__ -> text
                pattern = r'(\*\*|__)(.+?)\1'
            elif target_format == 'italic':
                 # *text* 또는 _text_ -> text (주의: 중첩 처리 한계)
                 pattern = r'(?<![\*_])(\*|_)(?![\*_])(.+?)\1(?!\1)' # **bold** 안의 *italic* 제외 시도
            elif target_format == 'list':
                # *, -, +, 1. 등 제거 (들여쓰기 유지)
                pattern = r'^[ \t]*([\*\-\+]|\d+\.)[ \t]+'
                replacement = '' # 리스트 마커 자체를 제거
                new_text = re.sub(pattern, replacement, current_text, flags=re.MULTILINE)
            else:
                return # 지원하지 않는 타입

            if target_format != 'list': # 리스트는 위에서 처리
                 # 패턴이 None이 아닌 경우에만 실행
                 if pattern:
                     new_text = re.sub(pattern, replacement, current_text)

            if new_text != current_text:
                self.text_edit.setPlainText(new_text)
                self.status_handler.set_success(f"'{target_format}' 서식 삭제 완료", 3000)
            else:
                self.status_handler.set_message(f"삭제할 '{target_format}' 서식이 없습니다.", 3000)

        except Exception as e:
             self.status_handler.set_error(f"서식 삭제 중 오류: {e}")


        # 상태 초기화
        self.reset_format_change_state()


    def setup_heading_buttons_in_editor(self):
        """텍스트 편집기 내부에 헤딩 및 포맷 버튼 그룹들을 배치합니다."""
        # 위젯은 이미 생성되어 있으므로 텍스트 편집기에 추가만 함
        self.text_edit.setContentsMargins(10, 70, 10, 10)  # 상단 여백 확보 (두 줄 버튼 고려)

        # 헤딩 버튼 컨테이너 위치 설정 (우측 상단)
        self.heading_button_container.setParent(self.text_edit)
        self.heading_button_container.show()
        # self.heading_button_container.raise_() # resize에서 처리

        # 포맷 버튼 컨테이너 위치 설정 (헤딩 버튼 좌측)
        self.format_button_container.setParent(self.text_edit)
        self.format_button_container.show()
        # self.format_button_container.raise_() # resize에서 처리

        # 하위 헤딩 버튼 컨테이너 위치 설정 (헤딩 버튼 아래)
        self.sub_heading_widget.setParent(self.text_edit)
        # self.sub_heading_widget.raise_() # resize에서 처리

        # 하위 포맷 삭제 버튼 컨테이너 위치 설정 (포맷 버튼 아래)
        self.sub_format_widget.setParent(self.text_edit)
        # self.sub_format_widget.raise_() # resize에서 처리

        # 텍스트 편집기 리사이즈 이벤트에 버튼 위치 조정 로직 연결
        self.text_edit.resizeEvent = self.on_text_edit_resize
        # 초기 위치 설정 호출
        QTimer.singleShot(0, lambda: self.on_text_edit_resize(None))


    def on_text_edit_resize(self, event):
        """텍스트 편집기 크기 변경 시 버튼 위치를 조정합니다."""
        # 기본 리사이즈 이벤트 처리 (None 체크 추가)
        if event:
             QTextEdit.resizeEvent(self.text_edit, event)

        editor_width = self.text_edit.width()
        padding = 10 # 우측 여백
        button_y_pos = 5 # 첫 줄 버튼 y 위치
        sub_button_y_pos = button_y_pos + 30 # 두번째 줄 버튼 y 위치 (버튼 높이 + 간격)

        # 1. 헤딩 버튼 컨테이너 위치 조정 (우측 정렬)
        heading_container_width = self.heading_button_container.sizeHint().width()
        heading_x = editor_width - heading_container_width - padding
        self.heading_button_container.move(heading_x, button_y_pos)

        # 2. 포맷 버튼 컨테이너 위치 조정 (헤딩 버튼 좌측)
        format_container_width = self.format_button_container.sizeHint().width()
        format_x = heading_x - format_container_width - 5 # 헤딩 버튼과 5px 간격
        self.format_button_container.move(format_x, button_y_pos)

        # 3. 하위 헤딩 버튼 컨테이너 위치 조정 (헤딩 버튼 아래, 우측 정렬)
        sub_heading_width = self.sub_heading_widget.sizeHint().width()
        # sizeHint가 0일 경우 대비, 또는 고정 너비 사용
        if sub_heading_width == 0 and self.sub_heading_widget.layout().count() > 0:
             # 버튼 개수 기반으로 너비 재계산 (on_heading_button_clicked 로직 참고)
             num_visible = sum(1 for i in range(self.sub_heading_widget.layout().count()) if self.sub_heading_widget.layout().itemAt(i).widget().isVisible())
             spacing = self.sub_heading_layout.spacing()
             button_width = 32 # 가정
             sub_heading_width = (num_visible * button_width) + ((num_visible - 1) * spacing if num_visible > 0 else 0)

        sub_heading_x = editor_width - sub_heading_width - padding
        self.sub_heading_widget.move(sub_heading_x, sub_button_y_pos)

        # 4. 하위 포맷 삭제 버튼 컨테이너 위치 조정 (활성화된 버튼 기준)
        if self.selected_format_type and self.active_delete_button:
             # 해당 포맷 버튼 찾기
             format_button = self.format_buttons.get(self.selected_format_type)
             if format_button:
                 format_container_x = self.format_button_container.pos().x()
                 button_x_in_container = format_button.pos().x()
                 target_x = format_container_x + button_x_in_container
                 # 삭제 버튼 너비에 맞춰 조정 (가운데 정렬 효과)
                 # sizeHint() 대신 실제 너비 사용 시도
                 delete_button_width = self.active_delete_button.width() if self.active_delete_button.width() > 0 else 32 # 너비 보장
                 format_button_width = format_button.width() if format_button.width() > 0 else 32 # 너비 보장
                 target_x += (format_button_width - delete_button_width) // 2
                 self.sub_format_widget.move(target_x, sub_button_y_pos) # y 위치 변경

        # 버튼들을 다시 최상위로 올리기 (스택 순서 중요: 메인 컨테이너 -> 서브 컨테이너)
        self.heading_button_container.raise_()
        self.format_button_container.raise_()
        self.sub_heading_widget.raise_() # 헤딩 서브 위젯 올리기
        self.sub_format_widget.raise_() # 포맷 서브 위젯을 가장 위로 올리기


    def create_default_template(self):
        """기본 문서 설정이 적용된 새 템플릿 생성"""
        try:
            # 사용자로부터 새 템플릿 이름 입력 받기
            template_name, ok = QInputDialog.getText(
                self, "새 템플릿 생성",
                "템플릿 이름을 입력하세요 (확장자 제외):",
                text="새템플릿"
            )

            if not ok or not template_name:
                return

            # 템플릿 생성
            success, message = self.converter.template_manager.create_default_template(template_name)

            if success:
                QMessageBox.information(self, "성공", message)
            else:
                QMessageBox.critical(self, "오류", message)

        except Exception as e:
            QMessageBox.critical(
                self, "오류",
                f"템플릿 생성 중 오류가 발생했습니다: {str(e)}"
            )

    def create_template_from_source(self):
        """원본 문서 설정이 적용된 새 템플릿 생성"""
        try:
            # 사용자로부터 원본 HWP 파일 선택
            source_path, _ = QFileDialog.getOpenFileName(
                self, "원본 HWP 파일 선택",
                "", "HWP 파일 (*.hwp)"
            )

            if not source_path:
                return

            # HWP를 HML로 변환
            from md2hwp.utils.hwp_to_hml import convert_hwp_to_hml
            hml_path = convert_hwp_to_hml(source_path)
            
            if not hml_path:
                QMessageBox.critical(self, "오류", "HWP 파일을 HML로 변환하는데 실패했습니다.")
                return

            # 사용자로부터 새 템플릿 이름 입력 받기
            template_name, ok = QInputDialog.getText(
                self, "새 템플릿 생성",
                "템플릿 이름을 입력하세요 (확장자 제외):",
                text="새템플릿"
            )

            if not ok or not template_name:
                # 템플릿 생성이 취소된 경우 임시 HML 파일 삭제
                if os.path.exists(hml_path):
                    os.remove(hml_path)
                return

            # 템플릿 생성
            success, message = self.converter.template_manager.create_template_from_source(hml_path, template_name)

            # 템플릿 생성 후 임시 HML 파일 삭제
            if os.path.exists(hml_path):
                os.remove(hml_path)

            if success:
                QMessageBox.information(self, "성공", message)
            else:
                QMessageBox.critical(self, "오류", message)

        except Exception as e:
            QMessageBox.critical(
                self, "오류",
                f"템플릿 생성 중 오류가 발생했습니다: {str(e)}"
            )
