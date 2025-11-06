"""
md2hwp 커스텀 예외 클래스 정의

이 모듈은 md2hwp 애플리케이션에서 사용하는 모든 커스텀 예외를 정의합니다.
계층적 예외 구조를 통해 세밀한 에러 처리와 사용자 친화적인 메시지를 제공합니다.
"""

from typing import Optional


class MD2HWPException(Exception):
    """md2hwp의 모든 예외의 기본 클래스"""

    def __init__(self, message: str, details: Optional[str] = None, solution: Optional[str] = None):
        """
        Args:
            message: 사용자에게 표시할 간단한 에러 메시지
            details: 에러에 대한 상세 정보 (선택적)
            solution: 문제 해결 방법 제안 (선택적)
        """
        self.message = message
        self.details = details
        self.solution = solution
        super().__init__(self.get_full_message())

    def get_full_message(self) -> str:
        """전체 에러 메시지를 조합하여 반환"""
        parts = [self.message]

        if self.details:
            parts.append(f"\n상세정보: {self.details}")

        if self.solution:
            parts.append(f"\n해결방법: {self.solution}")

        return "".join(parts)

    def get_user_message(self) -> str:
        """GUI에 표시할 사용자 친화적 메시지만 반환"""
        return self.message


# ============================================================================
# 템플릿 관련 예외
# ============================================================================

class TemplateException(MD2HWPException):
    """템플릿 관련 예외의 기본 클래스"""
    pass


class TemplateLoadError(TemplateException):
    """템플릿 파일 로딩 실패"""

    def __init__(self, template_path: str, reason: str):
        self.template_path = template_path
        self.reason = reason
        super().__init__(
            message=f"템플릿 파일을 불러올 수 없습니다",
            details=f"파일: {template_path}\n이유: {reason}",
            solution="템플릿 파일이 존재하는지, 올바른 HML 형식인지 확인하세요."
        )


class TemplateNotFoundError(TemplateException):
    """템플릿 파일을 찾을 수 없음"""

    def __init__(self, template_path: str):
        self.template_path = template_path
        super().__init__(
            message=f"템플릿 파일을 찾을 수 없습니다",
            details=f"경로: {template_path}",
            solution="템플릿 파일 경로가 올바른지 확인하거나, 새 템플릿을 선택하세요."
        )


class TemplateMalformedError(TemplateException):
    """템플릿 구조가 올바르지 않음"""

    def __init__(self, missing_element: str, template_path: Optional[str] = None):
        self.missing_element = missing_element
        self.template_path = template_path

        detail_msg = f"누락된 요소: {missing_element}"
        if template_path:
            detail_msg = f"파일: {template_path}\n{detail_msg}"

        super().__init__(
            message=f"템플릿 구조가 올바르지 않습니다",
            details=detail_msg,
            solution=f"템플릿에 {missing_element} 요소가 포함되어 있는지 확인하거나, 다른 템플릿을 사용하세요."
        )


class TemplateStyleNotFoundError(TemplateException):
    """템플릿에서 필요한 스타일을 찾을 수 없음"""

    def __init__(self, style_name: str):
        self.style_name = style_name
        super().__init__(
            message=f"템플릿에 필요한 스타일이 없습니다",
            details=f"스타일: {style_name}",
            solution=f"템플릿에 '{style_name}' 스타일을 추가하거나, 해당 스타일이 포함된 템플릿을 사용하세요."
        )


# ============================================================================
# 변환 관련 예외
# ============================================================================

class ConversionException(MD2HWPException):
    """변환 관련 예외의 기본 클래스"""
    pass


class ConversionError(ConversionException):
    """일반적인 변환 오류"""

    def __init__(self, element_type: str, reason: str, line_number: Optional[int] = None):
        self.element_type = element_type
        self.reason = reason
        self.line_number = line_number

        detail_msg = f"요소 타입: {element_type}\n이유: {reason}"
        if line_number:
            detail_msg = f"라인: {line_number}\n{detail_msg}"

        super().__init__(
            message=f"마크다운 변환 중 오류가 발생했습니다",
            details=detail_msg,
            solution="마크다운 문법이 올바른지 확인하세요."
        )


