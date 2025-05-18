# md2hwp/gui/license_dialog.py

from PySide6.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import Qt

class LicenseDialog(QDialog):
    """라이선스 키 입력 대화 상자"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("라이선스 키 입력")
        self.setMinimumWidth(350)
        # 사용자가 창을 닫지 못하게 하려면 Modal로 설정하거나 closeEvent 재정의
        # self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # 도움말 버튼 제거

        self.key_input = QLineEdit()
        # 기본 라이선스 키 입력
        self.key_input.setText("TEST-KEY-1234-ABCD")
        self.key_input.setPlaceholderText("라이선스 키를 입력하세요 (예: XXXX-XXXX-XXXX)")
        self.ok_button = QPushButton("확인")
        self.cancel_button = QPushButton("취소")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("프로그램을 사용하려면 유효한 라이선스 키를 입력해주세요."))
        layout.addWidget(self.key_input)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept) # OK 누르면 Accepted 반환
        self.cancel_button.clicked.connect(self.reject) # Cancel 누르면 Rejected 반환
        self.key_input.returnPressed.connect(self.accept) # Enter 키로 확인 가능

    def get_key(self):
        """입력된 라이선스 키 반환"""
        return self.key_input.text().strip()

    # 사용자가 X 버튼으로 닫는 것을 막으려면:
    # def closeEvent(self, event):
    #     # 창 닫기 이벤트를 무시하거나, reject()를 호출하여 취소로 처리
    #     event.ignore() # 또는 self.reject()
    #     print("창 닫기 버튼 비활성화됨. 취소 버튼을 이용하세요.")