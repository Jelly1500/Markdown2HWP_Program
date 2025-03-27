# md2hwp/gui/main_window.py

import os
import datetime
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QPushButton, QFileDialog,
                              QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QApplication,
                              QMenu)
from .status_handler import StatusHandler
from ..config import OUTPUT_DIR_NAME, DEFAULT_ENCODING
# generate_output_filename 함수 임포트 확인
from ..utils.file_utils import ensure_directory, generate_output_filename, save_text_file, open_file, open_file_explorer

class MainWindow(QMainWindow):
    """GUI 메인 창 클래스"""

    def __init__(self, converter):
        super().__init__()

        self.setWindowTitle("마크다운 → HWP 변환기")
        self.setGeometry(100, 100, 600, 400)

        self.converter = converter
        self.template_path = ""
        self.output_path = None # 초기 출력 경로는 없음
        # --- 사용자가 출력 경로를 직접 선택했는지 여부 플래그 추가 ---
        self.user_selected_output_path = False

        # 현재 스크립트의 위치를 기준으로 상대 경로 설정 (이 부분은 setup_ui로 이동 가능)
        # current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # self.output_dir = os.path.join(current_dir, OUTPUT_DIR_NAME)
        # ensure_directory(self.output_dir)

        self.setup_ui()

    def setup_ui(self):
        """UI 구성 요소 설정"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # --- output_dir 설정 __init__ 에서 setup_ui 로 이동 ---
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(current_dir, OUTPUT_DIR_NAME)
        ensure_directory(self.output_dir)
        # ---

        self.layout = QVBoxLayout(self.central_widget)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("여기에 마크다운 텍스트를 붙여넣거나 클립보드에서 불러오세요")
        self.layout.addWidget(self.text_edit)

        self.button_layout = QHBoxLayout()

        self.template_button = QPushButton("템플릿 선택")
        self.clipboard_button = QPushButton("클립보드에서 불러오기")
        
        # file_explore 버튼과 메뉴 설정
        self.file_explore = QPushButton("파일 위치 보기")
        self.file_explore_menu = QMenu()
        self.show_output_action = self.file_explore_menu.addAction("한글 파일 위치 보기")
        self.show_template_action = self.file_explore_menu.addAction("템플릿 위치 보기")
        self.file_explore.setMenu(self.file_explore_menu)
        
        self.convert_button = QPushButton("변환")

        self.button_layout.addWidget(self.template_button)
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.file_explore)
        self.button_layout.addWidget(self.convert_button)

        self.layout.addLayout(self.button_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_handler = StatusHandler(self.status_bar)
        self.status_handler.reset()

        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.show_output_action.triggered.connect(self.show_output_location)
        self.show_template_action.triggered.connect(self.show_template_location)
        self.convert_button.clicked.connect(self.convert)

    def select_template(self):
        """템플릿 파일 선택 대화상자 표시"""
        file_path, _ = QFileDialog.getOpenFileName(self, "템플릿 파일 선택", "", "HWP 파일 (*.hml)")
        if file_path:
            self.template_path = file_path
            # --- 템플릿 변경 시, 사용자 지정 출력 경로 유지 여부 결정 필요 ---
            # 여기서는 일단 유지하는 것으로 가정
            # self.user_selected_output_path = False # 필요시 주석 해제
            # self.output_path = None              # 필요시 주석 해제
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

    def show_output_location(self):
        """한글 파일 위치를 파일 탐색기에서 보여줌"""
        if self.output_path:
            try:
                open_file_explorer(self.output_path, handle_type='output')
            except Exception as e:
                self.status_handler.set_error(f"파일 탐색기 열기 실패: {str(e)}")
        else:
            self.status_handler.set_error("아직 변환된 파일이 없습니다")

    def show_template_location(self):
        """템플릿 파일 위치를 파일 탐색기에서 보여줌"""
        if self.template_path:
            try:
                open_file_explorer(self.template_path, handle_type='template')
            except Exception as e:
                self.status_handler.set_error(f"파일 탐색기 열기 실패: {str(e)}")
        else:
            self.status_handler.set_error("먼저 템플릿을 선택하세요")

    def convert(self):
        """마크다운을 HWPML로 변환하여 저장"""
        if not self.template_path:
            self.status_handler.set_error("먼저 템플릿을 선택하세요")
            return

        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_handler.set_error("변환할 텍스트가 없습니다")
            return

        # --- 출력 경로 결정 로직 수정 ---
        if self.user_selected_output_path and self.output_path:
            # 사용자가 직접 경로를 선택한 경우 해당 경로 사용
            current_output_path = self.output_path
        else:
            # 사용자가 경로를 선택하지 않은 경우, 변환 시점마다 새 타임스탬프 경로 생성
            current_output_path = generate_output_filename(self.output_dir)
            self.output_path = current_output_path
            # 필요하다면 self.output_path 도 업데이트 할 수 있으나, 다음 변환 시 어차피 새로 생성될 것이므로 필수는 아님
            # self.output_path = current_output_path
        # ---

        self.status_handler.set_message("변환 중...")

        try:
            # convert_md_to_hwpml 호출 시 메타데이터는 내부에서 처리됨
            hwpml_content = self.converter.convert_md_to_hwpml(md_text)

            # 결정된 현재 출력 경로(current_output_path)에 저장
            save_text_file(current_output_path, hwpml_content, encoding=DEFAULT_ENCODING)

            self.status_handler.set_success(f"변환 완료: {current_output_path}")

            # 변환 완료 후 파일 자동 실행
            if not open_file(current_output_path):
                self.status_handler.set_error("파일을 자동으로 열지 못했습니다")
                
        except Exception as e:
            # 오류 발생 시 상세 정보 포함하여 표시
            import traceback
            traceback.print_exc() # 콘솔에 상세 오류 출력
            self.status_handler.set_error(f"변환 중 오류 발생: {str(e)}")