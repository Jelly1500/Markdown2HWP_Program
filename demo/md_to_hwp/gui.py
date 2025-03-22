# md_to_hwp/gui.py
"""
마크다운 변환기의 GUI 인터페이스 모듈
"""
import re
import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                             QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar,
                             QLabel, QComboBox, QTabWidget, QFormLayout, QGroupBox,
                             QLineEdit, QSpinBox, QCheckBox, QColorDialog, QDialog,
                             QFontComboBox)
from PySide6.QtGui import QIcon, QFont, QColor
from PySide6.QtCore import Qt
from md_to_hwp.converter import HWPMLConverter
from md_to_hwp.template_manager import MarkdownTemplate

class ColorButton(QPushButton):
    """색상 선택 버튼 클래스"""
    
    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedWidth(80)
        self.setColor(color)
        self.clicked.connect(self.choose_color)
    
    def setColor(self, color):
        """버튼 색상 설정"""
        self.color = color
        r, g, b = self.hex_to_rgb(color)
        
        # 배경색에 따라 텍스트 색상 선택 (가독성 향상)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_color = "white" if luminance < 0.5 else "black"
        
        self.setStyleSheet(f"background-color: {color}; color: {text_color};")
        self.setText(color)
    
    def choose_color(self):
        """색상 선택 대화상자 표시"""
        r, g, b = self.hex_to_rgb(self.color)
        initial_color = QColor(r, g, b)
        
        color = QColorDialog.getColor(initial_color, self.parent(), "색상 선택")
        if color.isValid():
            hex_color = f"#{color.red():02x}{color.green():02x}{color.blue():02x}"
            self.setColor(hex_color)
    
    def hex_to_rgb(self, hex_color):
        """HEX 색상코드를 RGB로 변환"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return (0, 0, 0)
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class TemplateEditDialog(QDialog):
    """템플릿 편집 대화상자"""
    
    def __init__(self, template_manager, template_name="default", parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.template_name = template_name
        self.template_data = template_manager.templates.get(template_name, {}).copy()
        
        self.setWindowTitle(f"템플릿 편집 - {template_name}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        self.layout = QVBoxLayout(self)
        
        # 탭 위젯 생성
        self.tabs = QTabWidget()
        
        # 제목 탭
        self.headings_tab = QWidget()
        self.create_headings_tab()
        
        # 목록 탭
        self.lists_tab = QWidget()
        self.create_lists_tab()
        
        # 텍스트 서식 탭
        self.text_tab = QWidget()
        self.create_text_tab()
        
        # 테이블 탭
        self.table_tab = QWidget()
        self.create_table_tab()
        
        # 탭 추가
        self.tabs.addTab(self.headings_tab, "제목")
        self.tabs.addTab(self.lists_tab, "목록")
        self.tabs.addTab(self.text_tab, "텍스트 서식")
        
        self.layout.addWidget(self.tabs)
        
        # 저장/취소 버튼
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("저장")
        self.cancel_btn = QPushButton("취소")
        
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.cancel_btn)
        
        self.layout.addLayout(self.button_layout)
        
        # 이벤트 연결
        self.save_btn.clicked.connect(self.save_template)
        self.cancel_btn.clicked.connect(self.reject)
    
    def create_headings_tab(self):
        """제목 탭 생성"""
        self.headings_layout = QVBoxLayout(self.headings_tab)
        
        # 제목 1 (H1) 그룹
        self.h1_group = QGroupBox("제목 1 (# )")
        h1_layout = QFormLayout(self.h1_group)
        
        h1_tmpl = self.template_data.get("heading1", {})
        self.h1_prefix = QLineEdit(h1_tmpl.get("prefix", "# "))
        
        self.h1_font = QFontComboBox()
        self.h1_font.setCurrentFont(QFont(h1_tmpl.get("font", "맑은 고딕")))
        
        self.h1_size = QSpinBox()
        self.h1_size.setRange(8, 72)  # pt 단위 (8~72)
        self.h1_size.setValue(h1_tmpl.get("size", 20))
        
        self.h1_color_btn = ColorButton(h1_tmpl.get("color", "#000000"))
        
        # 스타일 체크박스
        self.h1_bold = QCheckBox("굵게")
        self.h1_bold.setChecked(h1_tmpl.get("bold", True))
        self.h1_italic = QCheckBox("기울임")
        self.h1_italic.setChecked(h1_tmpl.get("italic", False))
        self.h1_underline = QCheckBox("밑줄")
        self.h1_underline.setChecked(h1_tmpl.get("underline", False))
        
        # 폼에 추가
        h1_layout.addRow("기호:", self.h1_prefix)
        h1_layout.addRow("글꼴:", self.h1_font)
        h1_layout.addRow("크기:", self.h1_size)
        h1_layout.addRow("색상:", self.h1_color_btn)
        
        # 스타일 설정을 가로로 배치
        style_layout = QHBoxLayout()
        style_layout.addWidget(self.h1_bold)
        style_layout.addWidget(self.h1_italic)
        style_layout.addWidget(self.h1_underline)
        h1_layout.addRow("스타일:", style_layout)
        
        # 제목 2 (H2) 그룹
        self.h2_group = QGroupBox("제목 2 (## )")
        h2_layout = QFormLayout(self.h2_group)
        
        h2_tmpl = self.template_data.get("heading2", {})
        self.h2_prefix = QLineEdit(h2_tmpl.get("prefix", "## "))
        
        self.h2_font = QFontComboBox()
        self.h2_font.setCurrentFont(QFont(h2_tmpl.get("font", "맑은 고딕")))
        
        self.h2_size = QSpinBox()
        self.h2_size.setRange(8, 72)
        self.h2_size.setValue(h2_tmpl.get("size", 16))
        
        self.h2_color_btn = ColorButton(h2_tmpl.get("color", "#000000"))
        
        # 스타일 체크박스
        self.h2_bold = QCheckBox("굵게")
        self.h2_bold.setChecked(h2_tmpl.get("bold", True))
        self.h2_italic = QCheckBox("기울임")
        self.h2_italic.setChecked(h2_tmpl.get("italic", False))
        self.h2_underline = QCheckBox("밑줄")
        self.h2_underline.setChecked(h2_tmpl.get("underline", False))
        
        # 템플릿 유형
        self.h2_template_type = QComboBox()
        self.h2_template_type.addItems(["normal", "table"])
        self.h2_template_type.setCurrentText(h2_tmpl.get("template_type", "normal"))
        
        # 폼에 추가
        h2_layout.addRow("기호:", self.h2_prefix)
        h2_layout.addRow("글꼴:", self.h2_font)
        h2_layout.addRow("크기:", self.h2_size)
        h2_layout.addRow("색상:", self.h2_color_btn)
        
        # 스타일 설정을 가로로 배치
        style_layout = QHBoxLayout()
        style_layout.addWidget(self.h2_bold)
        style_layout.addWidget(self.h2_italic)
        style_layout.addWidget(self.h2_underline)
        h2_layout.addRow("스타일:", style_layout)
        
        # 제목 3 (H3) 그룹
        self.h3_group = QGroupBox("제목 3 (### )")
        h3_layout = QFormLayout(self.h3_group)
        
        h3_tmpl = self.template_data.get("heading3", {})
        self.h3_prefix = QLineEdit(h3_tmpl.get("prefix", "### "))
        
        self.h3_font = QFontComboBox()
        self.h3_font.setCurrentFont(QFont(h3_tmpl.get("font", "맑은 고딕")))
        
        self.h3_size = QSpinBox()
        self.h3_size.setRange(8, 72)
        self.h3_size.setValue(h3_tmpl.get("size", 14))
        
        self.h3_color_btn = ColorButton(h3_tmpl.get("color", "#000000"))
        
        # 스타일 체크박스
        self.h3_bold = QCheckBox("굵게")
        self.h3_bold.setChecked(h3_tmpl.get("bold", True))
        self.h3_italic = QCheckBox("기울임")
        self.h3_italic.setChecked(h3_tmpl.get("italic", False))
        self.h3_underline = QCheckBox("밑줄")
        self.h3_underline.setChecked(h3_tmpl.get("underline", False))
        
        # 폼에 추가
        h3_layout.addRow("기호:", self.h3_prefix)
        h3_layout.addRow("글꼴:", self.h3_font)
        h3_layout.addRow("크기:", self.h3_size)
        h3_layout.addRow("색상:", self.h3_color_btn)
        
        # 스타일 설정을 가로로 배치
        style_layout = QHBoxLayout()
        style_layout.addWidget(self.h3_bold)
        style_layout.addWidget(self.h3_italic)
        style_layout.addWidget(self.h3_underline)
        h3_layout.addRow("스타일:", style_layout)
        
        # 레이아웃에 추가
        self.headings_layout.addWidget(self.h1_group)
        self.headings_layout.addWidget(self.h2_group)
        self.headings_layout.addWidget(self.h3_group)
    
    def create_lists_tab(self):
        """목록 탭 생성"""
        self.lists_layout = QVBoxLayout(self.lists_tab)
        
        # 글머리 기호 목록 그룹
        self.bullet_group = QGroupBox("글머리 기호 목록")
        bullet_layout = QFormLayout(self.bullet_group)
        
        bullet_tmpl = self.template_data.get("bullet_list", {})
        self.bullet_symbol = QLineEdit(bullet_tmpl.get("symbol", "• "))
        
        self.bullet_font = QFontComboBox()
        self.bullet_font.setCurrentFont(QFont(bullet_tmpl.get("font", "맑은 고딕")))
        
        self.bullet_size = QSpinBox()
        self.bullet_size.setRange(8, 72)
        self.bullet_size.setValue(bullet_tmpl.get("size", 10))
        
        self.bullet_color_btn = ColorButton(bullet_tmpl.get("color", "#000000"))
        
        # 스타일 체크박스
        self.bullet_bold = QCheckBox("굵게")
        self.bullet_bold.setChecked(bullet_tmpl.get("bold", False))
        self.bullet_italic = QCheckBox("기울임")
        self.bullet_italic.setChecked(bullet_tmpl.get("italic", False))
        
        bullet_layout.addRow("기호:", self.bullet_symbol)
        bullet_layout.addRow("글꼴:", self.bullet_font)
        bullet_layout.addRow("크기:", self.bullet_size)
        bullet_layout.addRow("색상:", self.bullet_color_btn)
        
        # 스타일 설정을 가로로 배치
        style_layout = QHBoxLayout()
        style_layout.addWidget(self.bullet_bold)
        style_layout.addWidget(self.bullet_italic)
        bullet_layout.addRow("스타일:", style_layout)
        
        # 번호 매기기 목록 그룹
        self.ordered_group = QGroupBox("번호 매기기 목록")
        ordered_layout = QFormLayout(self.ordered_group)
        
        ordered_tmpl = self.template_data.get("ordered_list", {})
        self.ordered_format = QLineEdit(ordered_tmpl.get("format", "%d. "))
        
        self.ordered_font = QFontComboBox()
        self.ordered_font.setCurrentFont(QFont(ordered_tmpl.get("font", "맑은 고딕")))
        
        self.ordered_size = QSpinBox()
        self.ordered_size.setRange(8, 72)
        self.ordered_size.setValue(ordered_tmpl.get("size", 10))
        
        self.ordered_color_btn = ColorButton(ordered_tmpl.get("color", "#000000"))
        
        # 스타일 체크박스
        self.ordered_bold = QCheckBox("굵게")
        self.ordered_bold.setChecked(ordered_tmpl.get("bold", False))
        self.ordered_italic = QCheckBox("기울임")
        self.ordered_italic.setChecked(ordered_tmpl.get("italic", False))
        
        ordered_layout.addRow("형식:", self.ordered_format)
        ordered_layout.addRow("글꼴:", self.ordered_font)
        ordered_layout.addRow("크기:", self.ordered_size)
        ordered_layout.addRow("색상:", self.ordered_color_btn)
        
        # 스타일 설정을 가로로 배치
        style_layout = QHBoxLayout()
        style_layout.addWidget(self.ordered_bold)
        style_layout.addWidget(self.ordered_italic)
        ordered_layout.addRow("스타일:", style_layout)
        
        # 레이아웃에 추가
        self.lists_layout.addWidget(self.bullet_group)
        self.lists_layout.addWidget(self.ordered_group)
    
    def create_text_tab(self):
        """텍스트 서식 탭 생성"""
        self.text_layout = QVBoxLayout(self.text_tab)
        
        # 일반 텍스트 그룹
        self.text_group = QGroupBox("일반 텍스트 (기본 서식)")
        text_layout = QFormLayout(self.text_group)
        
        text_tmpl = self.template_data.get("paragraph", {})
        
        self.text_font = QFontComboBox()
        self.text_font.setCurrentFont(QFont(text_tmpl.get("font", "맑은 고딕")))
        
        self.text_size = QSpinBox()
        self.text_size.setRange(8, 72)
        self.text_size.setValue(text_tmpl.get("size", 10))
        
        self.text_color_btn = ColorButton(text_tmpl.get("color", "#000000"))
        
        text_layout.addRow("글꼴:", self.text_font)
        text_layout.addRow("크기:", self.text_size)
        text_layout.addRow("색상:", self.text_color_btn)
        
        # 일반 텍스트 설정이 변경될 때 굵기/기울임 문법에 자동 적용
        self.text_font.currentFontChanged.connect(lambda font: self.update_bold_italic_font(font))
        self.text_size.valueChanged.connect(lambda size: self.update_bold_italic_size(size))
        self.text_color_btn.clicked.connect(self.update_bold_italic_color)
        
        # 굵기 그룹
        self.bold_group = QGroupBox("굵게")
        bold_layout = QFormLayout(self.bold_group)
        
        bold_tmpl = self.template_data.get("bold", {})
        self.bold_prefix = QLineEdit(bold_tmpl.get("prefix", "**"))
        self.bold_suffix = QLineEdit(bold_tmpl.get("suffix", "**"))
        
        self.bold_font = QFontComboBox()
        self.bold_font.setCurrentFont(QFont(bold_tmpl.get("font", text_tmpl.get("font", "맑은 고딕"))))
        
        self.bold_size = QSpinBox()
        self.bold_size.setRange(8, 72)
        self.bold_size.setValue(bold_tmpl.get("size", text_tmpl.get("size", 10)))
        
        self.bold_color_btn = ColorButton(bold_tmpl.get("color", text_tmpl.get("color", "#000000")))
        
        # 기울임 그룹
        self.italic_group = QGroupBox("기울임")
        italic_layout = QFormLayout(self.italic_group)
        
        italic_tmpl = self.template_data.get("italic", {})
        self.italic_prefix = QLineEdit(italic_tmpl.get("prefix", "_"))
        self.italic_suffix = QLineEdit(italic_tmpl.get("suffix", "_"))
        
        self.italic_font = QFontComboBox()
        self.italic_font.setCurrentFont(QFont(italic_tmpl.get("font", text_tmpl.get("font", "맑은 고딕"))))
        
        self.italic_size = QSpinBox()
        self.italic_size.setRange(8, 72)
        self.italic_size.setValue(italic_tmpl.get("size", text_tmpl.get("size", 10)))
        
        self.italic_color_btn = ColorButton(italic_tmpl.get("color", text_tmpl.get("color", "#000000")))
        
        # 레이아웃에 추가
        self.text_layout.addWidget(self.text_group)
        
        # 링크 그룹
        self.link_group = QGroupBox("링크")
        link_layout = QFormLayout(self.link_group)
        
        link_tmpl = self.template_data.get("link", {})
        self.link_prefix = QLineEdit(link_tmpl.get("prefix", "["))
        self.link_middle = QLineEdit(link_tmpl.get("middle", "]("))
        self.link_suffix = QLineEdit(link_tmpl.get("suffix", ")"))
        
        self.link_font = QFontComboBox()
        self.link_font.setCurrentFont(QFont(link_tmpl.get("font", "맑은 고딕")))
        
        self.link_size = QSpinBox()
        self.link_size.setRange(8, 72)
        self.link_size.setValue(link_tmpl.get("size", 10))
        
        self.link_color_btn = ColorButton(link_tmpl.get("color", "#0000FF"))
        
        self.link_underline = QCheckBox("밑줄")
        self.link_underline.setChecked(link_tmpl.get("underline", True))
        
        link_layout.addRow("시작 기호:", self.link_prefix)
        link_layout.addRow("중간 기호:", self.link_middle)
        link_layout.addRow("종료 기호:", self.link_suffix)
        link_layout.addRow("글꼴:", self.link_font)
        link_layout.addRow("크기:", self.link_size)
        link_layout.addRow("색상:", self.link_color_btn)
        link_layout.addRow("", self.link_underline)
        
        # 레이아웃에 추가
        self.text_layout.addWidget(self.link_group)
    
    def update_bold_italic_font(self, font):
        """일반 텍스트의 글꼴이 변경될 때 굵기/기울임 문법의 글꼴도 업데이트"""
        self.bold_font.setCurrentFont(font)
        self.italic_font.setCurrentFont(font)
    
    def update_bold_italic_size(self, size):
        """일반 텍스트의 크기가 변경될 때 굵기/기울임 문법의 크기도 업데이트"""
        self.bold_size.setValue(size)
        self.italic_size.setValue(size)
    
    def update_bold_italic_color(self):
        """일반 텍스트의 색상이 변경될 때 굵기/기울임 문법의 색상도 업데이트"""
        self.bold_color_btn.setColor(self.text_color_btn.color)
        self.italic_color_btn.setColor(self.text_color_btn.color)
    
    def create_table_tab(self):
        """표 탭 생성"""
        self.table_layout = QVBoxLayout(self.table_tab)
        
        # 표 스타일 그룹
        self.table_group = QGroupBox("표 스타일")
        table_layout = QFormLayout(self.table_group)
        
        table_tmpl = self.template_data.get("table", {})
        self.table_header_border = QLineEdit(table_tmpl.get("header_border", "3"))
        self.table_middle_border = QLineEdit(table_tmpl.get("middle_border", "6"))
        self.table_last_border = QLineEdit(table_tmpl.get("last_border", "4"))
        
        table_layout.addRow("헤더 행 테두리 ID:", self.table_header_border)
        table_layout.addRow("중간 행 테두리 ID:", self.table_middle_border)
        table_layout.addRow("마지막 행 테두리 ID:", self.table_last_border)
        
        # 레이아웃에 추가
        self.table_layout.addWidget(self.table_group)
    
    def save_template(self):
        """템플릿 저장"""
        # 헤딩 설정
        self.template_data["heading1"] = {
            "prefix": self.h1_prefix.text(),
            "font": self.h1_font.currentFont().family(),
            "size": self.h1_size.value(),
            "color": self.h1_color_btn.color,
            "bold": self.h1_bold.isChecked(),
            "italic": self.h1_italic.isChecked(),
            "underline": self.h1_underline.isChecked(),
            "paraShape": "0",
            "template_type": "normal",
            "charShape": "1"
        }
        
        self.template_data["heading2"] = {
            "prefix": self.h2_prefix.text(),
            "font": self.h2_font.currentFont().family(),
            "size": self.h2_size.value(),
            "color": self.h2_color_btn.color,
            "bold": self.h2_bold.isChecked(),
            "italic": self.h2_italic.isChecked(),
            "underline": self.h2_underline.isChecked(),
            "paraShape": "0",
            "template_type": self.h2_template_type.currentText(),
            "charShape": "2"
        }
        
        self.template_data["heading3"] = {
            "prefix": self.h3_prefix.text(),
            "font": self.h3_font.currentFont().family(),
            "size": self.h3_size.value(),
            "color": self.h3_color_btn.color,
            "bold": self.h3_bold.isChecked(),
            "italic": self.h3_italic.isChecked(),
            "underline": self.h3_underline.isChecked(),
            "paraShape": "0",
            "template_type": "normal",
            "charShape": "3"
        }
        
        # 목록 설정
        self.template_data["bullet_list"] = {
            "symbol": self.bullet_symbol.text(),
            "font": self.bullet_font.currentFont().family(),
            "size": self.bullet_size.value(),
            "color": self.bullet_color_btn.color,
            "bold": self.bullet_bold.isChecked(),
            "italic": self.bullet_italic.isChecked(),
            "paraShape": "1",
            "charShape": "0"
        }
        
        self.template_data["ordered_list"] = {
            "format": self.ordered_format.text(),
            "font": self.ordered_font.currentFont().family(),
            "size": self.ordered_size.value(),
            "color": self.ordered_color_btn.color,
            "bold": self.ordered_bold.isChecked(),
            "italic": self.ordered_italic.isChecked(),
            "paraShape": "1",
            "charShape": "0"
        }
        
        # 일반 텍스트 설정
        self.template_data["paragraph"] = {
            "font": self.text_font.currentFont().family(),
            "size": self.text_size.value(),
            "color": self.text_color_btn.color,
            "bold": False,
            "italic": False,
            "underline": False,
            "paraShape": "0",
            "charShape": "0"
        }
        
        # 텍스트 서식 설정
        self.template_data["bold"] = {
            "prefix": self.bold_prefix.text(),
            "suffix": self.bold_suffix.text(),
            "font": self.bold_font.currentFont().family(),
            "size": self.bold_size.value(),
            "color": self.bold_color_btn.color,
            "bold": True,
            "italic": False,
            "underline": False,
            "charShape": "6"
        }
        
        self.template_data["italic"] = {
            "prefix": self.italic_prefix.text(),
            "suffix": self.italic_suffix.text(),
            "font": self.italic_font.currentFont().family(),
            "size": self.italic_size.value(),
            "color": self.italic_color_btn.color,
            "bold": False,
            "italic": True,
            "underline": False,
            "charShape": "7"
        }
        
        self.template_data["link"] = {
            "prefix": self.link_prefix.text(),
            "middle": self.link_middle.text(),
            "suffix": self.link_suffix.text(),
            "font": self.link_font.currentFont().family(),
            "size": self.link_size.value(),
            "color": self.link_color_btn.color,
            "bold": False,
            "italic": False,
            "underline": self.link_underline.isChecked(),
            "charShape": "8"
        }
        
        # 표 설정
        self.template_data["table"] = {
            "header_border": self.table_header_border.text(),
            "middle_border": self.table_middle_border.text(),
            "last_border": self.table_last_border.text()
        }
        
        # 템플릿 관리자에 저장
        self.template_manager.save_template(self.template_name, self.template_data)
        
        # 대화상자 닫기
        self.accept()

class ConverterGUI(QMainWindow):
    """마크다운 변환기 GUI 클래스"""
    
    def __init__(self):
        super().__init__()
        
        # 템플릿 관리자 및 변환기 초기화
        self.template_manager = MarkdownTemplate()
        self.converter = HWPMLConverter(self.template_manager)
        
        # UI 설정
        self.setWindowTitle("마크다운 → HWP 변환기")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        # 템플릿 선택 영역
        self.template_layout = QHBoxLayout()
        
        self.template_label = QLabel("템플릿:")
        self.template_combo = QComboBox()
        self.update_template_combo()
        
        self.template_edit_btn = QPushButton("템플릿 편집")
        self.template_delete_btn = QPushButton("템플릿 삭제")

        self.template_new_btn = QPushButton("새 템플릿")
        
        self.template_layout.addWidget(self.template_label)
        self.template_layout.addWidget(self.template_combo)
        self.template_layout.addWidget(self.template_edit_btn)
        self.template_layout.addWidget(self.template_delete_btn)
        self.template_layout.addWidget(self.template_new_btn)
        
        self.layout.addLayout(self.template_layout)
        
        # 텍스트 편집기
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("여기에 마크다운 텍스트를 붙여넣거나 클립보드에서 가져오세요")
        self.layout.addWidget(self.text_edit)
        
        # 버튼 영역
        self.button_layout = QHBoxLayout()
        
        self.clipboard_button = QPushButton("클립보드에서 가져오기")
        self.path_button = QPushButton("저장 경로 선택")
        self.convert_button = QPushButton("변환")
        
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.path_button)
        self.button_layout.addWidget(self.convert_button)
        
        self.layout.addLayout(self.button_layout)
        
        # 상태 표시줄
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")
        
        # 이벤트 연결
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.path_button.clicked.connect(self.select_save_path)
        self.convert_button.clicked.connect(self.convert_md_to_hwp)
        self.template_combo.currentTextChanged.connect(self.change_template)
        self.template_edit_btn.clicked.connect(self.edit_template)
        self.template_new_btn.clicked.connect(self.create_new_template)
        self.template_delete_btn.clicked.connect(self.delete_template)
        
        # 저장 경로 초기화
        self.save_path = ""
    
    def delete_template(self):
        """현재 선택된 템플릿 삭제"""
        template_name = self.template_combo.currentText()
        if template_name == "default":
            self.status_bar.showMessage("기본 템플릿은 삭제할 수 없습니다")
            return

        # Confirm deletion
        from PySide6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self, 
            "템플릿 삭제", 
            f"템플릿 '{template_name}'을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success = self.template_manager.delete_template(template_name)
            if success:
                self.update_template_combo()
                self.status_bar.showMessage(f"템플릿 '{template_name}' 삭제됨")
            else:
                self.status_bar.showMessage("템플릿 삭제 실패")

    def update_template_combo(self):
        """템플릿 콤보박스 갱신"""
        self.template_combo.clear()
        for template_name in self.template_manager.templates.keys():
            self.template_combo.addItem(template_name)
        
        if self.template_manager.current_template:
            index = self.template_combo.findText(self.template_manager.current_template)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)
    
    def change_template(self, template_name):
        """템플릿 변경"""
        if template_name:
            self.template_manager.load_template(template_name)
    
    def edit_template(self):
        """현재 템플릿 편집"""
        template_name = self.template_combo.currentText()
        if template_name:
            dialog = TemplateEditDialog(self.template_manager, template_name, self)
            if dialog.exec():
                self.status_bar.showMessage(f"템플릿 '{template_name}' 저장됨")
    
    def create_new_template(self):
        """새 템플릿 생성"""
        template_name, ok = QFileDialog.getSaveFileName(self, "새 템플릿 이름", "", "템플릿 (*.json)")
        if ok and template_name:
            # 파일 이름에서 확장자 제거
            template_name = os.path.splitext(os.path.basename(template_name))[0]
            
            # 기본 템플릿 복사
            new_template = self.template_manager.templates["default"].copy()
            self.template_manager.save_template(template_name, new_template)
            
            # 콤보박스 갱신
            self.update_template_combo()
            
            # 새 템플릿 선택
            index = self.template_combo.findText(template_name)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)
            
            # 템플릿 편집 대화상자 표시
            self.edit_template()
    
    def load_from_clipboard(self):
        """클립보드에서 텍스트 가져오기"""
        clipboard = QApplication.clipboard()
        md_text = clipboard.text()
        
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_bar.showMessage("클립보드에서 텍스트를 가져왔습니다")
        else:
            self.status_bar.showMessage("클립보드에 텍스트가 없습니다")
    
    def select_save_path(self):
        """저장 경로 선택"""
        file_name, _ = QFileDialog.getSaveFileName(self, "HWP 파일 저장", "", "HWP Files (*.hml)")
        
        if file_name:
            self.save_path = file_name
            self.status_bar.showMessage(f"저장 경로: {self.save_path}")
        else:
            self.status_bar.showMessage("저장 경로가 선택되지 않았습니다")
    
    def convert_md_to_hwp(self):
        """마크다운을 HWP로 변환"""
        if not self.save_path:
            self.status_bar.showMessage("오류: 저장 경로를 먼저 선택하세요")
            return
        
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_bar.showMessage("오류: 변환할 텍스트가 없습니다")
            return
        
        self.status_bar.showMessage("변환 중...")
        
        try:
            # 메타데이터 추출
            t = re.search(r"(?<=title: ).*", md_text)
            a = re.search(r"(?<=author: ).*", md_text)
            d = re.search(r"(?<=date: ).*", md_text)
            
            title = t.group(0) if t else "제목 없음"
            author = a.group(0) if a else "작성자 없음"
            date = d.group(0) if d else "날짜 없음"
            
            # 변환 실행
            hwpml = self.converter.convert_markdown_to_hwpml(md_text, title, author, date)
            
            # 파일로 저장
            self.converter.save_to_file(hwpml, self.save_path)
            
            self.status_bar.showMessage(f"변환 완료: {self.save_path}")
        except Exception as e:
            self.status_bar.showMessage(f"오류: {str(e)}")