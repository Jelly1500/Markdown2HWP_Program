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
                              QGroupBox, QToolButton)
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
    """GUI 메인 창 클래스 (헤딩 변경 기능 추가)"""

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
        
        # 하위 변경 옵션 버튼 그룹 (초기에는 숨김)
        self.sub_heading_widget = QWidget()
        self.sub_heading_widget.setObjectName("SubHeadingButtonContainer")
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
            self.status_handler.set_success(f"변환 완료: {os.path.basename(current_output_path)}")
            QTimer.singleShot(100, lambda: self.try_open_result(current_output_path, current_output_dir))
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
        # 하위 버튼은 숨겨진 상태이므로 별도 처리 불필요할 수 있으나,
        # 만약 활성화 상태에서 비활성화될 경우 고려
        if not enabled:
             self.reset_heading_change_state() # 비활성화 시 상태 초기화


    def try_open_result(self, file_path, folder_path):
        if not open_file(file_path):
            try:
                open_file_explorer(folder_path)
                self.status_handler.set_warning("파일 자동 열기 실패. 저장 폴더를 열었습니다.", 5000)
            except Exception as folder_err:
                 self.status_handler.set_warning(f"파일/폴더 자동 열기 실패: {folder_err}", 5000)


    # --- 헤딩 변경 관련 메서드 ---

    def highlight_headings(self, level):
        """지정된 레벨의 헤딩을 하이라이트합니다."""
        self.clear_highlights()
        if level == 0:
            return

        cursor = QTextCursor(self.text_edit.document())
        selections = []

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 180)) # 연한 노란색 배경

        # 정규식 패턴 (줄 시작, # 개수, 공백)
        pattern = r'^' + '#' * level + r' '
        regex = QRegularExpression(pattern)
        
        doc = self.text_edit.document()
        cursor = doc.find(regex, cursor)
        
        while not cursor.isNull():
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            # 헤딩 마커 부분만 선택 ('## ' 부분)
            selection.cursor.clearSelection()
            start_pos = cursor.position() - (len(pattern)-1) # 패턴 길이만큼 앞으로 (주의: 패턴 길이 계산)
            end_pos = cursor.position()
            selection.cursor.setPosition(start_pos)
            selection.cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)

            selection.format = highlight_format
            selections.append(selection)
            cursor = doc.find(regex, cursor) # 다음 찾기에도 정규식 객체 사용

        self.text_edit.setExtraSelections(selections)

    def clear_highlights(self):
        """모든 추가 선택(하이라이트)을 제거합니다."""
        self.text_edit.setExtraSelections([])

    def reset_heading_change_state(self):
        """헤딩 변경 관련 상태를 초기화합니다."""
        self.clear_highlights()
        # 애니메이션으로 하위 버튼 숨기기
        self.animate_sub_heading_widget(False) 
        if self.selected_heading_level in self.heading_buttons:
             if self.heading_buttons[self.selected_heading_level].isChecked():
                 self.heading_buttons[self.selected_heading_level].setChecked(False)
        self.selected_heading_level = 0

    def animate_sub_heading_widget(self, show=True):
        """하위 헤딩 버튼을 애니메이션으로 표시하거나 숨깁니다."""
        target_height = 35 if show else 0
        
        # 애니메이션 전 설정
        if show:
            # 보여주기 전에 위젯을 표시하고 맨 위로 가져오기
            self.sub_heading_widget.show()
            self.sub_heading_widget.raise_()
            # 시작 높이 설정
            self.sub_heading_widget.setFixedHeight(0)
        
        # 애니메이션 생성
        self.animation = QPropertyAnimation(self.sub_heading_widget, b"maximumHeight")
        self.animation.setDuration(200)  # 애니메이션 시간 (ms)
        self.animation.setStartValue(0 if show else 35)  # 명시적인 시작값
        self.animation.setEndValue(target_height)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # 부드러운 효과
        
        # 애니메이션 중간에 실행되는 함수 (높이 동기화)
        def update_height(height):
            self.sub_heading_widget.setFixedHeight(height)
            self.sub_heading_widget.updateGeometry()
        
        self.animation.valueChanged.connect(update_height)
        
        # 애니메이션 완료 후 처리
        if not show:
            self.animation.finished.connect(lambda: self.sub_heading_widget.hide())
        else:
            self.animation.finished.connect(lambda: self.sub_heading_widget.setMinimumHeight(target_height))
        
        # 애니메이션 시작
        self.animation.start()

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
            self.reset_heading_change_state()
            return

        # 이전에 다른 버튼이 선택된 상태였다면 초기화
        if self.selected_heading_level != 0 and self.selected_heading_level != target_level:
            self.reset_heading_change_state() # 하이라이트, 하위 버튼 숨김 등

        # 현재 상태 업데이트 및 하이라이트
        self.selected_heading_level = target_level
        self.highlight_headings(target_level)

        # 하위 버튼 위치 재조정 (헤딩 버튼 바로 아래)
        container_width = self.heading_button_container.width()
        self.sub_heading_widget.move(self.text_edit.width() - container_width - 10, 35)

        # 하위 버튼 표시 (자기 자신 제외)
        for level, btn in self.sub_heading_buttons.items():
            btn.setVisible(level != target_level)
        
        # 하위 버튼을 위로 올리고 애니메이션으로 표시
        self.sub_heading_widget.raise_()
        self.animate_sub_heading_widget(True)

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

    def setup_heading_buttons_in_editor(self):
        """텍스트 편집기 내부에 헤딩 버튼을 배치합니다."""
        # 위젯은 이미 생성되어 있으므로 텍스트 편집기에 추가만 함
        self.text_edit.setContentsMargins(10, 40, 10, 10)  # 상단 여백 확보
        
        # 버튼 컨테이너 위치 설정
        self.heading_button_container.setParent(self.text_edit)
        self.heading_button_container.move(10, 5)  # 텍스트 편집기 내 상단 위치
        self.heading_button_container.show()
        self.heading_button_container.raise_()  # 상위로 올리기
        
        # 하위 버튼 컨테이너 위치 설정
        self.sub_heading_widget.setParent(self.text_edit)
        self.sub_heading_widget.move(10, 35)  # 헤딩 버튼 아래 위치
        self.sub_heading_widget.raise_()  # 상위로 올리기
        
        # 텍스트 편집기 리사이즈 이벤트에 버튼 위치 조정 로직 연결
        self.text_edit.resizeEvent = self.on_text_edit_resize

    def on_text_edit_resize(self, event):
        """텍스트 편집기 크기 변경 시 버튼 위치를 조정합니다."""
        # 기본 리사이즈 이벤트 처리
        QTextEdit.resizeEvent(self.text_edit, event)
        
        # 버튼 컨테이너 위치 조정 (우상단 배치)
        container_width = self.heading_button_container.width()
        self.heading_button_container.move(self.text_edit.width() - container_width - 10, 5)
        
        # 하위 버튼 컨테이너 위치 조정 (헤딩 버튼 아래)
        self.sub_heading_widget.move(self.text_edit.width() - self.sub_heading_widget.width() - 10, 35)
        
        # 버튼들을 다시 최상위로 올리기
        self.heading_button_container.raise_()
        self.sub_heading_widget.raise_()

