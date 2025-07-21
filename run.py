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
from PySide6.QtWidgets import QApplication, QMessageBox # GUI 및 메시지 박스

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD2HWP_DIR = os.path.join(SCRIPT_DIR, 'md2hwp')

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from md2hwp.main import MD2HWPConverter, perform_license_check
    from md2hwp.gui.main_window import MainWindow
    from md2hwp.config import APP_NAME
except ImportError as e:
    app_temp = QApplication.instance()
    if not app_temp: app_temp = QApplication(sys.argv) 
    QMessageBox.critical(None, "오류", f"프로그램 실행에 필요한 모듈을 찾을 수 없습니다.\n오류: {e}\n경로: {sys.path}\n프로그램을 종료합니다.")
    sys.exit(1)

app = None              # QApplication 인스턴스
window = None           # MainWindow 인스턴스
converter = None        # MD2HWPConverter 인스턴스
window_visible = False  # 창 표시 여부 상태
hotkey = "ctrl+alt+h"   # 창 토글 단축키
tray_icon = None        # pystray 아이콘 객체

def toggle_window():
    """창 표시/숨김 상태를 토글하는 함수"""
    global window, window_visible
    if window:
        if window_visible:
            window.hide()
        else:
            window.show()
            window.activateWindow() 
            window.raise_()       
        window_visible = not window_visible

def setup_hotkey():
    """전역 단축키를 설정하는 함수"""
    try:
        keyboard.add_hotkey(hotkey, toggle_window)
        print(f"단축키 '{hotkey}' 설정 완료.")
    except Exception as e:
        print(f"단축키 설정 오류: {e}")
        if QApplication.instance(): 
             QMessageBox.warning(None, "단축키 설정 경고",
                                f"단축키 '{hotkey}' 설정에 실패했습니다.\n"
                                f"오류: {e}\n\n"
                                "다른 프로그램에서 이미 사용 중이거나, \n"
                                "프로그램 실행 권한이 부족할 수 있습니다.\n"
                                "(필요시 관리자 권한으로 실행해 보세요)")
        else:
            print("경고: 단축키 설정 실패. 관리자 권한이 필요할 수 있습니다.")

def create_image():
    """시스템 트레이 아이콘 이미지를 생성하는 함수"""
    # 아이콘 파일 경로 (run.py와 같은 위치에 icon.png 파일이 있다고 가정)
    icon_path = os.path.join(SCRIPT_DIR, "icon.png")
    try:
        if os.path.exists(icon_path):
            print(f"아이콘 파일 로드: {icon_path}")
            return Image.open(icon_path)
        else:
            print("아이콘 파일(icon.png)을 찾을 수 없습니다. 기본 이미지를 생성합니다.")
            return Image.new('RGB', (64, 64), color = (73, 109, 137))
    except Exception as e:
        print(f"아이콘 로드 중 오류 발생: {e}. 기본 이미지를 생성합니다.")
        return Image.new('RGB', (64, 64), color = (73, 109, 137))

def setup_tray():
    """시스템 트레이 아이콘을 설정하고 실행하는 함수 (이전 버전 로직)"""
    global tray_icon, app 

    icon_image = create_image()
    tray_icon = pystray.Icon(APP_NAME, icon=icon_image, title=APP_NAME)

    def on_quit(icon, item):
        """트레이 메뉴 '종료' 클릭 시 호출될 함수"""
        print("트레이 메뉴: 종료 요청됨")
        global window_visible
        if window and window_visible:
            window.hide()
            window_visible = False
        

        
        # 트레이 아이콘 중지
        icon.stop()     
        
        # 파이썬 프로세스 완전히 종료
        if app:         
            app.quit() 


    def on_show(icon, item):
        """트레이 메뉴 '창 열기/닫기' 클릭 시 호출될 함수"""
        toggle_window()

    tray_icon.menu = pystray.Menu(
        pystray.MenuItem('창 열기/닫기', on_show, default=True), 
        pystray.MenuItem(pystray.Menu.SEPARATOR, None),      
        pystray.MenuItem('종료', on_quit)
    )

    tray_icon.on_click = lambda icon: toggle_window()


    tray_icon.run_detached()

def main():
    """애플리케이션 메인 실행 함수"""
    global app, window, converter, window_visible, tray_icon

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    perform_license_check() 

    converter = MD2HWPConverter()
    window = MainWindow(converter)

    def override_close_event(event):
        """창 닫기(X) 버튼 클릭 시 창을 숨기는 이벤트 핸들러"""
        toggle_window() 
        event.ignore() 
    window.closeEvent = override_close_event



    setup_hotkey()

    setup_tray()

    window.show()
    window_visible = True

    exit_code = app.exec()

    # 프로그램 종료 시 모든 리소스 확실히 해제
    if tray_icon and tray_icon.visible:
        tray_icon.stop()
    try:
        keyboard.unhook_all()
    except Exception as e:
        print(f"단축키 리소스 해제 중 오류: {e}")

    sys.exit(exit_code) 

if __name__ == "__main__":
    main()