class TableConversionError(ConversionException):
    """테이블 변환 오류"""

    def __init__(self, reason: str, row_number: Optional[int] = None):
        self.reason = reason
        self.row_number = row_number

        detail_msg = f"이유: {reason}"
        if row_number is not None:
            detail_msg = f"행 번호: {row_number}\n{detail_msg}"

        super().__init__(
            message=f"테이블 변환 중 오류가 발생했습니다",
            details=detail_msg,
            solution="테이블 마크다운 문법(행/열 구분자)이 올바른지 확인하세요."
        )


class InvalidMarkdownError(ConversionException):
    """마크다운 문법 오류"""

    def __init__(self, reason: str, context: Optional[str] = None):
        self.reason = reason
        self.context = context

        detail_msg = f"이유: {reason}"
        if context:
            detail_msg += f"\n문제가 발생한 부분:\n{context}"

        super().__init__(
            message=f"마크다운 형식이 올바르지 않습니다",
            details=detail_msg,
            solution="마크다운 문법을 확인하고 수정하세요."
        )


class EmptyContentError(ConversionException):
    """변환할 내용이 없음"""

    def __init__(self):
        super().__init__(
            message="변환할 내용이 없습니다",
            details="입력된 마크다운 텍스트가 비어있거나 유효한 내용이 없습니다.",
            solution="마크다운 텍스트를 입력하거나 파일을 불러오세요."
        )


class ContentTooLargeError(ConversionException):
    """변환할 내용이 너무 큼"""

    def __init__(self, size_mb: float, max_size_mb: float):
        self.size_mb = size_mb
        self.max_size_mb = max_size_mb
        super().__init__(
            message="파일이 너무 큽니다",
            details=f"현재 크기: {size_mb:.1f}MB\n최대 크기: {max_size_mb}MB",
            solution=f"파일 크기를 {max_size_mb}MB 이하로 줄이거나, 문서를 분할하세요."
        )


# ============================================================================
# 파일 관련 예외
# ============================================================================

class FileException(MD2HWPException):
    """파일 관련 예외의 기본 클래스"""
    pass


class FileAccessError(FileException):
    """파일 접근 권한 오류"""

    def __init__(self, file_path: str, operation: str = "읽기"):
        self.file_path = file_path
        self.operation = operation
        super().__init__(
            message=f"파일에 접근할 수 없습니다",
            details=f"파일: {file_path}\n작업: {operation}",
            solution="파일 권한을 확인하거나, 다른 위치에서 시도하세요."
        )


class FileSaveError(FileException):
    """파일 저장 오류"""

    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        super().__init__(
            message=f"파일을 저장할 수 없습니다",
            details=f"파일: {file_path}\n이유: {reason}",
            solution="디스크 공간과 쓰기 권한을 확인하세요."
        )


class InvalidFileFormatError(FileException):
    """지원하지 않는 파일 형식"""

    def __init__(self, file_path: str, expected_formats: list[str]):
        self.file_path = file_path
        self.expected_formats = expected_formats
        super().__init__(
            message=f"지원하지 않는 파일 형식입니다",
            details=f"파일: {file_path}\n지원 형식: {', '.join(expected_formats)}",
            solution=f"지원하는 형식({', '.join(expected_formats)})의 파일을 사용하세요."
        )


# ============================================================================
# 라이선스 관련 예외
# ============================================================================

class LicenseException(MD2HWPException):
    """라이선스 관련 예외의 기본 클래스"""
    pass


class LicenseValidationError(LicenseException):
    """라이선스 검증 실패"""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            message=f"라이선스 검증에 실패했습니다",
            details=reason,
            solution="유효한 라이선스 키를 입력하거나, 관리자에게 문의하세요."
        )


class LicenseExpiredError(LicenseException):
    """라이선스 만료"""

    def __init__(self, expired_date: str):
        self.expired_date = expired_date
        super().__init__(
            message=f"라이선스가 만료되었습니다",
            details=f"만료일: {expired_date}",
            solution="라이선스를 갱신하거나 새로운 라이선스를 구매하세요."
        )


