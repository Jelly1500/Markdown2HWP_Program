"""
GUI 에러 처리 유틸리티

사용자 친화적인 에러 메시지를 표시하고 로깅하는 기능을 제공합니다.
"""

from PySide6.QtWidgets import QMessageBox
from typing import Optional
import traceback
from ..exceptions import MD2HWPException
from ..utils.logger import log_error, log_info


class ErrorHandler:
    """GUI 에러 처리를 위한 헬퍼 클래스"""

    @staticmethod
    def show_error(parent, title: str, exception: Exception, show_details: bool = True):
        """
        에러를 사용자 친화적으로 표시합니다.

        Args:
            parent: 부모 위젯 (QWidget)
            title: 대화상자 제목
            exception: 발생한 예외
            show_details: 상세 정보 버튼 표시 여부
        """
        # 로그에 기록
        log_error(f"{title}: {str(exception)}")

        # 커스텀 예외인 경우
        if isinstance(exception, MD2HWPException):
            ErrorHandler._show_custom_error(parent, title, exception, show_details)
        else:
            # 일반 예외인 경우
            ErrorHandler._show_generic_error(parent, title, exception, show_details)

    @staticmethod
    def _show_custom_error(parent, title: str, exception: MD2HWPException, show_details: bool):
        """커스텀 예외를 표시"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Icon.Critical)

        # 사용자 친화적 메시지
        msg_box.setText(exception.get_user_message())

        # 상세 정보
        if show_details and (exception.details or exception.solution):
            detail_parts = []
            if exception.details:
                detail_parts.append(f"상세정보:\n{exception.details}")
            if exception.solution:
                detail_parts.append(f"\n해결방법:\n{exception.solution}")

            msg_box.setDetailedText("\n\n".join(detail_parts))

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def _show_generic_error(parent, title: str, exception: Exception, show_details: bool):
        """일반 예외를 표시"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Icon.Critical)

        # 예외 타입에 따라 사용자 친화적 메시지 생성
        user_message = ErrorHandler._get_friendly_message(exception)
        msg_box.setText(user_message)

        # 상세 정보 (기술적 세부사항)
        if show_details:
            technical_details = f"예외 타입: {type(exception).__name__}\n\n"
            technical_details += f"오류 메시지:\n{str(exception)}\n\n"
            technical_details += "스택 트레이스:\n"
            technical_details += traceback.format_exc()
            msg_box.setDetailedText(technical_details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def _get_friendly_message(exception: Exception) -> str:
        """예외 타입에 따라 사용자 친화적 메시지를 생성"""
        exc_type = type(exception).__name__

        # 일반적인 예외에 대한 친화적 메시지 매핑
        friendly_messages = {
            'FileNotFoundError': '파일을 찾을 수 없습니다',
            'PermissionError': '파일 접근 권한이 없습니다',
            'UnicodeDecodeError': '파일 인코딩이 올바르지 않습니다',
            'UnicodeEncodeError': '지원하지 않는 문자가 포함되어 있습니다',
            'ValueError': '입력값이 올바르지 않습니다',
            'RuntimeError': '실행 중 오류가 발생했습니다',
            'KeyError': '필요한 정보를 찾을 수 없습니다',
            'AttributeError': '내부 처리 오류가 발생했습니다',
            'TypeError': '데이터 타입이 올바르지 않습니다',
            'OSError': '시스템 오류가 발생했습니다',
            'ImportError': '필요한 모듈을 불러올 수 없습니다',
            'ConnectionError': '네트워크 연결에 실패했습니다',
            'TimeoutError': '시간 초과가 발생했습니다',
        }

        base_message = friendly_messages.get(exc_type, '알 수 없는 오류가 발생했습니다')

        # 예외 메시지가 있으면 추가
        if str(exception):
            return f"{base_message}\n\n{str(exception)}"
        else:
            return base_message

    @staticmethod
    def show_warning(parent, title: str, message: str, detailed_text: Optional[str] = None):
        """경고 메시지 표시"""
        log_info(f"Warning: {title} - {message}")

        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(message)

        if detailed_text:
            msg_box.setDetailedText(detailed_text)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def show_info(parent, title: str, message: str, detailed_text: Optional[str] = None):
        """정보 메시지 표시"""
        log_info(f"Info: {title} - {message}")

        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(message)

        if detailed_text:
            msg_box.setDetailedText(detailed_text)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def confirm(parent, title: str, message: str, detailed_text: Optional[str] = None) -> bool:
        """확인 대화상자 표시 (예/아니오)"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText(message)

        if detailed_text:
            msg_box.setDetailedText(detailed_text)

        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes


def handle_exceptions(func):
    """
    메서드 데코레이터: 예외를 자동으로 처리하고 사용자에게 표시

    사용 예:
        @handle_exceptions
        def some_method(self):
            # 예외가 발생할 수 있는 코드
            pass
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except MD2HWPException as e:
            ErrorHandler.show_error(
                self,
                f"{func.__name__} 오류",
                e,
                show_details=True
            )
        except Exception as e:
            ErrorHandler.show_error(
                self,
                "예상치 못한 오류",
                e,
                show_details=True
            )
    return wrapper
