"""
상태 표시줄 관리 모듈
"""
from PySide6.QtWidgets import QStatusBar

class StatusHandler:
    """상태 표시줄 관리 클래스"""
    
    def __init__(self, status_bar):
        self.status_bar = status_bar
        self.default_message = "준비 완료"
    
    def set_message(self, message, timeout=0):
        """상태 메시지 설정"""
        self.status_bar.showMessage(message, timeout)
    
    def set_error(self, message):
        """오류 메시지 표시"""
        self.status_bar.showMessage(f"오류: {message}")
    
    def set_success(self, message):
        """성공 메시지 표시"""
        self.status_bar.showMessage(f"성공: {message}")
    
    def reset(self):
        """기본 메시지로 복원"""
        self.status_bar.showMessage(self.default_message) 