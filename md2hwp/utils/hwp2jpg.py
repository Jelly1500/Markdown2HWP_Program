from pyhwpx import Hwp
import os
import time
import re
import datetime
from md2hwp.utils.logger import log_info, log_debug, log_error

def _safe_jpg_path(preferred_path: str) -> str:
    """파일명에 특수문자가 많을 때 안전한 JPG 경로를 생성."""
    out_dir = os.path.dirname(preferred_path)
    base = os.path.splitext(os.path.basename(preferred_path))[0]
    safe_base = re.sub(r"[^0-9A-Za-z._-]+", "_", base) or "image"
    candidate = os.path.join(out_dir, safe_base + ".jpg")
    if not os.path.exists(candidate):
        return candidate
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(out_dir, f"{safe_base}_{ts}.jpg")


def _temp_jpg_path() -> str:
    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "md2hwp")
    os.makedirs(temp_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(temp_dir, f"image_{ts}.jpg")


def _wait_ready(hwp, timeout_sec: float = 5.0):
    """한/글 상태가 '준비'가 될 때까지 대기 (최대 timeout)."""
    try:
        checks = int(timeout_sec / 0.1)
        while checks > 0:
            try:
                ki = hwp.KeyIndicator()
                if isinstance(ki, str) and ("준비" in ki or "Ready" in ki):
                    break
            except Exception:
                pass
            time.sleep(0.1)
            checks -= 1
    except Exception:
        pass


def convert_hwp_to_jpg(hwp, hwp_path: str, jpg_path: str):
    """
    [최종 개선] 파일을 열고 닫은 후, 각각의 작업이 완료될 때까지
    상태 표시줄을 확인하여 안정성을 확보합니다.
    """
    try:
        # 1. HWP 파일 열기
        
        log_info(f"[JPG] 문서 열기: {os.path.basename(hwp_path)} (HWPML2X)")
        hwp.open(hwp_path, "HWPML2X")
        _wait_ready(hwp, 3.0)
        
        # 3. PrintToImage 액션을 사용해 JPG로 저장
        # 1차: 요청된 경로
        abs_jpg_path = os.path.abspath(jpg_path)
        log_info(f"[JPG] 저장 시도: JPG → {abs_jpg_path}")
        saved = hwp.save_as(abs_jpg_path, "JPG")
        if not saved:
            # 2차: JPEG 필터명 시도
            log_info(f"[JPG] 저장 재시도: JPEG → {abs_jpg_path}")
            saved = hwp.save_as(abs_jpg_path, "JPEG")
        if not saved:
            # 3차: 안전한 파일명으로 재시도
            safe_path = _safe_jpg_path(abs_jpg_path)
            log_info(f"[JPG] 저장 재시도(안전이름): {safe_path}")
            saved = hwp.save_as(safe_path, "JPG") or hwp.save_as(safe_path, "JPEG")
            if saved:
                log_info(f"[JPG] 성공(안전이름): {os.path.basename(safe_path)}")
                return
        if not saved:
            # 4차: 임시 폴더 경로
            temp_path = _temp_jpg_path()
            log_info(f"[JPG] 저장 재시도(임시폴더): {temp_path}")
            saved = hwp.save_as(temp_path, "JPG") or hwp.save_as(temp_path, "JPEG")
            if saved:
                log_info(f"[JPG] 성공(임시폴더): {os.path.basename(temp_path)}")
                return
        if not saved:
            raise RuntimeError("JPG 저장 실패(JPG/JPEG, 안전이름/임시폴더 모두 실패)")
        log_info(f"[JPG] 성공: {os.path.basename(abs_jpg_path)}")
    finally:
        # 현재 문서 닫기 시도 (다음 파일 대비)
        try:
            hwp.Clear(1)
            _wait_ready(hwp, 2.0)
        except Exception:
            pass

    # finally:
    #     # 4. 현재 열려있는 문서를 닫고, 닫기 작업이 완료될 때까지 대기
    #     try:
    #         hwp.Clear(1)
            
    #         # --- ★★★ 핵심 수정 사항: 문서 닫기 후 상태 확인 ★★★ ---
    #         # 다음 파일을 열기 전에, 현재 문서 닫기 작업이 완전히 완료되고
    #         # 한/글이 다시 '준비' 상태가 될 때까지 기다립니다.
    #         close_timeout = 50 # 5초
    #         while close_timeout > 0:
    #             if "준비" in hwp.KeyIndicator():
    #                 break
    #             time.sleep(0.1)
    #             close_timeout -= 1
    #         # ----------------------------------------------------

    #     except Exception as cleare:
    #         print(f"문서 닫기 중 오류 발생: {cleare}")

def convert_all_hmls_to_jpg(hml_dir, output_dir):
    """
    한/글 객체를 한 번만 생성하고 재사용하여 모든 HML 파일을 JPG로 변환합니다.
    """
    hwp = None
    try:
        log_info("[JPG] 한/글 오토메이션 객체 생성 시작 (visible=True)")
        # 일부 환경에서 비가시 모드가 대화상자/보안 경고로 인해 멈추는 경우가 있어 가시 모드 사용
        hwp = Hwp(visible=True)
        log_info("[JPG] 객체 생성 완료")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            log_info(f"[JPG] 출력 디렉토리 생성: {output_dir}")

        hml_files = [f for f in os.listdir(hml_dir) if f.endswith('.hml')]
        if not hml_files:
            log_error(f"[JPG] '{hml_dir}' 폴더에 HML 파일이 없습니다.")
            return

        log_info(f"[JPG] 총 {len(hml_files)}개의 HML 파일을 변환합니다.")

        for hml_file in hml_files:
            hml_path = os.path.join(hml_dir, hml_file)
            base = os.path.splitext(hml_file)[0]
            safe_base = re.sub(r"[^0-9A-Za-z._-]+", "_", base) or "paragraph"
            jpg_file = safe_base + '.jpg'
            jpg_path = os.path.join(output_dir, jpg_file)

            log_info(f"[JPG] 변환 시작: {hml_file} -> {jpg_file}")
            try:
                convert_hwp_to_jpg(hwp, hml_path, jpg_path)
            except Exception as e:
                log_error(f"[JPG] 이 항목 변환 실패: {hml_file} → 이유: {e}")
                # 다음 항목 계속 처리
                continue

    except Exception as e:
        log_error(f"[JPG] 전체 변환 작업 중 심각한 오류 발생: {e}")

    finally:
        if hwp:
            try:
                hwp.quit()
                log_info("[JPG] 모든 작업 완료 후, 한/글 프로그램을 완전히 종료했습니다.")
            except Exception as e:
                log_error(f"[JPG] 한/글 프로그램 종료 중 오류 발생: {e}")


if __name__ == "__main__":
    hml_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\output_split_hml'
    output_jpg_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\images'
    
    convert_all_hmls_to_jpg(hml_dir, output_jpg_dir)

# --- 사용 예시 ---
# 실제 파일 경로로 바꿔서 사용하세요.
# 입력 HWP 파일 경로
#     input_hwp_file_path = r'C:\Users\USER\Downloads\한글-템플릿2.hwp'
# # 출력 JPG 파일 경로 (다중 페이지 시 파일명 뒤에 페이지 번호가 붙을 수 있습니다)
#     output_jpg_file_path = r'.\YourDocument_output.jpg'

#     convert_hwp_to_jpg(input_hwp_file_path, output_jpg_file_path)

