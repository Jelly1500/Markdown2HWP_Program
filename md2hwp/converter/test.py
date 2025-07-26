# test.py (또는 원하는 이름으로 변경 가능, 예: mapping_window.py)
import sys
import os
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QSizePolicy, QSpacerItem, QMessageBox, QInputDialog
)
from PySide6.QtGui import QPixmap, QDrag, QPainter, QIcon, QFont, QColor
from PySide6.QtCore import Qt, QMimeData, QPoint, Signal

# --- 위젯 클래스들 (DraggableImage, ImageSourcePanel, DropTableWidget, MappedItemWidget) ---
# 이 클래스들은 이전 코드와 동일하므로 그대로 사용합니다. (코드는 하단에 전체 포함)

# ... (DraggableImage 등 4개 클래스 코드는 여기에 위치) ...
# --- 1. 드래그 가능한 이미지 위젯 ---
class DraggableImage(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        pixmap = QPixmap(image_path)
        self.setPixmap(pixmap.scaled(700, 300, 
                              Qt.AspectRatioMode.KeepAspectRatio, 
                              Qt.TransformationMode.SmoothTransformation))
        self.setToolTip(f"이미지 경로:\n{image_path}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            mime_data.setText(self.image_path)
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            
            preview_pixmap = QPixmap(self.pixmap().size())
            preview_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(preview_pixmap)
            painter.setOpacity(0.7)
            painter.drawPixmap(0, 0, self.pixmap())
            painter.end()
            drag.setPixmap(preview_pixmap)
            drag.setHotSpot(event.position().toPoint())
            drag.exec(Qt.DropAction.MoveAction)


# --- 2. 이미지를 담을 스크롤 패널 ---
class ImageSourcePanel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(10)
        self.setWidget(self.container)
        self.image_widgets = {}

    def load_images_and_map_ptags(self, folder_path, p_tag_list):
        for widget in self.image_widgets.values():
            widget.deleteLater()
        self.image_widgets.clear()
        
        if not os.path.isdir(folder_path):
            print(f"오류: 폴더를 찾을 수 없습니다 - {folder_path}")
            return {}
            
        image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
        
        if len(image_files) != len(p_tag_list):
            print(f"경고: 이미지 개수({len(image_files)})와 P태그 개수({len(p_tag_list)})가 일치하지 않습니다.")
        
        temp_map = {}
        for image_file, p_tag in zip(image_files, p_tag_list):
            image_path = os.path.join(folder_path, image_file)
            draggable_image = DraggableImage(image_path)
            self.layout.addWidget(draggable_image)
            self.image_widgets[image_path] = draggable_image
            temp_map[image_path] = p_tag
        return temp_map
            
    def hide_image(self, image_path):
        if image_path in self.image_widgets: self.image_widgets[image_path].hide()

    def show_image(self, image_path):
        if image_path in self.image_widgets: self.image_widgets[image_path].show()


# --- 3. 드롭을 받을 테이블 위젯 ---
class DropTableWidget(QTableWidget):
    image_dropped = Signal(str, int)
    def __init__(self, rows, cols, parent=None):
        super().__init__(rows, cols, parent)
        self.setAcceptDrops(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        drop_pos = event.position().toPoint()
        row = self.indexAt(drop_pos).row()
        col = self.indexAt(drop_pos).column()
        if row != -1 and col == 1:
            image_path = event.mimeData().text()
            self.image_dropped.emit(image_path, row)
            event.acceptProposedAction()
        else:
            event.ignore()

# --- 4. 드롭된 이미지와 X버튼을 담을 위젯 ---
class MappedItemWidget(QWidget):
    revert_clicked = Signal(str)
    def __init__(self, image_path, target_width, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        revert_button = QPushButton("X")
        revert_button.setFixedSize(25, 25)
        revert_button.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        revert_button.clicked.connect(lambda: self.revert_clicked.emit(self.image_path))
        layout.addWidget(image_label, 1)
        layout.addWidget(revert_button)


# --- 5. 메인 윈도우 -> MappingWindow로 클래스 이름 변경 및 로직 수정 ---
class MainWindow(QMainWindow):
    # [신규] 템플릿 생성이 완료되었음을 알리는 신호 정의
    # bool: 성공 여부, str: 결과 메시지
    template_creation_finished = Signal(bool, str)

    def __init__(self, cropped_images_path, p_tag_list, source_hml_path, template_manager, parent=None):
        super().__init__(parent)
        
        # 외부에서 데이터 주입
        self.cropped_images_path = cropped_images_path
        self.p_tags_list = p_tag_list
        self.source_hml_path = source_hml_path
        self.template_manager = template_manager

        # 데이터 관리
        self.image_to_p_tag_map = {}
        self.mapping_data = {} 
        self._template_created = False  # <- 템플릿 정상 생성 여부 플래그

        self.setWindowTitle("문서 이미지 템플릿 매핑")
        self.setGeometry(150, 150, 1400, 900)
        self.setWindowModality(Qt.WindowModality.ApplicationModal) # 다른 창과 상호작용 불가
        
        font = QFont("Malgun Gothic", 10)
        QApplication.setFont(font)
        
        self.initUI()
        self.connect_signals()

    def initUI(self):
        # UI 구성 로직은 이전과 대부분 동일
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>MD 문법</b>"))
        self.drop_table = self._create_drop_table()
        left_layout.addWidget(self.drop_table)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>원본 문서 미리보기</b>"))
        self.source_panel = ImageSourcePanel()
        right_layout.addWidget(self.source_panel)

        bottom_layout = QHBoxLayout()
        bottom_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        cancel_button = QPushButton("취소")
        self.apply_button = QPushButton("적용")
        bottom_layout.addWidget(cancel_button)
        bottom_layout.addWidget(self.apply_button)
        
        cancel_button.clicked.connect(self.cancel_operation)

        right_main_layout = QVBoxLayout()
        right_main_layout.addLayout(right_layout)
        right_main_layout.addLayout(bottom_layout)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_main_layout, 1)

        # 생성자에서 받은 데이터로 이미지 로드 및 P태그 매핑
        self.image_to_p_tag_map = self.source_panel.load_images_and_map_ptags(self.cropped_images_path, self.p_tags_list)
    
    def cancel_operation(self):
        """Emits a cancellation signal and closes the window."""
        self.template_creation_finished.emit(False, "템플릿 생성이 사용자에 의해 취소되었습니다.")
        self._template_created = True  # 중복 emit 방지
        self.close()
    
    def connect_signals(self):
        self.drop_table.image_dropped.connect(self.handle_image_drop)
        # "적용" 버튼 클릭 시 최종 템플릿 생성 함수 연결
        self.apply_button.clicked.connect(self.apply_and_create_template)

    def _create_drop_table(self):
        # 테이블의 아이템 이름과 최종 JSON의 키가 될 숫자(문자열)를 분리하여 관리
        self.table_items = ["대제목", "중제목", "소제목", "세부제목1", "세부제목2", "세부제목3", "일반 텍스트", "리스트"]
        self.md_map = {
            "대제목": "1", "중제목": "2", "소제목": "3", "세부제목1": "4",
            "세부제목2": "5", "세부제목3": "6", "일반 텍스트": "7", "리스트": "8"
        }
        table = DropTableWidget(len(self.table_items), 2)
        table.setHorizontalHeaderLabels(["MD 문법", "보고서 문단 형식"])
        for row, text in enumerate(self.table_items):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, item)
            table.setRowHeight(row, 100)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        return table

    def handle_image_drop(self, image_path, row):
        if row in self.mapping_data:
            old_image_path = self.mapping_data[row]
            self.source_panel.show_image(old_image_path)
        target_width = self.drop_table.columnWidth(1) - 40 
        self.mapping_data[row] = image_path
        self.source_panel.hide_image(image_path)
        cell_widget = MappedItemWidget(image_path, target_width)
        cell_widget.revert_clicked.connect(self.handle_revert_click)
        self.drop_table.setCellWidget(row, 1, cell_widget)

    def handle_revert_click(self, image_path):
        row_to_revert = -1
        for row, path in self.mapping_data.items():
            if path == image_path: row_to_revert = row; break
        if row_to_revert != -1:
            self.drop_table.removeCellWidget(row_to_revert, 1)
            del self.mapping_data[row_to_revert]
            self.source_panel.show_image(image_path)

    def apply_and_create_template(self):
        """ '적용' 버튼 클릭 시 최종 매핑 정보로 템플릿을 생성합니다. """
        p_tag_mappings = {}
        for row, image_path in self.mapping_data.items():
            table_item_key = self.table_items[row]
            line_number_str = self.md_map.get(table_item_key)
            p_tag_value = self.image_to_p_tag_map.get(image_path)
            if line_number_str and p_tag_value:
                p_tag_mappings[line_number_str] = p_tag_value
        
        if not p_tag_mappings:
            QMessageBox.warning(self, "경고", "매핑된 데이터가 없습니다.")
            return

        template_name, ok = QInputDialog.getText(self, "새 템플릿 저장", "저장할 템플릿 파일 이름을 입력하세요:", text="나의 템플릿")
        if not ok or not template_name:
            # If user cancels the input dialog, treat it as a cancellation of the whole process.
            self.template_creation_finished.emit(False, "템플릿 이름 입력이 취소되었습니다.")
            self.close()
            return

        try:
            success, message = self.template_manager.create_template_from_source_advanced(
                source_path=self.source_hml_path,
                template_name=template_name,
                p_tag_mappings=p_tag_mappings
            )
            # ★★★ FIX: Emit the signal with the result ★★★
            self.template_creation_finished.emit(success, message)
            if success:
                self._template_created = True  # <- 정상 생성 시 True로 설정
                self.close() # Close window only on success

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_message = f"템플릿 생성 중 예외가 발생했습니다:\n{e}"
            # ★★★ FIX: Emit the signal on failure ★★★
            self.template_creation_finished.emit(False, error_message)

    def closeEvent(self, event):
        # 창이 닫힐 때(우측 상단 X 버튼 포함) 메인 윈도우가 다시 활성화되도록 시그널 emit
        if not self._template_created:
            self.template_creation_finished.emit(False, "템플릿 생성이 사용자에 의해 닫기 버튼으로 취소되었습니다.")
        super().closeEvent(event)

# test.py를 직접 실행했을 때의 동작 (테스트용)
if __name__ == '__main__':
    
    pass