class LicenseServerError(LicenseException):
    """라이선스 서버 연결 오류"""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            message=f"라이선스 서버에 연결할 수 없습니다",
            details=reason,
            solution="인터넷 연결을 확인하거나, 잠시 후 다시 시도하세요."
        )


# ============================================================================
# HWP 처리 관련 예외
# ============================================================================

class HWPException(MD2HWPException):
    """HWP 처리 관련 예외의 기본 클래스"""
    pass


class HWPCreationError(HWPException):
    """HWP 파일 생성 오류"""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            message=f"HWP 파일 생성에 실패했습니다",
            details=reason,
            solution="HWPML 구조가 올바른지 확인하거나, 템플릿을 변경해보세요."
        )


class HWPConversionError(HWPException):
    """HWP 파일 변환 오류"""

    def __init__(self, source_format: str, target_format: str, reason: str):
        self.source_format = source_format
        self.target_format = target_format
        self.reason = reason
        super().__init__(
            message=f"{source_format}에서 {target_format}로 변환 실패",
            details=reason,
            solution="한/글이 설치되어 있는지 확인하고, 파일이 손상되지 않았는지 확인하세요."
        )


class HWPAutomationError(HWPException):
    """HWP 자동화 오류"""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            message=f"한/글 자동화 실행 중 오류가 발생했습니다",
            details=reason,
            solution="한/글이 설치되어 있는지, 보안 모듈이 해제되어 있는지 확인하세요."
        )


# ============================================================================
# 이미지 처리 관련 예외
# ============================================================================

class ImageException(MD2HWPException):
    """이미지 처리 관련 예외의 기본 클래스"""
    pass


class ImageLoadError(ImageException):
    """이미지 로딩 오류"""

    def __init__(self, image_path: str, reason: str):
        self.image_path = image_path
        self.reason = reason
        super().__init__(
            message=f"이미지를 불러올 수 없습니다",
            details=f"파일: {image_path}\n이유: {reason}",
            solution="이미지 파일이 존재하고 올바른 형식인지 확인하세요."
        )


class ImageConversionError(ImageException):
    """이미지 변환 오류"""

    def __init__(self, source_path: str, target_format: str, reason: str):
        self.source_path = source_path
        self.target_format = target_format
        self.reason = reason
        super().__init__(
            message=f"이미지를 {target_format} 형식으로 변환할 수 없습니다",
            details=f"파일: {source_path}\n이유: {reason}",
            solution="이미지 파일 형식과 권한을 확인하세요."
        )


# ============================================================================
# GUI 관련 예외
# ============================================================================

class GUIException(MD2HWPException):
    """GUI 관련 예외의 기본 클래스"""
    pass


class WindowHandleError(GUIException):
    """윈도우 핸들 관련 오류"""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            message=f"윈도우 처리 중 오류가 발생했습니다",
            details=reason,
            solution="프로그램을 재시작하거나, 다른 창을 닫아보세요."
        )


# ============================================================================
# 유효성 검증 관련 예외
# ============================================================================

class ValidationException(MD2HWPException):
    """유효성 검증 관련 예외의 기본 클래스"""
    pass


class InvalidInputError(ValidationException):
    """잘못된 입력값"""

    def __init__(self, field_name: str, reason: str, valid_examples: Optional[str] = None):
        self.field_name = field_name
        self.reason = reason
        self.valid_examples = valid_examples

        solution = f"{field_name}의 값을 올바르게 입력하세요."
        if valid_examples:
            solution += f"\n예시: {valid_examples}"

        super().__init__(
            message=f"잘못된 입력값입니다",
            details=f"필드: {field_name}\n이유: {reason}",
            solution=solution
        )


class UnsafeContentError(ValidationException):
    """안전하지 않은 콘텐츠"""

    def __init__(self, content_type: str):
        self.content_type = content_type
        super().__init__(
            message=f"안전하지 않은 콘텐츠가 감지되었습니다",
            details=f"유형: {content_type}",
            solution="위험한 스크립트나 태그를 제거하고 다시 시도하세요."
        )
