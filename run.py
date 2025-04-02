#!/usr/bin/env python
"""
마크다운-HWP 변환기 실행 스크립트
"""
import os
import sys
import threading
import keyboard
import pystray
from PIL import Image
from PySide6.QtWidgets import QApplication
from md2hwp.main import MD2HWPConverter
from md2hwp.gui.main_window import MainWindow
from md2hwp.config import APP_NAME

# 전역 변수
app = None
window = None
converter = None
window_visible = False
hotkey = "ctrl+alt+h"  # 기본 단축키 설정

def toggle_window():
    """창 표시/숨김 토글 함수"""
    global window, window_visible
    if window:
        if window_visible:
            window.hide()
        else:
            window.show()
            window.activateWindow()  # 창을 전면으로 가져옴
            window.raise_()
        window_visible = not window_visible

def setup_hotkey():
    """단축키 설정"""
    keyboard.add_hotkey(hotkey, toggle_window)

def create_image():
    """시스템 트레이 아이콘 이미지 생성"""
    # 간단한 이미지 생성 (실제 프로젝트에서는 아이콘 파일을 사용하는 것이 좋음)
    image = Image.new('RGB', (64, 64), color = (73, 109, 137))
    return image

def setup_tray():
    """시스템 트레이 아이콘 설정"""
    icon = pystray.Icon(APP_NAME)
    icon.icon = create_image()
    icon.title = APP_NAME
    
    def on_quit(icon, item):
        icon.stop()
        app.quit()
    
    def on_show(icon, item):
        toggle_window()
    
    # 트레이 메뉴 설정
    icon.menu = pystray.Menu(
        pystray.MenuItem('창 열기/닫기', on_show),
        pystray.MenuItem('종료', on_quit)
    )
    
    # 아이콘 클릭 시 창 표시/숨김 토글
    icon.on_click = lambda icon: toggle_window()
    
    # 트레이 아이콘 실행
    icon.run_detached()

def main():
    """애플리케이션 시작 함수"""
    global app, window, converter, window_visible
    
    # QApplication 생성
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # 변환기 및 메인 창 생성
    converter = MD2HWPConverter()
    window = MainWindow(converter)
    
    # 창 닫기 이벤트를 숨기기로 변경
    window.closeEvent = lambda event: (event.ignore(), toggle_window())
    
    # 단축키 설정
    setup_hotkey()
    
    # 시스템 트레이 아이콘 설정
    setup_tray()
    
    # 처음에는 창을 표시
    window.show()
    window_visible = True
    
    # QApplication 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 