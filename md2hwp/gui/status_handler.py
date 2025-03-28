# md2hwp/gui/status_handler.py
"""
상태 표시줄 관리 모듈 (스타일링 기능 추가)
"""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QStatusBar, QApplication

class StatusHandler:
    """상태 표시줄 관리 클래스"""

    def __init__(self, status_bar: QStatusBar):
        self.status_bar = status_bar
        self.default_message = "준비 완료"
        # 기본 스타일 저장 (main_window.py의 QSS와 일치하거나, 여기서 정의)
        self.default_style = """
            QStatusBar {
                background-color: #f8f8f8;
                border-top: 1px solid #e0e0e0;
                color: #6e6e73;
                font-size: 9pt;
                padding-left: 10px;
            }
            QStatusBar::item {
                border: none;
            }
        """
        # 또는 self.default_style = self.status_bar.styleSheet()

    def set_message(self, message, timeout=0):
        """일반 메시지 설정 (기본 스타일)"""
        self.reset_style() # 다른 상태 스타일 초기화
        self.status_bar.showMessage(message, timeout)
        # 메시지가 timeout 후 사라지면 기본 메시지로 돌아가도록 설정 가능
        if timeout > 0:
             QTimer.singleShot(timeout, lambda: self.status_bar.currentMessage() == message and self.reset())


    def set_warning(self, message, timeout=5000):
        """경고 메시지 표시 (노란색 계열 스타일)"""
        style = self.default_style + """
            QStatusBar {
                background-color: #fffbeb; /* 연한 노랑 */
                color: #664d03; /* 어두운 노랑/갈색 텍스트 */
                border-top: 1px solid #fff3cd;
            }
        """
        self.status_bar.setStyleSheet(style)
        self.status_bar.showMessage(f"⚠️ {message}", timeout) # 아이콘 추가
        QTimer.singleShot(timeout, self.reset_style) # 시간 지나면 기본 스타일 복원

    def set_success(self, message, timeout=5000):
        """성공 메시지 표시 (초록색 계열 스타일)"""
        style = self.default_style + """
            QStatusBar {
                background-color: #e9f7ef; /* 연한 초록 */
                color: #0f5132; /* 어두운 초록 텍스트 */
                border-top: 1px solid #d1e7dd;
            }
        """
        self.status_bar.setStyleSheet(style)
        self.status_bar.showMessage(f"✅ {message}", timeout) # 아이콘 추가
        QTimer.singleShot(timeout, self.reset_style) # 시간 지나면 기본 스타일 복원

    def set_error(self, message, timeout=0):
        """오류 메시지 표시 (빨간색 계열 스타일, timeout 0으로 계속 표시)"""
        style = self.default_style + """
            QStatusBar {
                background-color: #fdecef; /* 연한 빨강 */
                color: #842029; /* 어두운 빨강 텍스트 */
                border-top: 1px solid #f8d7da;
            }
        """
        self.status_bar.setStyleSheet(style)
        self.status_bar.showMessage(f"❌ {message}", timeout) # 아이콘 추가
        # 오류는 사용자가 다른 동작을 하기 전까지 유지될 수 있으므로,
        # reset_style 타이머를 걸지 않거나, 다른 메시지가 표시될 때 reset_style 호출

    def reset_style(self):
        """상태바 스타일을 기본값으로 복원"""
        # 현재 메시지가 오류 메시지가 아닐 때만 스타일 복원 (선택적 로직)
        # if "❌" not in self.status_bar.currentMessage():
        self.status_bar.setStyleSheet(self.default_style)

    def reset(self):
        """기본 메시지로 복원 및 스타일 리셋"""
        self.reset_style()
        self.status_bar.showMessage(self.default_message)