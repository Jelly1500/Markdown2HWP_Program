from pyhwpx import Hwp
import os
import time
import re
from md2hwp.utils.logger import log_info, log_debug, log_error

# 성능 최적화: 불필요한 헬퍼 함수들 제거 (재시도 로직 간소화로 더 이상 불필요)


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


def convert_hwp_to_jpg(hwp, hwp_path: str, jpg_path: str, clear_doc: bool = False):
    """
    성능 최적화: 문서 닫기를 선택적으로 수행하여 속도 향상
    """
    try:
        # 1. HWP 파일 열기
        
        hwp.open(hwp_path, "HWPML2X")
        
        # JPG로 저장 (성능 최적화: 경로 처리 간소화)
        saved = hwp.save_as(jpg_path, "JPG")
        if not saved:
            saved = hwp.save_as(jpg_path, "JPEG")
        
        if not saved:
            raise RuntimeError(f"JPG 저장 실패: {os.path.basename(jpg_path)}")
    except Exception as e:
        # 오류 발생 시 문서 강제 정리
        try:
            hwp.Clear(1)
        except:
            pass
        raise e
    finally:
        # 선택적 문서 정리 (메모리 관리용)
        if clear_doc:
            try:
                hwp.Clear(1)
            except:
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
        # 성능 최적화: 백그라운드에서 실행
        hwp = Hwp(visible=False)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            log_info(f"[JPG] 출력 디렉토리 생성: {output_dir}")

        hml_files = [f for f in os.listdir(hml_dir) if f.endswith('.hml')]
        if not hml_files:
            log_error(f"[JPG] '{hml_dir}' 폴더에 HML 파일이 없습니다.")
            return

        log_info(f"[JPG] 총 {len(hml_files)}개의 HML 파일을 변환합니다.")

        # 성능 최적화: 배치 처리 + 경로 처리 간소화
        batch_size = 50  # 50개마다 메모리 정리
        for i, hml_file in enumerate(hml_files):
            hml_path = os.path.join(hml_dir, hml_file)
            # 파일명 정규화 최적화: 간단한 처리만
            base = os.path.splitext(hml_file)[0]
            if any(c in base for c in '<>:"|?*\\'):
                safe_base = re.sub(r"[<>:\"|?*\\]+", "_", base) or "paragraph"
            else:
                safe_base = base
            jpg_path = os.path.join(output_dir, safe_base + '.jpg')

            # 배치 마지막이거나 오류 발생 시에만 문서 정리
            clear_doc = (i + 1) % batch_size == 0 or (i + 1) == len(hml_files)
            
            try:
                convert_hwp_to_jpg(hwp, hml_path, jpg_path, clear_doc)
            except Exception as e:
                log_error(f"[JPG] 변환 실패: {hml_file} → {e}")
                # 오류 발생 시 강제 정리
                try:
                    hwp.Clear(1)
                except:
                    pass
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

